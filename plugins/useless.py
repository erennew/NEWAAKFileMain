# (©) WeekendsBotz
import os
import time
import asyncio
import platform
import psutil
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction, ParseMode
from bot import Bot, START_TIME
from config import (
    ADMINS, 
    USER_REPLY_TEXT,
    GLOBAL_REQUESTS,
    TIME_WINDOW,
    USER_REQUESTS,
    AUTO_CLEAN,
    DELETE_DELAY
)
from database.database import full_userbase
from helper_func import (
    reply_with_clean,
    request_timestamps,
    get_readable_time
)

AUTO_DELETE_TIME = int(os.getenv("AUTO_DELETE_TIME", 900))  # 15 minutes default

def get_user_request_count(user_id: int) -> int:
    """Count requests from specific user"""
    return sum(1 for ts in request_timestamps 
              if time.time() - ts < TIME_WINDOW and isinstance(ts, tuple) and ts[0] == user_id)

@Bot.on_message(filters.command("stats") & filters.user(ADMINS))
async def stats(client, message: Message):
    """Pirate-themed system statistics command"""
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    
    uptime = get_readable_time(time.time() - START_TIME)
    total_users = len(await full_userbase())
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    report = (
        f"<b>🏴‍☠️ BOT STATUS REPORT 🏴‍☠️</b>\n\n"
        f"⏳ <b>Uptime:</b> <code>{uptime}</code>\n"
        f"👥 <b>Users:</b> <code>{total_users}</code>\n"
        f"🧭 <b>System:</b> <code>{platform.system()} {platform.release()}</code>\n\n"
        f"⚡ <b>Performance:</b>\n"
        f"  • CPU: <code>{cpu}%</code>\n"
        f"  • RAM: <code>{mem.percent}%</code>\n"
        f"  • Storage: <code>{disk.percent}%</code>\n\n"
        f"🌊 <b>Rate Limits:</b>\n"
        f"  • Global: <code>{len(request_timestamps)}/{GLOBAL_REQUESTS}</code>\n"
        f"  • Your: <code>{get_user_request_count(message.from_user.id)}/{USER_REQUESTS}</code>"
    )

    await reply_with_clean(message, report, parse_mode=ParseMode.HTML)

@Bot.on_message(filters.command("ping") & filters.user(ADMINS))
async def ping(client, message: Message):
    """Animated ping command"""
    start = time.time()
    msg = await message.reply("🏴‍☠️ Testing connection...")
    
    ping_time = int((time.time() - start) * 1000)
    response = (
        f"⚡ <b>Speed:</b> <code>{ping_time}ms</code>\n"
        f"🌊 <b>Status:</b> {'Excellent' if ping_time < 100 else 'Good' if ping_time < 300 else 'Slow'}"
    )
    
    await msg.edit_text(response)
    if AUTO_CLEAN:
        await asyncio.sleep(DELETE_DELAY)
        await msg.delete()
        await message.delete()

@Bot.on_message(filters.private & filters.incoming)
async def useless(_, message: Message):
    """Auto-reply to non-command messages"""
    if USER_REPLY_TEXT:
        await reply_with_clean(message, USER_REPLY_TEXT)
