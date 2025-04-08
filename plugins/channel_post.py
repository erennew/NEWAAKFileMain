# (©)Codexbotz

import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from bot import Bot
from config import ADMINS
from helper_func import encode

@Bot.on_message(
    filters.private & filters.user(ADMINS) & ~filters.command(
        ['start', 'users', 'broadcast', 'batch', 'genlink', 'stats', 'ping']
    )
)
async def channel_post(client: Client, message: Message):
    reply_text = await message.reply_text("⚙️ Hoisting the sails... Please wait!", quote=True)
    
    try:
        post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)
    except Exception as e:
        print(e)
        await reply_text.edit_text("☠️ Something went wrong while storing the file!")
        return

    converted_id = post_message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🎒 Get File Again", url=link)
            ]
        ]
    )

    await reply_text.edit(
        f"🏴‍☠️ <b>File Stored in the Grand Line!</b>\n\n"
        f"🔗 <b>Here’s your treasure map:</b>\n<code>{link}</code>",
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )
