from aiohttp import web

async def handle_home(request):
    return web.Response(text="Luffy File Bot is alive! 🏴‍☠️")

def web_server():
    app = web.Application()
    app.router.add_get("/", handle_home)  # You can also add more routes here
    return app
