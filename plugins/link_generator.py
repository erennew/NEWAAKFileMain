# (©) WeekendsBotz - Luffy Edition v2.0
import random
import time
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, RPCError
from config import ADMINS, DB_CHANNEL, API_ID, API_HASH, TG_BOT_TOKEN

# Set up crash-resistant logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("luffy_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Luffy Boot Animations
BOOT_SEQUENCES = [
    [
        "🌀 Booting Gear 2...",
        "💥 Steam surging through veins...",
        "⚡ Activating Jet Pistol!",
        "🔥 LUFFY IS READY!!"
    ],
    [
        "⚙️ Initializing Gear 4...",
        "💪 Inflating muscles...",
        "🔒 Activating Boundman mode!",
        "🦾 LUFFY IS PUMPED!!"
    ],
    [
        "🌪️ Entering Gear 5...",
        "🎨 Bending reality...",
        "👑 Becoming the Warrior of Liberation...",
        "💫 LUFFY IS IN GOD MODE!!"
    ]
]

class LuffyBot(Client):
    def __init__(self):
        super().__init__(
            "WeekendsBotz",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=200,
            max_concurrent_transmissions=5
        )
        self.db_channel = None
        self._boot_anim = random.choice(BOOT_SEQUENCES)

    async def _animate_boot(self):
        """Show random Luffy boot sequence"""
        for step in self._boot_anim:
            logger.info(step)
            await asyncio.sleep(1.5)

    async def _safety_checks(self):
        """Anti-crash system checks"""
        checks = {
            "DB Channel": lambda: self.db_channel.id if self.db_channel else None,
            "Admins": lambda: ADMINS[0] if ADMINS else None,
            "Bot Token": lambda: self.bot_token[:5] + "..." if self.bot_token else None
        }
        
        for check_name, check_func in checks.items():
            try:
                if not check_func():
                    raise RuntimeError(f"{check_name} check failed!")
                logger.info(f"✅ {check_name} check passed")
            except Exception as e:
                logger.critical(f"❌ {check_name} validation failed: {e}")
                return False
        return True

    async def start(self):
        """Crash-resistant startup"""
        try:
            await self._animate_boot()
            
            await super().start()
            self.db_channel = await self.get_chat(DB_CHANNEL)
            
            if not await self._safety_checks():
                raise RuntimeError("Critical checks failed")
            
            me = await self.get_me()
            logger.info(f"👑 {me.first_name} is now King of the Bots!")
            
            # Load handlers
            self.setup_handlers()
            
            # Keep alive
            while True:
                await asyncio.sleep(3600)
                
        except FloodWait as e:
            logger.warning(f"⏳ Flood control: Sleeping for {e.value}s")
            await asyncio.sleep(e.value)
        except RPCError as e:
            logger.critical(f"☠️ RPC Error: {e}")
        finally:
            if self.is_initialized:
                await self.stop()

    def setup_handlers(self):
        """All message handlers"""
        @self.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
        async def batch_handler(client: Client, message: Message):
            """Fixed batch link generator"""
            try:
                # Get first message
                first = await client.ask(
                    chat_id=message.from_user.id,
                    text="📥 Forward FIRST message from DB channel",
                    timeout=60
                )
                f_msg_id = first.forward_from_message_id or int(first.text.split("/")[-1])
                
                # Get last message
                last = await client.ask(
                    chat_id=message.from_user.id,
                    text="📤 Forward LAST message from DB channel",
                    timeout=60
                )
                s_msg_id = last.forward_from_message_id or int(last.text.split("/")[-1])
                
                # Generate batch link
                batch_link = f"https://t.me/{client.username}?start=batch_{f_msg_id}_{s_msg_id}"
                
                await last.reply(
                    f"🔗 Batch Link:\n`{batch_link}`",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("Share", url=f"https://t.me/share/url?url={batch_link}")
                    ]])
                )
                
            except Exception as e:
                logger.error(f"Batch error: {e}")
                await message.reply("❌ Failed! Check logs.")

        @self.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
        async def genlink_handler(client: Client, message: Message):
            """Single link generator"""
            try:
                msg = await client.ask(
                    chat_id=message.from_user.id,
                    text="📨 Forward message from DB channel",
                    timeout=30
                )
                msg_id = msg.forward_from_message_id or int(msg.text.split("/")[-1])
                
                file_link = f"https://t.me/{client.username}?start=file_{msg_id}"
                
                await msg.reply(
                    f"📤 File Link:\n`{file_link}`",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("Share", url=f"https://t.me/share/url?url={file_link}")
                    ]])
                )
            except Exception as e:
                logger.error(f"Genlink error: {e}")
                await message.reply("💥 Failed! Check logs.")

if __name__ == "__main__":
    bot = LuffyBot()
    asyncio.run(bot.start())
