import asyncio
from bot import bot  # Reusing the instance created in bot.py
import logging

logging.basicConfig(level=logging.INFO)

async def main():
    try:
        await bot.start()     # Starts the bot (uses Pyrogram's async flow)
        await idle()          # Keeps the bot running (until a signal like SIGTERM)
    finally:
        await bot.stop()

if __name__ == "__main__":
    from pyrogram import idle
    asyncio.run(main())
