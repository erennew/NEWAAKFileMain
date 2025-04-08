#(©)Codexbotz

import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from bot import Bot
from config import ADMINS, DB_CHANNEL
from helper_func import encode, is_user_limited

@Bot.on_message(
    filters.private & 
    filters.user(ADMINS) & 
    ~filters.command(['start','users','broadcast','batch','genlink','stats','ping'])
)
async def channel_post(client: Client, message: Message):
    
    # 🧊 Rate limiting check (even for admins)
    if await is_user_limited(message.from_user.id):
        return await message.reply_text("🧯 Whoa! You're going too fast. Try again in a few seconds.")

    # Boot-style sequence
    reply_text = await message.reply_text(
        "🛠️ Booting Gear 2...\n⚙️ Uploading to secret chamber...\n🔗 Crafting Pirate Link...",
        quote=True
    )

    try:
        post_message = await message.copy(
            chat_id=client.db_channel.id, 
            disable_notification=True
        )
    except FloodWait as e:
        await asyncio.sleep(e.value)
        post_message = await message.copy(
            chat_id=client.db_channel.id, 
            disable_notification=True
        )
    except Exception as e:
        print(e)
        return await reply_text.edit_text("🚨 Something went wrong while creating your treasure map!")

    # Generate encoded link
    converted_id = post_message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    # Pirate-themed button
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🦜 Get File Again", url=link)]]
    )

    await reply_text.edit(
        f"🏴‍☠️ <b>Here’s your secret pirate link:</b>\n\n{link}",
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )
