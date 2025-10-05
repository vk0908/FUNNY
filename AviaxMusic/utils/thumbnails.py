import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from youtubesearchpython.__future__ import VideosSearch
from config import YOUTUBE_IMG_URL
from AviaxMusic.core.dir import CACHE_DIR


# === Design Settings === #
PANEL_W, PANEL_H = 780, 560
PANEL_X = (1280 - PANEL_W) // 2
PANEL_Y = 80
TRANSPARENCY = 160
INNER_OFFSET = 38
THUMB_W, THUMB_H = 560, 290
THUMB_X = PANEL_X + (PANEL_W - THUMB_W) // 2
THUMB_Y = PANEL_Y + INNER_OFFSET
TITLE_X, TITLE_Y = 380, THUMB_Y + THUMB_H + 15
META_X, META_Y = 380, TITLE_Y + 45
BAR_X, BAR_Y = 390, META_Y + 45
BAR_RED_LEN, BAR_TOTAL_LEN = 300, 500
ICONS_W, ICONS_H = 415, 45
ICONS_X = PANEL_X + (PANEL_W - ICONS_W) // 2
ICONS_Y = BAR_Y + 55
MAX_TITLE_WIDTH = 600


def trim_to_width(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> str:
    ellipsis = "…"
    if font.getlength(text) <= max_w:
        return text
    for i in range(len(text) - 1, 0, -1):
        if font.getlength(text[:i] + ellipsis) <= max_w:
            return text[:i] + ellipsis
    return ellipsis


async def gen_thumb(videoid: str) -> str:
    cache_path = os.path.join(CACHE_DIR, f"{videoid}_glow.png")
    if os.path.exists(cache_path):
        return cache_path

    # --- YouTube Data Fetch ---
    results = VideosSearch(f"https://www.youtube.com/watch?v={videoid}", limit=1)
    try:
        data = (await results.next())["result"][0]
        title = re.sub(r"\W+", " ", data.get("title", "Untitled")).title()
        thumbnail = data.get("thumbnails", [{}])[0].get("url", YOUTUBE_IMG_URL)
        duration = data.get("duration")
        views = data.get("viewCount", {}).get("short", "Unknown Views")
    except Exception:
        title, thumbnail, duration, views = "Unknown Title", YOUTUBE_IMG_URL, "Live", "0 Views"

    is_live = not duration or str(duration).lower() in {"", "live", "live now"}
    duration_text = "LIVE 🔴" if is_live else duration or "Unknown"

    # --- Download Thumbnail ---
    thumb_path = os.path.join(CACHE_DIR, f"thumb_{videoid}.png")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    async with aiofiles.open(thumb_path, "wb") as f:
                        await f.write(await resp.read())
    except Exception:
        return YOUTUBE_IMG_URL

    # --- Base Background ---
    base = Image.open(thumb_path).resize((1280, 720)).convert("RGBA")
    blurred = base.filter(ImageFilter.GaussianBlur(18))
    darkened = ImageEnhance.Brightness(blurred).enhance(0.5)

    # Soft Gradient Glow Overlay
    gradient = Image.new("RGBA", darkened.size, (0, 0, 0, 0))
    for y in range(720):
        alpha = int(120 * (1 - y / 720))
        ImageDraw.Draw(gradient).line([(0, y), (1280, y)], fill=(255, 105, 180, alpha))
    darkened = Image.alpha_composite(darkened, gradient)

    # Frosted Glass Panel
    panel_area = darkened.crop((PANEL_X, PANEL_Y, PANEL_X + PANEL_W, PANEL_Y + PANEL_H))
    overlay = Image.new("RGBA", (PANEL_W, PANEL_H), (255, 255, 255, TRANSPARENCY))
    frosted = Image.alpha_composite(panel_area, overlay)
    mask = Image.new("L", (PANEL_W, PANEL_H), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, PANEL_W, PANEL_H), 50, fill=255)
    darkened.paste(frosted, (PANEL_X, PANEL_Y), mask)

    # --- Fonts ---
    try:
        title_font = ImageFont.truetype("AviaxMusic/assets/font2.ttf", 34)
        regular_font = ImageFont.truetype("AviaxMusic/assets/font.ttf", 20)
    except OSError:
        title_font = regular_font = ImageFont.load_default()

    draw = ImageDraw.Draw(darkened)

    # --- Video Thumbnail ---
    thumb = base.resize((THUMB_W, THUMB_H))
    tmask = Image.new("L", thumb.size, 0)
    ImageDraw.Draw(tmask).rounded_rectangle((0, 0, THUMB_W, THUMB_H), 25, fill=255)
    darkened.paste(thumb, (THUMB_X, THUMB_Y), tmask)

    # --- Glow Title ---
    trimmed_title = trim_to_width(title, title_font, MAX_TITLE_WIDTH)
    for offset in [(2,2), (-2,-2), (2,-2), (-2,2)]:
        draw.text((TITLE_X+offset[0], TITLE_Y+offset[1]), trimmed_title, font=title_font, fill=(255,105,180))
    draw.text((TITLE_X, TITLE_Y), trimmed_title, font=title_font, fill="white")

    # --- Meta Info ---
    draw.text((META_X, META_Y), f"YouTube | {views}", fill="#F8BBD0", font=regular_font)

    # --- Glowing Progress Bar ---
    glow_layer = Image.new("RGBA", darkened.size, (0,0,0,0))
    gdraw = ImageDraw.Draw(glow_layer)
    gdraw.line([(BAR_X, BAR_Y), (BAR_X + BAR_RED_LEN, BAR_Y)], fill=(255,105,180,255), width=10)
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(8))
    darkened = Image.alpha_composite(darkened, glow_layer)

    draw.line([(BAR_X, BAR_Y), (BAR_X + BAR_RED_LEN, BAR_Y)], fill=(255,105,180), width=6)
    draw.line([(BAR_X + BAR_RED_LEN, BAR_Y), (BAR_X + BAR_TOTAL_LEN, BAR_Y)], fill=(180,180,180), width=5)

    draw.text((BAR_X, BAR_Y + 15), "00:00", fill="white", font=regular_font)
    draw.text((BAR_X + BAR_TOTAL_LEN - 70, BAR_Y + 15), duration_text, fill="#FF4081", font=regular_font)

    # --- Top Text (Glowing Signature) ---
    glow_text = Image.new("RGBA", darkened.size, (0,0,0,0))
    g = ImageDraw.Draw(glow_text)
    g.text((40, 25), "Dev: @LifeOfSimon", font=regular_font, fill=(255,255,255))
    g.text((1020, 25), "IG: @rubesh_official_18", font=regular_font, fill=(255,255,255))
    glow_text = glow_text.filter(ImageFilter.GaussianBlur(3))
    darkened = Image.alpha_composite(darkened, glow_text)
    draw.text((40, 25), "Dev: @LifeOfSimon", font=regular_font, fill="#FFC0CB")
    draw.text((1020, 25), "IG: @rubesh_official_18", font=regular_font, fill="#FFC0CB")

    # --- Cleanup ---
    try:
        os.remove(thumb_path)
    except OSError:
        pass

    darkened.save(cache_path)
    return cache_path
