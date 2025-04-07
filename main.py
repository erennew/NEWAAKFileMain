# (©) WeekendsBotz
import asyncio
import logging
import sys
from bot import Bot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

LOGGER = logging.getLogger(__name__)

async def main():
    try:
        await bot.start()
        LOGGER.info("💫 Bot started successfully. Awaiting tasks...")

        await idle()  # Keeps the bot running
    except (KeyboardInterrupt, SystemExit):
        LOGGER.warning("🧨 Interrupted! Shutting down...")
    finally:
        await bot.stop()
        LOGGER.info("✅ Bot stopped. See ya, captain!")

def idle():
    """Idle loop to keep bot running."""
    loop = asyncio.get_event_loop()
    stop = loop.create_future()

    def shutdown():
        if not stop.done():
            stop.set_result(None)

    for signal_name in ('SIGINT', 'SIGTERM'):
        try:
            loop.add_signal_handler(getattr(signal, signal_name), shutdown)
        except (AttributeError, NotImplementedError):
            # Windows compatibility fallback
            pass

    return stop

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        LOGGER.critical(f"🔥 Fatal Error: {e}", exc_info=True)
