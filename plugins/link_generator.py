from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id

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
            await response.reply("❌ <b>Invalid DB Channel message.</b>\nMake sure it's forwarded from or linked to the original DB Channel.", quote=True)

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch(client: Client, message: Message):
    # Verify DB channel is configured
    if not hasattr(client, 'db_channel') or not client.db_channel:
        await message.reply("❌ DB Channel not configured!")
        return

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

    try:
        # Simplified ID handling - remove multiplication
        encoded = await encode(f"get-{f_msg_id}-{s_msg_id}")
        link = f"https://t.me/{client.username}?start={encoded}"
    except Exception as e:
        await message.reply(f"❌ Link generation failed: {str(e)}")
        return

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Share Link", url=f"https://telegram.me/share/url?url={link}")]
    ])

    await resp2.reply_text(
        f"<b>🏴‍☠️ Here's your batch link!</b>\n\n<code>{link}</code>",
        reply_markup=reply_markup,
        quote=True
    )
