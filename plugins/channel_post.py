# (©) RaviBots / Originally: Codexbotz

import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, RPCError

from bot import Bot
from config import ADMINS, DB_CHANNEL, AUTO_DELETE_TIME, AUTO_DELETE_MSG, AUTO_DEL_SUCCESS_MSG
from helper_func import encode, is_user_limited


@Bot.on_message(
    filters.private &
    filters.user(ADMINS) &
    ~filters.command(['start', 'users', 'broadcast', 'batch', 'genlink', 'stats', 'ping'])
)
async def channel_post(client: Client, message: Message):
    user_id = message.from_user.id

    # ⛔ Rate limiting check
    if await is_user_limited(user_id):
        return await message.reply_text(
            "🧯 Whoa! You're going too fast.\nLet the sea breeze cool things down a bit 🕊️"
        )

    # 🛠 Boot animation
    boot_msg = await message.reply_text(
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
        print(f"[channelpost.py error] {e}")
        return await boot_msg.edit_text("🚨 Something went wrong while creating your treasure map!")

    # 🔒 Generate encoded link
    converted_id = post_message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    # ⏱ Schedule message auto-delete
    async def delete_db_message():
        await asyncio.sleep(AUTO_DELETE_TIME)
        try:
            await client.delete_messages(chat_id=client.db_channel.id, message_ids=post_message.id)
            print(f"🗑️ Deleted file {post_message.id} from DB_CHANNEL after {AUTO_DELETE_TIME} seconds")
        except RPCError as e:
            print(f"[auto-delete error] {e}")

    asyncio.create_task(delete_db_message())

    # 🏴‍☠️ Final pirate message
    await boot_msg.edit(
        f"🏴‍☠️ <b>Here’s your secret pirate link:</b>\n\n<code>{link}</code>\n\n{AUTO_DELETE_MSG}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🦜 Get File Again", url=link)]
        ]),
        disable_web_page_preview=True
    )
