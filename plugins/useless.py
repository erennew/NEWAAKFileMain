#from bot import Bot
#from pyrogram.types import Message
#from pyrogram import filters
#from config import ADMINS, BOT_STATS_TEXT, USER_REPLY_TEXT
#from datetime import datetime
#from helper_func import get_readable_time

#@Bot.on_message(filters.command('stats') & filters.user(ADMINS))
#async def stats(bot: Bot, message: Message):
#    now = datetime.now()
#    delta = now - bot.uptime
#    time = get_readable_time(delta.seconds)
 #   await message.reply(BOT_STATS_TEXT.format(uptime=time))

#@Bot.on_message(filters.private & filters.incoming)
#async def useless(_,message: Message):
#    if USER_REPLY_TEXT:
#        await message.reply(USER_REPLY_TEXT)
from pyrogram import filters
from pyrogram.types import Message
from bot import Bot, START_TIME
from config import ADMINS, USER_REPLY_TEXT
from database.database import full_userbase
import asyncio
from helper_func import request_timestamps, GLOBAL_REQUESTS, TIME_WINDOW, USER_REQUESTS, reply_with_clean
import platform
import time
START_TIME = time.time()
from config import AUTO_DELETE_TIME
import psutil
from helper_func import reply_with_clean

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
    uptime = get_readable_time(time.time() - START_TIME)
    total_users = len(await full_userbase())
    current_time = time.time()

    # Global rate count
    global_count = len([ts for ts in request_timestamps if current_time - ts <= TIME_WINDOW])
    global_usage = f"{global_count}/{GLOBAL_REQUESTS} in {TIME_WINDOW}s"

    # Per-user rate count
    user_id = message.from_user.id
    user_count = len([
        ts for ts in request_timestamps
        if isinstance(ts, tuple) and ts[0] == user_id and current_time - ts[1] <= TIME_WINDOW
    ])
    user_usage = f"{user_count}/{USER_REQUESTS} in {TIME_WINDOW}s"

    # System stats
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    memory_usage = f"{memory.used // (1024 ** 2)}MB / {memory.total // (1024 ** 2)}MB"
    platform_info = platform.system() + " " + platform.release()

    text = (
        f"☠️ <b>Luffy Bot Pirate Report</b>\n\n"
        f"🕒 Uptime: <code>{uptime}</code>\n"
        f"👥 Total Crew Members: <code>{total_users}</code>\n"
        f"🧭 Platform: <code>{platform_info}</code>\n"
        f"🖥️ CPU Usage: <code>{cpu_usage}%</code>\n"
        f"📦 RAM Usage: <code>{memory_usage}</code>\n\n"
        f"🌍 Global Rate: <code>{global_usage}</code>\n"
        f"🙋‍♂️ Your Rate: <code>{user_usage}</code>\n\n"
        f"⚠️ Rate limits help protect our pirate ship from sinking! 🏴‍☠️\n"
        f"🧃 Keep the meat ready, more adventures ahead!"
    )

    await reply_with_clean(message, text)

@Bot.on_message(filters.command("ping") & filters.user(ADMINS))
async def ping(client, message: Message):
    start = time.time()

    # Send the "pinging" message
    reply = await message.reply_text("🏴‍☠️ Pinging the Sunny...")

    await asyncio.sleep(0.5)

    # Calculate ping time
    end = time.time()
    ping_time = int((end - start) * 1000)

    # Edit the reply with the ping time
    await reply.edit_text(f"🏴‍☠️ Pong! Luffy's up and stretchin' in <code>{ping_time}ms</code>!")

    # Delete both reply and command after delay
    await asyncio.sleep(AUTO_DELETE_TIME)
    try:
        await reply.delete()
    except:
        pass

    try:
        await message.delete()
    except:
        pass


@Bot.on_message(filters.private & filters.incoming)
async def useless(_, message: Message):
    if USER_REPLY_TEXT:
        await reply_with_clean(message, USER_REPLY_TEXT)
