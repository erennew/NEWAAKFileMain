# (©) WeekendsBotz
import base64
import re
import asyncio
import logging
import time
from collections import deque, defaultdict
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import (
    ADMINS, DB_CHANNEL, AUTO_DELETE_TIME, AUTO_DEL_SUCCESS_MSG,
    AUTO_CLEAN, DELETE_DELAY, GLOBAL_REQUESTS, USER_REQUESTS,
    TIME_WINDOW, FLOOD_MAX_REQUESTS, FLOOD_TIME_WINDOW,
    SOFT_THROTTLE_WINDOW, FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2,
    FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4
)

# ===== INITIALIZATION ===== #
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===== GLOBAL RATE LIMIT TRACKING ===== #
request_timestamps = deque()
user_request_timestamps = defaultdict(deque)
user_last_action = {}

# ===== SUBSCRIPTION CHECK ===== #
async def is_subscribed(filter, client, update) -> bool:
    """Check if user is subscribed to required channels"""
    if not any([FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, 
               FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4]):
        return True

    user_id = update.from_user.id
    if user_id in ADMINS:
        return True

    member_status = (
        ChatMemberStatus.OWNER, 
        ChatMemberStatus.ADMINISTRATOR, 
        ChatMemberStatus.MEMBER
    )

    for channel_id in [
        FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2,
        FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4
    ]:
        if not channel_id:
            continue

        try:
            member = await client.get_chat_member(chat_id=channel_id, user_id=user_id)
            if member.status not in member_status:
                await client.send_message(
                    chat_id=user_id,
                    text=f"❌ Please join our channel first: @{channel_id}",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("Join Channel", url=f"t.me/{channel_id}")
                    ]])
                )
                return False
        except UserNotParticipant:
            await client.send_message(
                chat_id=user_id,
                text=f"❌ Please join our channel first: @{channel_id}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Join Channel", url=f"t.me/{channel_id}")
                ]])
            )
            return False
        except Exception as e:
            logger.error(f"Subscription check error for channel {channel_id}: {e}")
            continue

    return True

subscribed = filters.create(is_subscribed)

# ===== ENCODING/DECODING ===== #
async def encode(string: str) -> str:
    """Encode string to URL-safe base64"""
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    return base64_bytes.decode("ascii").strip("=")

async def decode(base64_string: str) -> str:
    """Decode URL-safe base64 to string"""
    base64_string = base64_string.strip("=")
    padding = "=" * (-len(base64_string) % 4)
    base64_bytes = (base64_string + padding).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes)
    return string_bytes.decode("ascii")

# ===== MESSAGE HANDLING ===== #
async def get_messages(client, message_ids: List[int]) -> List[Message]:
    """Batch fetch messages with flood control"""
    messages = []
    total_messages = 0
    
    while total_messages < len(message_ids):
        batch_ids = message_ids[total_messages:total_messages+200]
        try:
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=batch_ids
            )
            if isinstance(msgs, list):
                messages.extend(msgs)
            else:
                messages.append(msgs)
            total_messages += len(batch_ids)
        except FloodWait as e:
            logger.warning(f"Flood wait for {e.value} seconds")
            await asyncio.sleep(e.value)
        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            break
            
    return messages

async def get_message_id(client, message: Message) -> Optional[int]:
    """Improved message ID validation with error handling"""
    try:
        if message.forward_from_chat:
            if message.forward_from_chat.id == client.db_channel.id:
                return message.forward_from_message_id
            return None
        
        if not message.text:
            return None
            
        # Handle both t.me and telegram.me links
        pattern = r"(?:https?://)?(?:t\.me|telegram\.me)/(?:c/)?([^/]+)/(\d+)"
        matches = re.match(pattern, message.text.strip())
        if not matches:
            return None
            
        channel_ref, msg_id = matches.groups()
        
        # Convert message ID
        try:
            msg_id = int(msg_id)
        except ValueError:
            return None
            
        # Validate channel match
        if channel_ref.isdigit():
            if f"-100{channel_ref}" != str(client.db_channel.id):
                return None
        elif channel_ref.lower() != getattr(client.db_channel, 'username', '').lower():
            return None
            
        return msg_id
        
    except Exception as e:
        logger.error(f"Message ID validation error: {e}")
        return None

