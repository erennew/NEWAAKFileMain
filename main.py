import asyncio
from bot import bot  # Import the Bot instance
from aiohttp import web

# Tiny web server for Koyeb health check
async def healthcheck(request):
    return web.Response(text="✅ Luffy bot alive!")

async def run_webserver():
    app = web.Application()
    app.router.add_get("/", healthcheck)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8000)  # Koyeb requires port 8000
    await site.start()

# Main async entry point
async def main():
    await asyncio.gather(
        bot.start(),
        run_webserver()
    )

# Run the bot + web server
if __name__ == "__main__":
    asyncio.run(main())
