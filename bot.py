from aiohttp import web
from plugins import web_server
import time
import asyncio
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime
from config import (
    API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS,
    FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2,
    FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4,
    CHANNEL_ID, PORT,
    FLOOD_MAX_REQUESTS, FLOOD_TIME_WINDOW, FLOOD_COOLDOWN
)

START_TIME = time.time()

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER
        self.user_rate_limit = {}  # Flood control dictionary

    async def check_flood(self, user_id: int) -> tuple:
        """Returns (is_flooding, warning_level)"""
        now = time.time()
        user_data = self.user_rate_limit.setdefault(user_id, {
            "timestamps": [],
            "warn_level": 0,
            "last_warn": 0
        })
        
        # Clean old requests
        user_data["timestamps"] = [
            t for t in user_data["timestamps"] 
            if now - t < FLOOD_TIME_WINDOW
        ]
        
        request_count = len(user_data["timestamps"])
        if request_count >= FLOOD_MAX_REQUESTS * 2:
            user_data["warn_level"] = 2  # Timeout
            return True, 2
        elif request_count >= FLOOD_MAX_REQUESTS:
            user_data["warn_level"] = 1  # Warning
            return True, 1
        
        user_data["timestamps"].append(now)
        return False, 0

    async def reset_flood_counts(self):
        """Auto-reset warn levels periodically"""
        while True:
            await asyncio.sleep(FLOOD_TIME_WINDOW * 2)
            for user_data in self.user_rate_limit.values():
                if time.time() - user_data.get("last_warn", 0) > FLOOD_TIME_WINDOW * 3:
                    user_data["warn_level"] = 0

    async def start(self):
        self.LOGGER(__name__).info("🚀 Starting bot initialization...")
        await super().start()
        
        # Start flood control task
        asyncio.create_task(self.reset_flood_counts())

        try:
            usr_bot_me = await self.get_me()
            self.username = usr_bot_me.username
            self.LOGGER(__name__).info(f"🤖 Bot @{self.username} initialized")
        except Exception as e:
            self.LOGGER(__name__).error(f"❌ Bot startup failed: {e}")
            sys.exit(1)

        # Force Sub Channels Setup
        for idx, channel in enumerate([
            FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2,
            FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4
        ], 1):
            if channel:
                try:
                    chat = await self.get_chat(channel)
                    link = chat.invite_link or await self.export_chat_invite_link(channel)
                    setattr(self, f"invitelink{'' if idx == 1 else idx}", link)
                except Exception as e:
                    self.LOGGER(__name__).error(f"❌ Force sub channel {idx} setup failed: {e}")
                    sys.exit(1)

        # DB Channel Verification
        try:
            self.db_channel = await self.get_chat(CHANNEL_ID)
            test_msg = await self.send_message(CHANNEL_ID, "🔧 Bot connectivity test")
            await test_msg.delete()
        except Exception as e:
            self.LOGGER(__name__).error(f"❌ DB channel setup failed: {e}")
            sys.exit(1)

        # Web Server Setup
        try:
            app = web.AppRunner(await web_server())
            await app.setup()
            await web.TCPSite(app, "0.0.0.0", PORT).start()
            self.LOGGER(__name__).info(f"🌐 Web server started on port {PORT}")
        except Exception as e:
            self.LOGGER(__name__).error(f"❌ Web server failed: {e}")

        self.set_parse_mode(ParseMode.HTML)
        self.uptime = datetime.now()
        self.LOGGER(__name__).info(f"""
┈┈┈╱▔▔▔▔▔▔╲┈╭━━━━━━━╮┈┈
┈┈▕┈╭━╮╭━╮┈▏┃Bot Activated!
┈┈▕┈┃╭╯╰╮┃┈▏╰┳━━━━━━╯┈┈
┈┈▕┈╰╯╭╮╰╯┈▏┈┃Uptime: {self.uptime}
┈┈▕┈┈┈┃┃┈┈┈▏━╯Flood Control: Active
┈┈▕┈┈┈╰╯┈┈┈▏┈┈Channels: {len([c for c in [
    FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2,
    FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4] if c])}
┈┈▕╱╲╱╲╱╲╱╲▏┈┈Mode: {'DEBUG' if __debug__ else 'PROD'}
        """)

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("🛑 Bot stopped gracefully")

__all__ = ["Bot", "START_TIME"]
