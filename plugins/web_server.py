from aiohttp import web

async def handle(request):
    return web.Response(text="Luffy Bot sailing smooth! 🏴‍☠️")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
