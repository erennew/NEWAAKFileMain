import os
import time
import asyncio
import platform
import psutil
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction  # ✅ NEW (works in v2.x)
from bot import Bot, START_TIME
from config import ADMINS, USER_REPLY_TEXT
from database.database import full_userbase
from helper_func import reply_with_clean, request_timestamps, GLOBAL_REQUESTS, TIME_WINDOW, USER_REQUESTS
from pyrogram.enums import ParseMode

# Auto-delete configuration from environment
AUTO_DELETE_TIME = int(os.getenv("AUTO_DELETE_TIME", 900))  # 15 minutes default
AUTO_CLEAN = os.getenv("AUTO_CLEAN", "False").lower() == "true"
DELETE_DELAY = int(os.getenv("DELETE_DELAY", 10))  # 10 seconds default

def get_readable_time(seconds):
    """Convert seconds to human-readable pirate time"""
    intervals = (
        ('d', 86400),
        ('h', 3600),
        ('m', 60),
        ('s', 1)
    )
    result = []
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            result.append(f"{int(value)}{name}")
    return " ".join(result) or "0s"

@Bot.on_message(filters.command("stats") & filters.user(ADMINS))
async def stats(client, message: Message):
    """Pirate-themed system statistics command"""
    # Show typing indicator
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    
    # Calculate metrics
    uptime = get_readable_time(time.time() - START_TIME)
    total_users = len(await full_userbase())
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    platform_info = f"{platform.system()} {platform.release()}"
    
    # Build pirate report
    report = (
        f"<b>🏴‍☠️ LUFFY BOT PIRATE REPORT 🏴‍☠️</b>\n\n"
        f"⏳ <b>Voyage Duration:</b> <code>{uptime}</code>\n"
        f"👥 <b>Crew Members:</b> <code>{total_users}</code>\n"
        f"🧭 <b>Navigation System:</b> <code>{platform_info}</code>\n\n"
        f"⚡ <b>Ship Status:</b>\n"
        f"  • CPU: <code>{cpu}%</code>\n"
        f"  • RAM: <code>{mem.percent}%</code> ({mem.used//(1024**2)}MB/{mem.total//(1024**2)}MB)\n"
        f"  • Storage: <code>{disk.percent}%</code>\n\n"
        f"🌊 <b>Current Limits:</b>\n"
        f"  • Global: <code>{len(request_timestamps)}/{GLOBAL_REQUESTS}</code>\n"
        f"  • Your: <code>{sum(1 for ts in request_timestamps if isinstance(ts, tuple) and ts[0] == message.from_user.id)}/{USER_REQUESTS}</code>"
    )

    await reply_with_clean(message, report, parse_mode=ParseMode.HTML)



@Bot.on_message(filters.command("ping") & filters.user(ADMINS))
async def ping(client, message: Message):
    """Animated ping command with pirate theme"""
    start = time.time()
    
    # Ping animation sequence
    animation = [
        "🏴‍☠️ Loading cola cannons...",
        "⚡ Stretching rubber arms...",
        "🌊 Sending signal across Grand Line..."
    ]
    
    msg = await message.reply_text(animation[0])
    for step in animation[1:]:
        await asyncio.sleep(0.7)
        await msg.edit_text(step)
    
    # Calculate and show response
    ping_time = int((time.time() - start) * 1000)
    response = (
        f"⚡ <b>Gear Second Speed!</b> <code>{ping_time}ms</code>" if ping_time < 100 else
        f"⛵ <b>Smooth Sailing!</b> <code>{ping_time}ms</code>" if ping_time < 300 else
        f"🐌 <b>Sea King Lag!</b> <code>{ping_time}ms</code>"
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
