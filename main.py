from bot import Bot
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot()
    await bot.start()
    await idle()  # Keeps the bot alive
    await bot.stop()

from pyrogram import idle

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped manually.")
