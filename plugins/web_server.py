from aiohttp import web
import os

# Basic health check endpoint
async def handle(request):
    return web.Response(text="Luffy Bot sailing smooth! 🏴‍☠️")

# Function to launch the web server
async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)

    runner = web.AppRunner(app)
    await runner.setup()

    # Koyeb expects the service on port 8000
    port = int(os.environ.get("PORT", 8000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
