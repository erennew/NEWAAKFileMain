from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS, DB_CHANNEL
from helper_func import encode, get_message_id


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch(client: Client, message: Message):
    try:
        first_message = await client.ask(
            chat_id=message.chat.id,
            text="<b>📥 Send the FIRST post from DB Channel (forwarded or link)</b>",
            filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
            timeout=60,
        )
        first_id = await get_message_id(client, first_message)
        if not first_id:
            return await first_message.reply("❌ Invalid first message. Try again.")
        
        second_message = await client.ask(
            chat_id=message.chat.id,
            text="<b>📤 Send the LAST post from DB Channel (forwarded or link)</b>",
            filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
            timeout=60,
        )
        second_id = await get_message_id(client, second_message)
        if not second_id:
            return await second_message.reply("❌ Invalid second message. Try again.")
        
        string = f"get-{first_id}-{second_id}"
        encoded = await encode(string)
        username = (await client.get_me()).username
        link = f"https://t.me/{username}?start={encoded}"

        await second_message.reply_text(
            f"<b>🏴‍☠️ Here's your treasure map!</b>\n\n<code>{link}</code>",
            reply_markup=InlineKeyboardMarkup([
                # [InlineKeyboardButton("🔁 Share Link", url=f"https://telegram.me/share/url?url={link}")],
                [InlineKeyboardButton("☠️ Get Files Again", url=link)]
            ]),
            quote=True,
        )
    except Exception as e:
        await message.reply_text(f"⚠️ Error: <code>{e}</code>")


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def genlink(client: Client, message: Message):
    try:
        forward = await client.ask(
            chat_id=message.chat.id,
            text="<b>📥 Send any message from DB Channel (forwarded or link)</b>",
            filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
            timeout=60,
        )
        msg_id = await get_message_id(client, forward)
        if not msg_id:
            return await forward.reply("❌ Invalid message. Try again.")

        encoded = await encode(f"get-{msg_id}")
        username = (await client.get_me()).username
        link = f"https://t.me/{username}?start={encoded}"

        await forward.reply_text(
            f"<b>🏴‍☠️ Here's your treasure link!</b>\n\n<code>{link}</code>",
            reply_markup=InlineKeyboardMarkup([
                # [InlineKeyboardButton("🔁 Share Link", url=f"https://telegram.me/share/url?url={link}")],
                [InlineKeyboardButton("☠️ Get File Again", url=link)]
            ]),
            quote=True,
        )
    except Exception as e:
        await message.reply_text(f"⚠️ Error: <code>{e}</code>")
