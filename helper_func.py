# (©) WeekendsBotz
import base64
import re
import asyncio
import logging
import time
from collections import deque
from typing import List, Optional, Tuple

from collections import defaultdict
from datetime import datetime, timedelta
from config import FLOOD_MAX_REQUESTS, FLOOD_TIME_WINDOW, GLOBAL_REQUESTS, GLOBAL_TIME_WINDOW
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from config import (
    FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, 
    FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4,
    ADMINS, AUTO_DELETE_TIME, AUTO_DEL_SUCCESS_MSG,
    AUTO_CLEAN, DELETE_DELAY, GLOBAL_REQUESTS,
    USER_REQUESTS, TIME_WINDOW, FLOOD_MAX_REQUESTS,
    FLOOD_TIME_WINDOW
)
from config import DB_CHANNEL
# ===== GLOBAL RATE LIMIT TRACKING ===== #
request_timestamps = deque()
user_request_timestamps = {}
user_rate_limit = {}

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
            member = await client.get_chat_member(
                chat_id=channel_id, 
                user_id=user_id
            )
            if member.status not in member_status:
                return False
        except UserNotParticipant:
            return False
        except Exception as e:
            logging.error(f"Subscription check error: {e}")
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
async def get_messages(client, message_ids: List[int]):
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
            messages.extend(msgs)
            total_messages += len(batch_ids)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception as e:
            logging.error(f"Failed to get messages: {e}")
            break
            
    return messages

async def get_message_id(client, message: Message) -> int:
    """Extract message ID from forwarded post or URL"""
    if message.forward_from_chat:
        if message.forward_from_chat.id == client.db_channel.id:
            return message.forward_from_message_id
        return 0
    
    if message.forward_sender_name or not message.text:
        return 0
        
    pattern = r"https://t.me/(?:c/)?(.*)/(\d+)"
    matches = re.match(pattern, message.text)
    if not matches:
        return 0
        
    channel_id, msg_id = matches.groups()
    try:
        msg_id = int(msg_id)
    except ValueError:
        return 0
        
    if channel_id.isdigit():
        if f"-100{channel_id}" == str(client.db_channel.id):
            return msg_id
    elif channel_id == client.db_channel.username:
        return msg_id
        
    return 0

# ===== TIME FORMATTING ===== #
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

# ===== AUTO DELETE HANDLER ===== #
async def delete_file(messages: List[Message], client, process: Message):
    """Delete messages after delay and send confirmation"""
    await asyncio.sleep(AUTO_DELETE_TIME)
    
    for msg in messages:
        try:
            await msg.delete()
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await msg.delete()
        except Exception as e:
            logging.error(f"Failed to delete message {msg.id}: {e}")
    
    try:
        await process.edit_text(AUTO_DEL_SUCCESS_MSG)
        if AUTO_CLEAN:
            await asyncio.sleep(DELETE_DELAY)
            await process.delete()
    except Exception as e:
        logging.error(f"Failed to edit process message: {e}")

# ===== RATE LIMITING ===== #
def is_user_limited(user_id: int) -> bool:
    """Check if user has exceeded rate limits"""
    now = time.time()
    
    # Global rate limit
    while request_timestamps and now - request_timestamps[0] > TIME_WINDOW:
        request_timestamps.popleft()
    if len(request_timestamps) >= GLOBAL_REQUESTS:
        return True
    
    # User-specific rate limit
    if user_id not in user_request_timestamps:
        user_request_timestamps[user_id] = deque()
    
    user_queue = user_request_timestamps[user_id]
    while user_queue and now - user_queue[0] > TIME_WINDOW:
        user_queue.popleft()
    
    if len(user_queue) >= USER_REQUESTS:
        return True
    
    # Record the request
    request_timestamps.append(now)
    user_queue.append(now)
    return False

async def check_flood(user_id: int) -> Tuple[bool, int]:
    """Check if user is flooding with tiered warnings"""
    now = time.time()
    user_data = user_rate_limit.setdefault(user_id, {
        "timestamps": [],
        "warn_level": 0
    })
    
    # Clean old requests
    user_data["timestamps"] = [
        t for t in user_data["timestamps"] 
        if now - t < FLOOD_TIME_WINDOW
    ]
    
    if len(user_data["timestamps"]) >= FLOOD_MAX_REQUESTS:
        user_data["warn_level"] = 2
        return True, 2
    elif len(user_data["timestamps"]) >= (FLOOD_MAX_REQUESTS // 2):
        user_data["warn_level"] = 1
        return True, 1
    
    user_data["timestamps"].append(now)
    return False, 0

# ===== MESSAGE UTILITIES ===== #
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
        except Exception:
            pass
