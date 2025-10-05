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
TRANSPARENCY = 170
INNER_OFFSET = 38
THUMB_W, THUMB_H = 560, 290
THUMB_X = PANEL_X + (PANEL_W - THUMB_W) // 2
THUMB_Y = PANEL_Y + INNER_OFFSET
TITLE_X, TITLE_Y = 380, THUMB_Y + THUMB_H + 15
META_X, META_Y = 380, TITLE_Y + 50
BAR_X, BAR_Y = 390, META_Y + 45
BAR_RED_LEN, BAR_TOTAL_LEN = 300, 500
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

    # --- YouTube Data ---
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

    # --- Download Thumbnail (fast + async) ---
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
    dark_bg = base.filter(ImageFilter.GaussianBlur(12))
    dark_bg = ImageEnhance.Brightness(dark_bg).enhance(0.45)

    # Gradient Overlay (Pink-Black blend)
    grad = Image.new("RGBA", dark_bg.size)
    for y in range(720):
        alpha = int(150 * (1 - y / 720))
        ImageDraw.Draw(grad).line([(0, y), (1280, y)], fill=(255, 105, 180, alpha))
    dark_bg = Image.alpha_composite(dark_bg, grad)

    # Frosted Glass Panel
    panel_crop = dark_bg.crop((PANEL_X, PANEL_Y, PANEL_X + PANEL_W, PANEL_Y + PANEL_H))
    overlay = Image.new("RGBA", (PANEL_W, PANEL_H), (255, 255, 255, TRANSPARENCY))
    frosted = Image.alpha_composite(panel_crop, overlay)
    mask = Image.new("L", (PANEL_W, PANEL_H), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, PANEL_W, PANEL_H), 50, fill=255)
    dark_bg.paste(frosted, (PANEL_X, PANEL_Y), mask)

    # --- Fonts ---
    try:
        title_font = ImageFont.truetype("AviaxMusic/assets/font2.ttf", 34)
        regular_font = ImageFont.truetype("AviaxMusic/assets/font.ttf", 20)
    except OSError:
        title_font = regular_font = ImageFont.load_default()

    draw = ImageDraw.Draw(dark_bg)

    # --- Thumbnail Glow ---
    thumb = base.resize((THUMB_W, THUMB_H))
    tmask = Image.new("L", thumb.size, 0)
    ImageDraw.Draw(tmask).rounded_rectangle((0, 0, THUMB_W, THUMB_H), 25, fill=255)
    glow = thumb.filter(ImageFilter.GaussianBlur(12))
    dark_bg.paste(glow, (THUMB_X - 4, THUMB_Y - 4), tmask)
    dark_bg.paste(thumb, (THUMB_X, THUMB_Y), tmask)

    # --- Title with Background Block ---
    trimmed_title = trim_to_width(title, title_font, MAX_TITLE_WIDTH)
    text_w = int(title_font.getlength(trimmed_title)) + 40
    text_bg = Image.new("RGBA", (text_w, 50), (0, 0, 0, 180))
    dark_bg.paste(text_bg, (TITLE_X - 20, TITLE_Y - 8), text_bg)
    draw.text((TITLE_X, TITLE_Y), trimmed_title, font=title_font, fill="#FFD700")

    # --- Meta Info ---
    meta_text = f"YouTube | {views}"
    meta_w = int(regular_font.getlength(meta_text)) + 30
    meta_bg = Image.new("RGBA", (meta_w, 32), (0, 0, 0, 160))
    dark_bg.paste(meta_bg, (META_X - 10, META_Y - 3), meta_bg)
    draw.text((META_X, META_Y), meta_text, fill="#FFEB3B", font=regular_font)

    # --- Progress Bar ---
    draw.line([(BAR_X, BAR_Y), (BAR_X + BAR_TOTAL_LEN, BAR_Y)], fill=(70, 70, 70), width=6)
    draw.line([(BAR_X, BAR_Y), (BAR_X + BAR_RED_LEN, BAR_Y)], fill=(255, 105, 180), width=8)
    draw.text((BAR_X, BAR_Y + 15), "00:00", fill="white", font=regular_font)
    draw.text((BAR_X + BAR_TOTAL_LEN - 70, BAR_Y + 15), duration_text, fill="#FF80AB", font=regular_font)

    # --- Dev & IG Signature ---
    sig_font = ImageFont.truetype("AviaxMusic/assets/font.ttf", 22)
    draw.text((40, 25), "Dev: @SunsetOfMe", font=sig_font, fill="#FFEB3B")
    draw.text((1020, 25), "IG: @daily_grief", font=sig_font, fill="#FFEB3B")

    # --- Cleanup ---
    try:
        os.remove(thumb_path)
    except OSError:
        pass

    dark_bg.save(cache_path, quality=95)
    return cache_path
    
