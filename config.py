# (©) RaviBots (Originally: WeekendsBotz)
import os
import logging
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

load_dotenv()

# ===== Bot Configuration ===== #
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "7988129609:AAHIJGSZm2-Ryso22AR4X5s05ZF-HaMmfuc")
API_ID = int(os.environ.get("API_ID", 24500584))
API_HASH = os.environ.get("API_HASH", "449da69cf4081dc2cc74eea828d0c490")
OWNER_ID = int(os.environ.get("OWNER_ID", 1047253913))

# ===== Database Configuration ===== #
DB_CHANNEL = int(os.environ.get("DB_CHANNEL", -1002448203068))
DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://chattaravikiran2001:6nJQC6pb3wLf1zCu@cluster1.daxfzgr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1")
DB_NAME = os.environ.get("DATABASE_NAME", "Cluster1")

# ===== Force Subscription Settings ===== #
JOIN_REQUEST_ENABLE = os.environ.get("JOIN_REQUEST_ENABLED", "False").lower() == "True"

FORCE_SUB_CHANNEL_1 = int(os.environ.get("FORCE_SUB_CHANNEL_1", -1002650862527))
FORCE_SUB_CHANNEL_2 = int(os.environ.get("FORCE_SUB_CHANNEL_2", -1002331321194))
FORCE_SUB_CHANNEL_3 = int(os.environ.get("FORCE_SUB_CHANNEL_3", -1001956677010))
FORCE_SUB_CHANNEL_4 = int(os.environ.get("FORCE_SUB_CHANNEL_4", -1002508438247))

# ===== Bot Performance Settings ===== #
TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", 4))
PORT = int(os.environ.get("PORT", 8080))  # fallback to 8000 if PORT not set

# ===== Rate Limiting Configuration ===== #
TIME_WINDOW = int(os.getenv("TIME_WINDOW", 60))
MAX_REQUESTS = int(os.getenv("MAX_REQUESTS", 5))
GLOBAL_REQUESTS = int(os.getenv("GLOBAL_REQUESTS", 30))
GLOBAL_TIME_WINDOW = int(os.getenv("GLOBAL_TIME_WINDOW", 60))
USER_REQUESTS = int(os.getenv("USER_REQUESTS", 3))

# ===== Flood Control Settings ===== #
FLOOD_MAX_REQUESTS = int(os.getenv("FLOOD_MAX_REQUESTS", 5))
FLOOD_TIME_WINDOW = int(os.getenv("FLOOD_TIME_WINDOW", 10))
FLOOD_COOLDOWN = int(os.getenv("FLOOD_COOLDOWN", 30))
SOFT_THROTTLE_WINDOW = int(os.environ.get("SOFT_THROTTLE_WINDOW", 10))
# ===== Boot Animation Settings ===== #
BOOT_DELAY = float(os.getenv("BOOT_DELAY", 0.8))
MIN_BOOT_STEPS = int(os.getenv("MIN_BOOT_STEPS", 3))

# ===== Message Configurations ===== #
START_PIC = os.environ.get("START_PIC", "")
START_MSG = os.environ.get("START_MESSAGE", 
    "👒 Oi oi, {mention}!\n\n""<blockquote>LUFFY here! Got a secret map from @CulturedTeluguweeb? I'll grab that anime treasure faster than Sanji serves dinner! 🍜🏴‍☠️</blockquote>"
)

FORCE_PIC = os.environ.get("FORCE_PIC", "")
FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", 
    "ᴀʀᴀ ᴀʀᴀ!! {mention}\n\n""<b><blockquote>ᴀʀᴀ ʏᴏᴜ'ʀᴇ ᴍɪssɪɴɢ ᴏᴜᴛ ᴏɴ sᴏᴍᴇ sᴇʀɪᴏᴜs ᴀᴄᴛɪᴏɴ. ᴛo ᴜɴʟᴏᴄᴋ ᴀʟʟ ғᴇᴀᴛᴜʀᴇs ᴀɴᴅ ᴀᴄᴄᴇss ғɪʟᴇs, ᴊᴏɪɴ ᴀʟʟ ᴏғ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ʙᴇʟᴏᴡ:!</blockquote></b>"
)

CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", "")

# ===== Media Settings ===== #
PICS = [pic for pic in os.environ.get(
    "PICS", 
    "https://envs.sh/sJX.jpg https://envs.sh/Uc0.jpg https://envs.sh/UkA.jpg https://envs.sh/Uk_.jpg https://envs.sh/Ukc.jpg https://envs.sh/UkZ.jpg https://envs.sh/UkK.jpg"
).split() if pic]

PROTECT_CONTENT = os.environ.get('PROTECT_CONTENT', "True") == "True"
DISABLE_CHANNEL_BUTTON = os.environ.get("DISABLE_CHANNEL_BUTTON", "False") == "True"

# ===== Auto Delete Settings ===== #
AUTO_DELETE_TIME = int(os.getenv("AUTO_DELETE_TIME", 900))
AUTO_CLEAN = os.getenv("AUTO_CLEAN", "False").lower() == "true"
DELETE_DELAY = int(os.getenv("DELETE_DELAY", 10))

# Human-readable format
minutes, seconds = divmod(AUTO_DELETE_TIME, 60)
AUTO_DELETE_HUMAN = (
    f"{minutes} minute{'s' if minutes != 1 else ''} "
    f"{seconds} second{'s' if seconds != 1 else ''}"
    if minutes > 0 
    else f"{seconds} second{'s' if seconds != 1 else ''}"
)

AUTO_DELETE_MSG = os.environ.get(
    "AUTO_DELETE_MSG",
    f"⚠️ Dᴜᴇ ᴛᴏ Cᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs....\n\n"
    f"<blockquote>This file won't stay long! You've got {AUTO_DELETE_HUMAN} before I throw it overboard!🏴‍☠️. "
    f"Please ensure you have saved any necessary content before this time.</blockquote>"
)

AUTO_DEL_SUCCESS_MSG = os.environ.get(
    "AUTO_DEL_SUCCESS_MSG",
    "⚡ Straw Hat LUFFY reporting:\nFile deleted with a Gomu Gomu no Slam! 💥🌀🗑️\nCatch ya later, nakama! 👒🏴‍☠️"
)

# ===== Text Templates ===== #
BOT_STATS_TEXT = "<b><blockquote>BOT UPTIME</b>\n{uptime}</blockquote>"
USER_REPLY_TEXT = "<blockquote>💖 I'm loyal to one place—@CulturedTeluguweeb! That's where my real journey begins. For anyone else... sorry, no adventure! 👒</blockquote>"

# ===== Admin Configuration ===== #
try:
    ADMINS = [int(x) for x in os.environ.get("ADMINS", "").split() if x]
except ValueError:
    raise Exception("Your Admins list does not contain valid integers.")

ADMINS.extend([OWNER_ID])

# ===== Logging Configuration ===== #
LOG_FILE_NAME = "filesharingbot.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50_000_000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)

# ===== Validation Checks ===== #
if not TG_BOT_TOKEN:
    raise ValueError("TG_BOT_TOKEN environment variable is required!")

if not all([API_ID, API_HASH]):
    raise ValueError("API_ID and API_HASH environment variables are required!")

if not DB_CHANNEL:
    raise ValueError("DB_CHANNEL environment variable is required!")
