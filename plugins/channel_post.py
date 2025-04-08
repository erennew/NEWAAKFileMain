# (©) WeekendsBotz
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS, DB_CHANNEL, FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4
from helper_func import encode, get_message_id, is_subscribed
import logging

logger = logging.getLogger(__name__)

# Create dynamic list of active channels
ACTIVE_CHANNELS = [
    channel for channel in [
        FORCE_SUB_CHANNEL_1,
        FORCE_SUB_CHANNEL_2,
        FORCE_SUB_CHANNEL_3,
        FORCE_SUB_CHANNEL_4
    ] if channel  # Only include configured channels
]

# --- Admin Side (Link Generation) ---
@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def generate_link(client: Client, message: Message):
    """Generate shareable links for files in DB channel"""
    # Get the message from admin
    msg = await client.ask(
        chat_id=message.from_user.id,
        text="📤 Forward the file from DB Channel or send its link",
        filters=filters.forwarded | (filters.text & ~filters.forwarded),
        timeout=120
    )
    
    # Validate message
    msg_id = await get_message_id(client, msg)
    if not msg_id:
        return await msg.reply("❌ Invalid message. Must be from DB Channel", quote=True)
    
    # Create encoded link
    encoded = await encode(f"file_{msg_id}")
    link = f"https://t.me/{client.username}?start={encoded}"
    
    # Send to admin
    await msg.reply_text(
        f"🔗 Your Shareable Link:\n\n{link}",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("Share Link", url=f"https://t.me/share/url?url={link}")
        ]]),
        quote=True
    )

# --- User Side (File Delivery) ---
@Bot.on_message(filters.private & filters.command("start"))
async def deliver_file(client: Client, message: Message):
    """Handle user requests for files"""
    if len(message.command) < 2:
        return await message.reply("Send me a valid file link")
    
    # Check force subscription
    if not await is_subscribed(None, client, message):
        # Create buttons for each active channel
        buttons = []
        for channel in ACTIVE_CHANNELS:
            buttons.append([InlineKeyboardButton(f"Join Channel", url=f"t.me/{channel}")])
        
        return await message.reply_text(
            "📢 Join our channels first to access files:",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
    
    try:
        # Decode file ID
        file_id = int(message.command[1].split("_")[1])
        
        # Forward file to user
        await client.copy_message(
            chat_id=message.chat.id,
            from_chat_id=DB_CHANNEL,
            message_id=file_id
        )
        
    except Exception as e:
        logger.error(f"File delivery error: {e}")
        await message.reply("❌ Failed to send file. Link may be expired.", quote=True)
