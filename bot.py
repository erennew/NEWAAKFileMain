from aiohttp import web
from plugins import web_server
import time

import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime

from config import (
    API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS,
    FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2,
    FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4,
    CHANNEL_ID, PORT
)

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

    async def start(self, use_qr=False, except_ids=None):
        self.LOGGER(__name__).info("🚀 Starting bot initialization...")
        await super().start()
        self.uptime = datetime.now()

        try:
            usr_bot_me = await self.get_me()
            if usr_bot_me is None:
                raise Exception("get_me() returned None. Invalid BOT_TOKEN?")
            self.username = usr_bot_me.username
        except Exception as e:
            self.LOGGER(__name__).error(f"❌ Failed to fetch bot info using get_me(): {e}")
            self.LOGGER(__name__).info("Make sure your TG_BOT_TOKEN is valid and the bot is not blocked.")
            sys.exit()

        # Force Sub Channels
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
                    self.LOGGER(__name__).warning(e)
                    self.LOGGER(__name__).warning(f"Bot can't Export Invite link from Force Sub Channel {idx}!")
                    self.LOGGER(__name__).warning(f"Check the FORCE_SUB_CHANNEL_{idx} value and ensure the bot is admin with Invite Users via Link permission.")
                    self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/weebs_support for support")
                    sys.exit()

        # DB Channel Check
        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id=db_channel.id, text="Test Message")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(f"Check DB Channel (CHANNEL_ID={CHANNEL_ID}) and ensure bot is admin.")
            self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/weebs_support for support")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"Bot Running..!\n\nCreated by \nhttps://t.me/WeekendsBotz")
        self.LOGGER(__name__).info(r"""       
  ┈┈┈╱▔▔▔▔▔▔╲┈╭━━━━━━━╮┈┈
┈┈▕┈╭━╮╭━╮┈▏┃𝕎𝕖𝕖𝕜𝕖𝕟𝕕𝕤𝔹𝕠𝕥𝕫
┈┈▕┈┃╭╯╰╮┃┈▏╰┳━━━━━━╯┈┈
┈┈▕┈╰╯╭╮╰╯┈▏┈┃┈┈┈┈┈
┈┈▕┈┈┈┃┃┈┈┈▏━╯┈┈┈┈┈
┈┈▕┈┈┈╰╯┈┈┈▏┈┈┈┈┈┈┈
┈┈▕╱╲╱╲╱╲╱╲▏┈┈┈┈┈┈┈
        """)

        # Start web server
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")
