import time

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from AviaxMusic import app
from AviaxMusic.misc import _boot_
from AviaxMusic.plugins.sudo.sudoers import sudoers_list
from AviaxMusic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from AviaxMusic.utils import bot_sys_stats
from AviaxMusic.utils.decorators.language import LanguageStart
from AviaxMusic.utils.formatters import get_readable_time
from AviaxMusic.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string

# ───────────────────────────────
#  Anime / Aesthetic Start Images
# ───────────────────────────────

NEXI_VID = [
    "https://graph.org/file/f76fd86d1936d45a63c64.jpg",
    "https://graph.org/file/69ba894371860cd22d92e.jpg",
    "https://graph.org/file/67fde88d8c3aa8327d363.jpg",
    "https://graph.org/file/3a400f1f32fc381913061.jpg",
    "https://graph.org/file/a0893f3a1e6777f6de821.jpg",
    "https://graph.org/file/5a285fc0124657c7b7a0b.jpg",
    "https://graph.org/file/a13e9733afdad69720d67.jpg",
    "https://graph.org/file/52713c9fe9253ae668f13.jpg",
]

# ───────────────────────────────
#  /start in Private Chat
# ───────────────────────────────

@app.on_message(filters.command(["start"]) & filters.private & ~config.BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)
    await message.react("🌚")

    # Typing animation effect
    typing_message = await message.reply("<b>ᴅɪηɢ..ᴅσηɢ..🥀</b>")
    typing_text = "<b>𝖲ᴛᴧʀᴛɪηɢ...❤️‍🔥</b>"

    for i in range(1, len(typing_text) + 1):
        try:
            await typing_message.edit_text(typing_text[:i])
            await asyncio.sleep(0.01)
        except Exception:
            break

    await asyncio.sleep(1)
    await typing_message.delete()

    # Handle subcommands
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]

        if name.startswith("help"):
            keyboard = help_pannel(_)
            await message.reply_sticker("CAACAgIAAxkBAAEBAjVnjyrcOqBOoPgtfLpcN3vlL7h4eAAC5SsAAmMK-UnNyZDgYsxtfjYE")
            return await message.reply_photo(
                random.choice(NEXI_VID),
                caption=_["help_1"].format(config.SUPPORT_GROUP),
                protect_content=True,
                reply_markup=keyboard,
            )

        if name.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                await app.send_message(
                    chat_id=config.LOG_GROUP_ID,
                    text=f"{message.from_user.mention} ᴊᴜsᴛ checked <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n"
                         f"<b>User ID:</b> <code>{message.from_user.id}</code>\n"
                         f"<b>Username:</b> @{message.from_user.username}",
                )
            return

        if name.startswith("inf"):
            m = await message.reply_text("🔎 Searching...")
            query = name.replace("info_", "", 1)
            results = VideosSearch(f"https://www.youtube.com/watch?v={query}", limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]

            searched_text = _["start_6"].format(
                title, duration, views, published, channellink, channel, app.mention
            )
            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=_["S_B_8"], url=link),
                        InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_GROUP),
                    ],
                ]
            )
            await m.delete()
            await app.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                reply_markup=key,
            )
            if await is_on_off(2):
                await app.send_message(
                    chat_id=config.LOG_GROUP_ID,
                    text=f"{message.from_user.mention} viewed <b>track info</b>.\n\n"
                         f"<b>User ID:</b> <code>{message.from_user.id}</code>\n"
                         f"<b>Username:</b> @{message.from_user.username}",
                )
            return

    # Normal /start message (no args)
    out = private_panel(_)
    UP, CPU, RAM, DISK = await bot_sys_stats()

    await message.reply_sticker("CAACAgIAAxkBAAEBAjVnjyrcOqBOoPgtfLpcN3vlL7h4eAAC5SsAAmMK-UnNyZDgYsxtfjYE")
    await message.reply_photo(
        random.choice(NEXI_VID),
        caption=_["start_2"].format(message.from_user.mention, app.mention, UP, DISK, CPU, RAM),
        reply_markup=InlineKeyboardMarkup(out),
    )

    if await is_on_off(2):
        await app.send_message(
            chat_id=config.LOG_GROUP_ID,
            text=f"{message.from_user.mention} started the bot.\n\n"
                 f"<b>User ID:</b> <code>{message.from_user.id}</code>\n"
                 f"<b>Username:</b> @{message.from_user.username}",
        )

# ───────────────────────────────
#  /start in Group Chat
# ───────────────────────────────

@app.on_message(filters.command(["start"]) & filters.group & ~config.BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - config._boot_)
    await message.reply_photo(
        random.choice(NEXI_VID),
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
    )
    return await add_served_chat(message.chat.id)

# ───────────────────────────────
#  New Member Welcome
# ───────────────────────────────

@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass
            if member.id == app.id:
                if message.chat.type != "supergroup":
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)
                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_GROUP,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                await message.reply_photo(
                    random.choice(NEXI_VID),
                    caption=_["start_3"].format(
                        message.from_user.first_name,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
        except Exception as ex:
            print(ex)
            

