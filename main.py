import asyncio
from pyrogram import idle
from bot import Bot  # Your Pyrogram Bot object
from plugins.web_server import web_server

async def main():
    await web_server()  # Start web server for Koyeb/Heroku health checks
    await Bot.start()   # Start the Telegram bot
    print("✅ Luffy Bot is up and running! 🏴‍☠️")
    await idle()        # Wait for events

if __name__ == "__main__":
    asyncio.run(main())
