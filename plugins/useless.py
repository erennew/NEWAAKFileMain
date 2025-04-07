from pyrogram import filters
from pyrogram.types import Message, ChatAction
from bot import Bot, START_TIME
from config import ADMINS, USER_REPLY_TEXT, AUTO_DELETE_TIME
from database.database import full_userbase
import asyncio
import platform
import time
import psutil
from helper_func import reply_with_clean, request_timestamps, GLOBAL_REQUESTS, TIME_WINDOW, USER_REQUESTS

def get_readable_time(seconds):
    count = 0
    time_list = []
    time_suffix_list = ["s", "m", "h", "d"]

    while count < 4 and seconds > 0:
        seconds, result = divmod(seconds, 60 if count < 2 else 24)
        time_list.append(f"{int(result)}{time_suffix_list[count]}")
        count += 1

    return " ".join(time_list[::-1])

@Bot.on_message(filters.command("stats") & filters.user(ADMINS))
async def stats(client, message: Message):
    # Calculate uptime in pirate style
    uptime_seconds = time.time() - START_TIME
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    # Get system metrics
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Current rate limits
    current_time = time.time()
    global_count = len([ts for ts in request_timestamps if current_time - ts <= TIME_WINDOW])
    user_count = len([
        ts for ts in request_timestamps
        if isinstance(ts, tuple) and ts[0] == message.from_user.id and current_time - ts[1] <= TIME_WINDOW
    ])

    # Pirate-themed stats message
    text = (
        f"<b>⚓ LUFFY BOT PIRATE REPORT ⚓</b>\n\n"
        f"⏳ <b>Voyage Duration:</b>\n"
        f"   - {int(days)} days\n"
        f"   - {int(hours)} hours\n"
        f"   - {int(minutes)} minutes\n"
        f"   - {int(seconds)} seconds\n\n"
        f"👥 <b>Crew Members:</b> <code>{len(await full_userbase())}</code>\n\n"
        f"⚡ <b>System Status:</b>\n"
        f"   - CPU: {cpu}% usage\n"
        f"   - RAM: {mem.percent}% used ({mem.used//(1024**2)}MB/{mem.total//(1024**2)}MB)\n"
        f"   - Storage: {disk.percent}% full\n\n"
        f"🌊 <b>Current Limits:</b>\n"
        f"   - Global: {global_count}/{GLOBAL_REQUESTS}\n"
        f"   - Your: {user_count}/{USER_REQUESTS}\n\n"
        f"<i>🏴‍☠️ The ship is sailing smoothly Captain!</i>"
    )
    
    # Show typing action for better UX
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(1)  # Dramatic pause
    
    await reply_with_clean(message, text, parse_mode="HTML")

@Bot.on_message(filters.command("ping") & filters.user(ADMINS))
async def ping(client, message: Message):
    start = time.time()
    
    # Pirate-themed ping animation
    steps = [
        "🏴‍☠️ Loading cola for cannon...",
        "⚡ Stretching rubber arms...",
        "🌊 Sending signal across Grand Line..."
    ]
    
    msg = await message.reply_text(steps[0])
    
    for step in steps[1:]:
        await asyncio.sleep(0.7)
        await msg.edit_text(step)
    
    ping_time = int((time.time() - start) * 1000)
    
    # Context-aware ping responses
    if ping_time < 100:
        response = f"⚡ <b>Gear Second Speed!</b> {ping_time}ms"
    elif ping_time < 300:
        response = f"⛵ <b>Smooth Sailing!</b> {ping_time}ms"
    else:
        response = f"🐌 <b>Sea King Lag!</b> {ping_time}ms"
    
    await msg.edit_text(response)
    await asyncio.sleep(AUTO_DELETE_TIME)
    await msg.delete()
    await message.delete()

@Bot.on_message(filters.private & filters.incoming)
async def useless(_, message: Message):
    if USER_REPLY_TEXT:
        await reply_with_clean(message, USER_REPLY_TEXT)
