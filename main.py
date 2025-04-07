import asyncio
from pyrogram import idle
from bot import Bot
from plugins.web_server import web_server

bot = Bot()  # Instantiate the bot

async def start_bot():
    await web_server()           # Start the aiohttp web server
    await bot.start()            # Start the bot (uses Pyrogram's event loop)
    print("✅ Luffy Bot is online!")
    await idle()                 # Keep bot running until manually stopped
    await bot.stop()             # Stop gracefully on shutdown

# DO NOT USE asyncio.run() here; use the loop already in use
loop = asyncio.get_event_loop()
loop.run_until_complete(start_bot())
