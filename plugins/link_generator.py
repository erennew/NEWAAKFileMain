# (©) WeekendsBotz
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id

async def get_valid_message(client: Client, user_id: int, prompt_text: str) -> tuple:
    """
    Get a valid message from user with error handling
    Returns: (message_object, message_id) or (None, None) on failure
    """
    while True:
        try:
            user_message = await client.ask(
                text=prompt_text,
                chat_id=user_id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
            
            msg_id = await get_message_id(client, user_message)
            if msg_id:
                return user_message, msg_id
                
            await user_message.reply(
                "❌ Invalid message\n\n"
                "The forwarded post must be from my DB Channel "
                "or you must send a valid DB Channel post link",
                quote=True
            )
        except Exception as e:
            print(f"Error in get_valid_message: {e}")
            return None, None

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch(client: Client, message: Message):
    # Get first message
    first_msg, f_msg_id = await get_valid_message(
        client,
        message.from_user.id,
        "📥 Forward the FIRST message from DB Channel (with quotes)\n"
        "OR send the DB Channel post link"
    )
    if not f_msg_id:
        return

    # Get last message
    second_msg, s_msg_id = await get_valid_message(
        client,
        message.from_user.id,
        "📤 Forward the LAST message from DB Channel (with quotes)\n"
        "OR send the DB Channel post link"
    )
    if not s_msg_id:
        return

    # Generate link
    try:
        string = f"batch-{f_msg_id}-{s_msg_id}"
        base64_string = await encode(string)
        link = f"https://t.me/{client.username}?start={base64_string}"
        
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')
        ]])
        
        await second_msg.reply_text(
            f"✅ Here is your batch link:\n\n{link}",
            quote=True,
            reply_markup=reply_markup
        )
    except Exception as e:
        print(f"Error generating batch link: {e}")
        await message.reply("❌ Failed to generate link. Please try again.")

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    # Get message from user
    channel_msg, msg_id = await get_valid_message(
        client,
        message.from_user.id,
        "📨 Forward a message from DB Channel (with quotes)\n"
        "OR send the DB Channel post link"
    )
    if not msg_id:
        return

    # Generate link
    try:
        base64_string = await encode(f"file-{msg_id}")
        link = f"https://t.me/{client.username}?start={base64_string}"
        
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')
        ]])
        
        await channel_msg.reply_text(
            f"✅ Here is your file link:\n\n{link}",
            quote=True,
            reply_markup=reply_markup
        )
    except Exception as e:
        print(f"Error generating file link: {e}")
        await message.reply("❌ Failed to generate link. Please try again.")
