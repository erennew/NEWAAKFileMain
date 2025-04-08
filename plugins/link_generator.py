from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot  # Make sure this is your pyrogram Client
from config import ADMINS
from helper_func import encode, get_message_id


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command("batch"))
async def batch_handler(client, message: Message):
    try:
        first_msg = await client.ask(
            chat_id=message.chat.id,
            text="📥 <b>Send the FIRST DB Channel post (forward/link)</b>",
            filters=(filters.forwarded | filters.text),
            timeout=60
        )
        first_id = await get_message_id(client, first_msg)
        if not first_id:
            return await first_msg.reply("❌ Invalid DB message.")

        second_msg = await client.ask(
            chat_id=message.chat.id,
            text="📤 <b>Now send the LAST DB Channel post (forward/link)</b>",
            filters=(filters.forwarded | filters.text),
            timeout=60
        )
        second_id = await get_message_id(client, second_msg)
        if not second_id:
            return await second_msg.reply("❌ Invalid DB message.")

        payload = f"get-{first_id}-{second_id}"
        encoded = await encode(payload)
        bot_username = (await client.get_me()).username
        link = f"https://t.me/{bot_username}?start={encoded}"

        await second_msg.reply_text(
            f"<b>🏴‍☠️ Here's your treasure map!</b>\n\n<code>{link}</code>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("☠️ Get Files Again", url=link)]
            ]),
            quote=True
        )
    except Exception as e:
        await message.reply_text(f"⚠️ Error: <code>{e}</code>")


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command("genlink"))
async def genlink_handler(client, message: Message):
    try:
        reply = await client.ask(
            chat_id=message.chat.id,
            text="📥 <b>Send a DB Channel post (forward or link)</b>",
            filters=(filters.forwarded | filters.text),
            timeout=60
        )
        msg_id = await get_message_id(client, reply)
        if not msg_id:
            return await reply.reply("❌ Invalid DB message.")

        encoded = await encode(f"get-{msg_id}")
        bot_username = (await client.get_me()).username
        link = f"https://t.me/{bot_username}?start={encoded}"

        await reply.reply_text(
            f"<b>🏴‍☠️ Here's your treasure link!</b>\n\n<code>{link}</code>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("☠️ Get File Again", url=link)]
            ]),
            quote=True
        )
    except Exception as e:
        await message.reply_text(f"⚠️ Error: <code>{e}</code>")
