import asyncio
import os
from aiohttp import web
from bot import Bot  # your bot instance
from plugins.web_server import web_server

PORT = int(os.environ.get("PORT", 8000))  # Default to 8000 for Koyeb

async def start_bot():
    await Bot.start()
    print("Bot started.")

async def start_web_server():
    app = web_server()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"Web server running on port {PORT}")

async def main():
    await asyncio.gather(start_bot(), start_web_server())

if __name__ == "__main__":
    asyncio.run(main())