# ===== RATE LIMITING ===== #
async def check_rate_limit(user_id: int) -> Tuple[bool, Optional[int]]:
    """Combined rate limit check with cooldown remaining"""
    now = time.time()
    
    # Global limit
    while request_timestamps and now - request_timestamps[0] > TIME_WINDOW:
        request_timestamps.popleft()
    if len(request_timestamps) >= GLOBAL_REQUESTS:
        return True, None
    
    # User limit
    user_queue = user_request_timestamps[user_id]
    while user_queue and now - user_queue[0] > TIME_WINDOW:
        user_queue.popleft()
    
    if len(user_queue) >= USER_REQUESTS:
        cooldown = int(TIME_WINDOW - (now - user_queue[0]))
        return True, cooldown
    
    user_queue.append(now)
    request_timestamps.append(now)
    return False, None

async def is_soft_limited(user_id: int) -> bool:
    """Soft throttle: Prevents user spamming within a few seconds"""
    current_time = time.time()
    last_time = user_last_action.get(user_id, 0)

    if current_time - last_time < SOFT_THROTTLE_WINDOW:
        return True

    user_last_action[user_id] = current_time
    return False

# ===== UTILITY FUNCTIONS ===== #
def get_readable_time(seconds: int) -> str:
    """Convert seconds to human-readable time"""
    intervals = [
        ('days', 86400),
        ('h', 3600),
        ('m', 60),
        ('s', 1)
    ]
    
    result = []
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            result.append(f"{value}{name}")
    
    return " ".join(result) if result else "0s"

async def reply_with_clean(message: Message, text: str, **kwargs):
    """Reply with auto-delete functionality"""
    reply = await message.reply(text, **kwargs)
    if AUTO_CLEAN:
        asyncio.create_task(_auto_delete(reply, message))
    return reply

async def _auto_delete(*messages: Message):
    """Background task to delete messages"""
    await asyncio.sleep(DELETE_DELAY)
    for msg in messages:
        try:
            await msg.delete()
        except Exception as e:
            logger.error(f"Failed to auto-delete message: {e}")

# ===== BATCH HANDLER ===== #
async def get_valid_db_message(client, user_id: int, ask_text: str) -> Tuple[Optional[Message], Optional[int]]:
    """Get valid message from DB channel with retry logic"""
    try:
        response = await client.ask(
            chat_id=user_id,
            text=ask_text,
            filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
            timeout=60
        )
        msg_id = await get_message_id(client, response)
        if msg_id:
            return response, msg_id
        
        await response.reply("❌ Invalid DB Channel message. Please forward from DB channel or send direct link.", quote=True)
        return None, None
    except Exception as e:
        logger.error(f"Error getting valid DB message: {e}")
        return None, None

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch_handler(client: Client, message: Message):
    """Handle batch file requests"""
    # Check DB channel
    if not hasattr(client, 'db_channel') or not client.db_channel:
        await message.reply("❌ Database channel not configured!")
        return

    # Get first message
    resp1, f_msg_id = await get_valid_db_message(
        client,
        message.from_user.id,
        "<b>📥 Forward the FIRST Message from DB Channel or Send Link</b>"
    )
    if not f_msg_id:
        return

    # Get last message
    resp2, s_msg_id = await get_valid_db_message(
        client,
        message.from_user.id,
        "<b>📤 Forward the LAST Message from DB Channel or Send Link</b>"
    )
    if not s_msg_id:
        return

    # Generate link
    try:
        encoded = await encode(f"get_{f_msg_id}_{s_msg_id}")
        link = f"https://t.me/{client.username}?start={encoded}"
        
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔁 Share Link", url=f"https://telegram.me/share/url?url={link}")
        ]])
        
        await resp2.reply_text(
            f"<b>✅ Batch Link Generated!</b>\n\n<code>{link}</code>",
            reply_markup=reply_markup,
            quote=True
        )
    except Exception as e:
        logger.error(f"Batch link generation failed: {e}")
        await message.reply("❌ Failed to generate batch link. Please try again.")

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def genlink_handler(client: Client, message: Message):
    """Handle single file link generation"""
    if not hasattr(client, 'db_channel') or not client.db_channel:
        await message.reply("❌ Database channel not configured!")
        return

    resp, msg_id = await get_valid_db_message(
        client,
        message.from_user.id,
        "<b>📬 Forward a DB Channel Message or Send Link</b>"
    )
    if not msg_id:
        return

    try:
        encoded = await encode(f"get_{msg_id}")
        link = f"https://t.me/{client.username}?start={encoded}"
        
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔁 Share Link", url=f"https://telegram.me/share/url?url={link}")
        ]])
        
        await resp.reply_text(
            f"<b>✅ File Link Generated!</b>\n\n<code>{link}</code>",
            reply_markup=reply_markup,
            quote=True
        )
    except Exception as e:
        logger.error(f"Single link generation failed: {e}")
        await message.reply("❌ Failed to generate file link. Please try again.")
