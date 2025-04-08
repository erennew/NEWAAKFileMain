from bot import Bot
from pyrogram.types import Message
from pyrogram import filters
from config import ADMINS, BOT_STATS_TEXT, USER_REPLY_TEXT
from datetime import datetime
from helper_func import get_readable_time
import time  # Add this at the top
# Simple rate limit tracking
user_last_request = {}

@Bot.on_message(filters.command('stats') & filters.user(ADMINS))
async def stats(bot: Bot, message: Message):
    now = datetime.now()
    delta = now - bot.uptime
    time = get_readable_time(delta.seconds)
    await message.reply(BOT_STATS_TEXT.format(uptime=time))

@Bot.on_message(filters.private & filters.incoming)
async def useless(client: Bot, message: Message):
    # Basic rate limiting
    user_id = message.from_user.id
    current_time = time.time()
    
    if user_id in user_last_request:
        if current_time - user_last_request[user_id] < 1:  # 1 second cooldown
            return
    
    user_last_request[user_id] = current_time
    
    if USER_REPLY_TEXT:
        await message.reply(USER_REPLY_TEXT)
