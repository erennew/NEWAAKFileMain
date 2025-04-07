import asyncio
from pyrogram import Client
from fastapi import FastAPI
import uvicorn
import os
import signal

# FastAPI health check app
app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "alive"}

class BotWrapper:
    def __init__(self):
        self.bot = Client(
            "luffy_bot",
            api_id=os.getenv("API_ID"),
            api_hash=os.getenv("API_HASH"),
            bot_token=os.getenv("BOT_TOKEN"),
            in_memory=True
        )
        self.running_event = asyncio.Event()

    async def start(self):
        await self.bot.start()
        print("🏴‍☠️ Luffy bot sailing the Grand Line!")
        await self.running_event.wait()

    async def stop(self):
        print("⚓ Stopping the bot...")
        self.running_event.set()
        await self.bot.stop()

async def run_server():
    config = uvicorn.Config(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    bot_wrapper = BotWrapper()

    async def shutdown_handler():
        await bot_wrapper.stop()

    # Graceful shutdown on SIGTERM/SIGINT
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown_handler()))

    await asyncio.gather(
        bot_wrapper.start(),
        run_server()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👋 Received goodbye signal.")
