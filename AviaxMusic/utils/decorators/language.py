#  Copyright (c) 2025 Aviax
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Language Decorators for AviaxMusic Bot

from pyrogram import Client
from pyrogram.types import Message, CallbackQuery

from AviaxMusic import app
from AviaxMusic.misc import SUDOERS
from AviaxMusic.utils.database import get_lang, is_maintenance
from config import SUPPORT_GROUP
from strings import get_string


# ───────────────────────────────
#  General Language Decorator
# ───────────────────────────────
def language(func):
    async def wrapper(_, message: Message, **kwargs):
        # Maintenance check
        if await is_maintenance() is False:
            if message.from_user and message.from_user.id not in SUDOERS:
                return await message.reply_text(
                    text=(
                        f"{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ⚙️\n\n"
                        f"⛓️ ᴠɪsɪᴛ <a href='{SUPPORT_GROUP}'>sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ</a> "
                        f"ғᴏʀ ᴜᴘᴅᴀᴛᴇs ᴏʀ ʀᴇᴀsᴏɴs."
                    ),
                    disable_web_page_preview=True,
                )

        # Try to delete triggering command if possible
        try:
            await message.delete()
        except Exception:
            pass

        # Get user language
        try:
            lang_code = await get_lang(message.chat.id)
            language = get_string(lang_code)
        except Exception:
            language = get_string("en")

        return await func(_, message, language, **kwargs)

    return wrapper


# ───────────────────────────────
#  CallbackQuery Language Decorator
# ───────────────────────────────
def languageCB(func):
    async def wrapper(_, callback_query: CallbackQuery, **kwargs):
        # Maintenance check
        if await is_maintenance() is False:
            if callback_query.from_user and callback_query.from_user.id not in SUDOERS:
                return await callback_query.answer(
                    f"{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ⚙️\n"
                    f"ᴊᴏɪɴ sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ ғᴏʀ ᴜᴘᴅᴀᴛᴇs.",
                    show_alert=True,
                )

        # Get language safely
        try:
            lang_code = await get_lang(callback_query.message.chat.id)
            language = get_string(lang_code)
        except Exception:
            language = get_string("en")

        return await func(_, callback_query, language, **kwargs)

    return wrapper


# ───────────────────────────────
#  Lightweight Language Decorator for /start etc.
# ───────────────────────────────
def LanguageStart(func):
    async def wrapper(_, message: Message, **kwargs):
        try:
            lang_code = await get_lang(message.chat.id)
            language = get_string(lang_code)
        except Exception:
            language = get_string("en")

        return await func(_, message, language, **kwargs)

    return wrapper
