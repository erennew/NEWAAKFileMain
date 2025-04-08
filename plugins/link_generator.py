from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id

# ⚙️ Helper function to get a valid DB Channel message
async def get_valid_db_message(client, user_id, ask_text):
    while True:
        try:
            response = await client.ask(
                chat_id=user_id,
                text=ask_text,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except:
            return None, None

        msg_id = await get_message_id(client, response)
        if msg_id:
            return response, msg_id
        else:
            await response.reply("❌ <b>Invalid DB Channel message.</b>\n\nMake sure it's forwarded from or linked to the original DB Channel.", quote=True)

# 🏴‍☠️ /batch - Generate file batch links from DB posts
@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch(client: Client, message: Message):
    resp1, f_msg_id = await get_valid_db_message(
        client,
        message.from_user.id,
        "<b>📥 Forward the <u>First</u> Message from the DB Channel or Send the Link</b>"
    )
    if not f_msg_id:
        return

    resp2, s_msg_id = await get_valid_db_message(
        client,
        message.from_user.id,
        "<b>📤 Now forward the <u>Last</u> Message from the DB Channel or Send the Link</b>"
    )
    if not s_msg_id:
        return

    # Encode the link string
    encoded = await encode(f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={encoded}"

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Share Link", url=f"https://telegram.me/share/url?url={link}")]
    ])

    await resp2.reply_text(
        f"<b>🏴‍☠️ Here’s your treasure map!</b>\n\n<code>{link}</code>",
        reply_markup=reply_markup,
        quote=True
    )

# 🧭 /genlink - Generate link for a single post
@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def genlink(client: Client, message: Message):
    resp, msg_id = await get_valid_db_message(
        client,
        message.from_user.id,
        "<b>📬 Forward a DB Channel Message or Send its Link</b>"
    )
    if not msg_id:
        return

    encoded = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={encoded}"

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Share Link", url=f"https://telegram.me/share/url?url={link}")]
    ])

    await resp.reply_text(
        f"<b>🏴‍☠️ Here’s your treasure link!</b>\n\n<code>{link}</code>",
        reply_markup=reply_markup,
        quote=True
    )
