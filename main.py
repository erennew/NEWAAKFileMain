# main.py

import asyncio
from pyrogram import idle
from bot import bot  # Import the already-created bot instance

async def main():
    await bot.start()   # Start your bot (async)
    await idle()        # Keep the bot running (like run() in sync)
    await bot.stop()    # Optional: graceful shutdown when stopped

if __name__ == "__main__":
    asyncio.run(main())
