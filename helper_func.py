# (©) WeekendsBotz
import base64
import re
import asyncio
import logging
from typing import List, Optional, Tuple

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message

from config import (
    FORCE_SUB_CHANNEL_1,
    FORCE_SUB_CHANNEL_2,
    FORCE_SUB_CHANNEL_3,
    FORCE_SUB_CHANNEL_4,
    ADMINS,
    AUTO_DELETE_TIME,
    AUTO_DEL_SUCCESS_MSG
)

# Initialize logger
logger = logging.getLogger(__name__)

async def is_subscribed(filter, client, update) -> bool:
    """Check if user is subscribed to required channels"""
    if not any([FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4]):
        return True

    user_id = update.from_user.id
    if user_id in ADMINS:
        return True

    member_status = (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER)

    for channel_id in [FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4]:
        if not channel_id:
            continue

        try:
            member = await client.get_chat_member(chat_id=channel_id, user_id=user_id)
            if member.status not in member_status:
                return False
        except UserNotParticipant:
            return False
        except Exception as e:
            logger.error(f"Error checking subscription for channel {channel_id}: {e}")
            continue

    return True

async def encode(string: str) -> str:
    """Encode string to URL-safe base64"""
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    return base64_bytes.decode("ascii").strip("=")

async def decode(base64_string: str) -> str:
    """Decode URL-safe base64 to string"""
    base64_string = base64_string.strip("=")  # Handle padding for old links
    padding = "=" * (-len(base64_string) % 4)
    base64_bytes = (base64_string + padding).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes)
    return string_bytes.decode("ascii")

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
            messages.extend(msgs)
            total_messages += len(batch_ids)
        except FloodWait as e:
            logger.warning(f"Flood wait for {e.value} seconds")
            await asyncio.sleep(e.value)
        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            break
            
    return messages

async def get_message_id(client, message: Message) -> Optional[int]:
    """Extract message ID from forwarded post or URL"""
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

async def delete_file(messages: List[Message], client, process: Message) -> None:
    """Delete messages after delay and send confirmation"""
    await asyncio.sleep(AUTO_DELETE_TIME)
    
    for msg in messages:
        try:
            await msg.delete()
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await msg.delete()
        except Exception as e:
            logger.error(f"Failed to delete message {msg.id}: {e}")
    
    try:
        await process.edit_text(AUTO_DEL_SUCCESS_MSG)
    except Exception as e:
        logger.error(f"Failed to edit process message: {e}")

# Create filter for subscription check
subscribed = filters.create(is_subscribed)
