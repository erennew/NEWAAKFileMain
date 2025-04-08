from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch_handler(client: Client, message: Message):
    try:
        # Ask for first message
        first_message = await client.ask(
            chat_id=message.chat.id,
            text="📥 <b>Send the FIRST post from DB Channel (forwarded or link)</b>",
            filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
            timeout=60
        )
        first_id = await get_message_id(client, first_message)
        if not first_id:
            return await first_message.reply("❌ This isn’t from the DB Channel. Try again.")

        # Ask for second message
        second_message = await client.ask(
            chat_id=message.chat.id,
            text="📤 <b>Now send the LAST post from DB Channel</b>",
            filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
            timeout=60
        )
        second_id = await get_message_id(client, second_message)
        if not second_id:
            return await second_message.reply("❌ This isn’t from the DB Channel. Try again.")

        # Generate batch encoded link
        payload = f"get-{first_id}-{second_id}"
        encoded = await encode(payload)
        bot_username = (await client.get_me()).username
        link = f"https://t.me/{bot_username}?start={encoded}"

        await second_message.reply_text(
            f"<b>🏴‍☠️ Here's your treasure map!</b>\n\n<code>{link}</code>",
            reply_markup=InlineKeyboardMarkup([
                 [InlineKeyboardButton("🔁 Share Link", url=f"https://telegram.me/share/url?url={link}")],
               # [InlineKeyboardButton("☠️ Get Files Again", url=link)]
            ]),
            quote=True
        )
    except Exception as e:
        await message.reply_text(f"⚠️ Error: <code>{e}</code>")


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def genlink_handler(client: Client, message: Message):
    try:
        # Ask for one DB message
        forward = await client.ask(
            chat_id=message.chat.id,
            text="📥 <b>Send a DB Channel message (forwarded or link)</b>",
            filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
            timeout=60
        )
        msg_id = await get_message_id(client, forward)
        if not msg_id:
            return await forward.reply("❌ Not a valid DB Channel post.")

        encoded = await encode(f"get-{msg_id}")
        bot_username = (await client.get_me()).username
        link = f"https://t.me/{bot_username}?start={encoded}"

        await forward.reply_text(
            f"<b>🏴‍☠️ Here's your treasure link!</b>\n\n<code>{link}</code>",
            reply_markup=InlineKeyboardMarkup([
                 [InlineKeyboardButton("🔁 Share Link", url=f"https://telegram.me/share/url?url={link}")],
                #[InlineKeyboardButton("☠️ Get File Again", url=link)]
            ]),
            quote=True
        )
    except Exception as e:
        await message.reply_text(f"⚠️ Error: <code>{e}</code>")
