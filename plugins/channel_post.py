# (©) WeekendsBotz
import asyncio
import logging
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, RPCError

from bot import Bot
from config import ADMINS, DB_CHANNEL, DISABLE_CHANNEL_BUTTON
from helper_func import encode

logger = logging.getLogger(__name__)

@Bot.on_message(
    filters.private & 
    filters.user(ADMINS) & 
    ~filters.command(['start','users','broadcast','batch','genlink','stats'])
)
async def channel_post(client: Client, message: Message):
    """Handle admin posts to database channel"""
    processing_msg = await message.reply_text("⚙ Processing your file...", quote=True)
    
    try:
        # Copy message to DB channel with retry logic
        try:
            post_message = await message.copy(
                chat_id=DB_CHANNEL,
                disable_notification=True
            )
        except FloodWait as e:
            await processing_msg.edit_text(f"⏳ Flood wait: {e.value} seconds")
            await asyncio.sleep(e.value)
            post_message = await message.copy(
                chat_id=DB_CHANNEL,
                disable_notification=True
            )
            
        # Generate shareable link
        converted_id = post_message.id * abs(DB_CHANNEL)
        base64_string = await encode(f"get-{converted_id}")
        link = f"https://t.me/{client.username}?start={base64_string}"
        
        # Create share button
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔗 Share Link", url=f'https://telegram.me/share/url?url={link}'),
            InlineKeyboardButton("📥 Direct Link", url=link)
        ]])
        
        # Send final message
        await processing_msg.edit_text(
            f"✅ <b>Link Generated Successfully!</b>\n\n"
            f"<code>{link}</code>\n\n"
            f"• Post ID: <code>{post_message.id}</code>\n"
            f"• DB Channel: <code>{DB_CHANNEL}</code>",
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
        
    except RPCError as e:
        logger.error(f"Channel post error: {e}")
        await processing_msg.edit_text("❌ Failed to process your file. Please try again.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await processing_msg.edit_text("⚠️ An unexpected error occurred. Contact support.")
