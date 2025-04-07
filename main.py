import asyncio
from aiohttp import web
from plugins.web_server import web_server  # Make sure this import matches your file

from config import PORT

async def _start_web_server():
    app = await web_server()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"✅ Web server running on port {PORT}")

async def main():
    await _start_web_server()
    # Start your bot here
    await bot.start()
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
