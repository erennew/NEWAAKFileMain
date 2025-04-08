# (©) WeekendsBotz
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS, DB_CHANNEL
from helper_func import encode, get_message_id
import logging

# Set up logging
logger = logging.getLogger(__name__)

async def get_valid_message(client: Client, user_id: int, prompt_text: str) -> tuple:
    """
    Improved message validation with better error handling
    Returns: (message_object, message_id) or (None, None)
    """
    try:
        user_message = await client.ask(
            text=prompt_text,
            chat_id=user_id,
            filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
            timeout=60
        )
        
        if not hasattr(client, 'db_channel'):
            await user_message.reply("❌ DB Channel not configured", quote=True)
            return None, None
            
        msg_id = await get_message_id(client, user_message)
        if not msg_id:
            await user_message.reply(
                "❌ Invalid message\n\n"
                "1. Must be forwarded from DB Channel\n"
                "2. Or must be a valid DB Channel post link\n"
                f"DB Channel ID: {client.db_channel.id}",
                quote=True
            )
            return None, None
            
        return user_message, msg_id
        
    except Exception as e:
        logger.error(f"Error in get_valid_message: {e}")
        return None, None

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch_handler(client: Client, message: Message):
    """Handle batch file link generation"""
    # Verify DB channel is set up
    if not hasattr(client, 'db_channel') or not client.db_channel:
        await message.reply("❌ Error: DB Channel not configured")
        return

    # Get first message
    first_msg, f_msg_id = await get_valid_message(
        client,
        message.from_user.id,
        "📥 Forward the FIRST message from DB Channel\n"
        "OR send the DB Channel post link"
    )
    if not f_msg_id:
        return

    # Get last message
    second_msg, s_msg_id = await get_valid_message(
        client,
        message.from_user.id,
        "📤 Forward the LAST message from DB Channel\n"
        "OR send the DB Channel post link"
    )
    if not s_msg_id:
        return

    # Generate and send link
    try:
        # Simple string format without channel ID multiplication
        string = f"get_batch_{f_msg_id}_{s_msg_id}"
        base64_string = await encode(string)
        link = f"https://t.me/{client.username}?start={base64_string}"
        
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔗 Share Link", url=f'https://telegram.me/share/url?url={link}')
        ]])
        
        await second_msg.reply_text(
            f"🔗 Batch Link Generated:\n\n<code>{link}</code>",
            reply_markup=reply_markup,
            quote=True
        )
    except Exception as e:
        logger.error(f"Batch error: {e}")
        await message.reply("❌ Failed to generate batch link")

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    """Handle single file link generation"""
    if not hasattr(client, 'db_channel') or not client.db_channel:
        await message.reply("❌ Error: DB Channel not configured")
        return

    # Get message from user
    channel_msg, msg_id = await get_valid_message(
        client,
        message.from_user.id,
        "📨 Forward a message from DB Channel\n"
        "OR send the DB Channel post link"
    )
    if not msg_id:
        return

    # Generate and send link
    try:
        # Simple string format without channel ID multiplication
        string = f"get_file_{msg_id}"
        base64_string = await encode(string)
        link = f"https://t.me/{client.username}?start={base64_string}"
        
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔗 Share Link", url=f'https://telegram.me/share/url?url={link}')
        ]])
        
        await channel_msg.reply_text(
            f"🔗 File Link Generated:\n\n<code>{link}</code>",
            reply_markup=reply_markup,
            quote=True
        )
    except Exception as e:
        logger.error(f"Genlink error: {e}")
        await message.reply("❌ Failed to generate file link")
