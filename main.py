import asyncio
from pyrogram import idle
from bot import Bot  # This is your bot class
from plugins.web_server import web_server

bot = Bot()  # ✅ Instantiate your Bot class

async def main():
    await web_server()   # Start the aiohttp web server for health checks
    await bot.start()    # Start the Telegram bot
    print("✅ Luffy Bot is up and running! 🏴‍☠️")
    await idle()         # Keep the bot alive
    await bot.stop()     # Gracefully shut down when exiting

if __name__ == "__main__":
    asyncio.run(main())
