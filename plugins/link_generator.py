from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch_handler(client: Client, message: Message):
    try:
        # Ask for FIRST message
        first_msg = await client.ask(
            chat_id=message.chat.id,
            text="📥 <b>Send the FIRST post from DB Channel (forwarded or message link)</b>",
            filters=(filters.forwarded | filters.text),
            timeout=60
        )
        first_id = await get_message_id(client, first_msg)
        if not first_id:
            return await first_msg.reply("❌ This isn’t a valid DB message.")

        # Ask for SECOND message
        second_msg = await client.ask(
            chat_id=message.chat.id,
            text="📤 <b>Now send the LAST post from DB Channel (forwarded or message link)</b>",
            filters=(filters.forwarded | filters.text),
            timeout=60
        )
        second_id = await get_message_id(client, second_msg)
        if not second_id:
            return await second_msg.reply("❌ This isn’t a valid DB message.")

        # Generate encoded payload
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
        await message.reply(f"⚠️ Error: <code>{e}</code>")


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def genlink_handler(client: Client, message: Message):
    try:
        # Ask for DB message
        reply = await client.ask(
            chat_id=message.chat.id,
            text="📥 <b>Send a DB Channel message (forwarded or message link)</b>",
            filters=(filters.forwarded | filters.text),
            timeout=60
        )
        msg_id = await get_message_id(client, reply)
        if not msg_id:
            return await reply.reply("❌ Not a valid DB message.")

        # Encode single file
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
        await message.reply(f"⚠️ Error: <code>{e}</code>")
