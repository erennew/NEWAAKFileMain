from aiohttp import web

# Basic health check endpoint
async def handle(request):
    return web.Response(text="Luffy Bot sailing smooth! 🏴‍☠️")

# Function to launch the web server
async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
