# (©) WeekendsBotz
from aiohttp import web
from pyrogram import Client
from pyrogram.enums import ParseMode
from typing import Optional, Dict, Any, Tuple
import asyncio
import time
import sys
from datetime import datetime
from collections import defaultdict
import logging

from config import (
    API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS,
    FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2,
    FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4,
    DB_CHANNEL, PORT,
    FLOOD_MAX_REQUESTS, FLOOD_TIME_WINDOW, FLOOD_COOLDOWN
)
from plugins import web_server
import psutil

# Global task tracker
active_tasks = set()

async def dynamic_cooldown() -> float:
    """
    Adjust cooldown duration based on server load and active tasks.
    """
    load = psutil.cpu_percent(interval=1)
    base = 1.0

    if load > 70:
        base *= 1.5  # High CPU load
    if len(active_tasks) > 50:
        base *= 2  # High async task load

    return base

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="LuffyFileBot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS or 4,
            bot_token=TG_BOT_TOKEN,
            parse_mode=ParseMode.HTML,
            sleep_threshold=30,
            max_concurrent_transmissions=5
        )
        self.log = LOGGER
        self.user_rate_limit = defaultdict(self._init_user_flood_data)
        self.uptime: Optional[datetime] = None
        self.db_channel: Optional[Any] = None
        self.invitelinks: Dict[int, str] = {}

    @staticmethod
    def _init_user_flood_data() -> Dict[str, Any]:
        return {
            "timestamps": [],
            "warn_level": 0,
            "last_warn": 0
        }

    async def check_flood(self, user_id: int) -> Tuple[bool, int]:
        now = time.time()
        user_data = self.user_rate_limit[user_id]
        user_data["timestamps"] = [
            t for t in user_data["timestamps"]
            if now - t < FLOOD_TIME_WINDOW
        ]
        request_count = len(user_data["timestamps"])

        if request_count >= FLOOD_MAX_REQUESTS * 2:
            user_data["warn_level"] = 2
            wait = await dynamic_cooldown()
            await asyncio.sleep(wait)
            return True, 2
        elif request_count >= FLOOD_MAX_REQUESTS:
            user_data["warn_level"] = 1
            wait = await dynamic_cooldown()
            await asyncio.sleep(wait)
            return True, 1

        user_data["timestamps"].append(now)
        return False, 0

    async def _reset_flood_counts(self):
        while True:
            await asyncio.sleep(FLOOD_TIME_WINDOW * 2)
            cutoff = time.time() - (FLOOD_TIME_WINDOW * 3)
            for user_id, data in list(self.user_rate_limit.items()):
                if data["last_warn"] < cutoff:
                    if not data["timestamps"]:
                        del self.user_rate_limit[user_id]
                    else:
                        data["warn_level"] = 0

    async def _setup_force_sub_channels(self):
        channels = [
            (1, FORCE_SUB_CHANNEL_1),
            (2, FORCE_SUB_CHANNEL_2),
            (3, FORCE_SUB_CHANNEL_3),
            (4, FORCE_SUB_CHANNEL_4)
        ]

        for idx, channel_id in channels:
            if not channel_id:
                continue
            try:
                chat = await self.get_chat(channel_id)
                link = chat.invite_link or await self.export_chat_invite_link(channel_id)
                self.invitelinks[idx] = link
                self.log(__name__).info(f"✅ Force sub channel {idx} configured: {chat.title}")
            except Exception as e:
                self.log(__name__).error(f"❌ Failed to setup channel {idx}: {e}")
                raise

    async def _verify_db_channel(self):
        try:
            self.db_channel = await self.get_chat(DB_CHANNEL)
            test_msg = await self.send_message(DB_CHANNEL, "🔧 Connection test")
            await test_msg.delete()
        except Exception as e:
            self.log(__name__).error(f"❌ DB channel verification failed: {e}")
            raise

    async def _start_web_server(self):
        try:
            app = web.AppRunner(web_server())  # ✅ No `await` here!
            await app.setup()
            await web.TCPSite(app, "0.0.0.0", PORT).start()
            self.log(__name__).info(f"🌐 Web server running on port {PORT}")
        except Exception as e:
            self.log(__name__).error(f"❌ Web server failed: {e}")
            raise


    async def start(self, use_qr=False, except_ids=None):
        self.log(__name__).info("🚀 Initializing Luffy File Bot...")
        await super().start()

        try:
            bot_me = await self.get_me()
            self.username = bot_me.username
            self.uptime = datetime.now()
            self.log(__name__).info(f"🤖 Bot @{self.username} authenticated")

            await self._verify_db_channel()
            await self._setup_force_sub_channels()

            asyncio.create_task(self._reset_flood_counts())
            self.log(__name__).info("🔄 Flood control system activated")

            await self._start_web_server()

            self.log(__name__).info(f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃      🏴‍☠️ LUFFY ONLINE      ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃• ID: @{self.username}
┃• Uptime: {self.uptime}
┃• Channels: {len(self.invitelinks)}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛""")

        except Exception as e:
            self.log(__name__).critical(f"🔥 Startup failed: {e}")
            await self.stop()
            raise

    async def stop(self, *args):
        self.log(__name__).info("🛑 Stopping bot gracefully...")
        await super().stop()
        self.log(__name__).info("👋 Bot stopped successfully")


# Global variables
START_TIME = time.time()
bot = Bot()
__all__ = ["Bot", "bot", "START_TIME"]
