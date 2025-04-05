#(©) WeekendsBotz

import os
import logging
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

load_dotenv()

#Bot token @Botfather
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "7988129609:AAHIJGSZm2-Ryso22AR4X5s05ZF-HaMmfuc")

#Your API ID from my.telegram.org
APP_ID = int(os.environ.get("APP_ID", "24500584"))

#Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "449da69cf4081dc2cc74eea828d0c490")

#Your db channel Id
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1002448203068"))

#OWNER ID
OWNER_ID = int(os.environ.get("OWNER_ID", "1047253913"))

#Port
PORT = os.environ.get("PORT", "8080")

#Database 
DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://chattaravikiran2001:6nJQC6pb3wLf1zCu@cluster1.daxfzgr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1")
DB_NAME = os.environ.get("DATABASE_NAME", "Cluster1")


JOIN_REQUEST_ENABLE = os.environ.get("JOIN_REQUEST_ENABLED", None)
#force sub channel id, if you want enable force sub
FORCE_SUB_CHANNEL_1 = int(os.environ.get("FORCE_SUB_CHANNEL_1", "-1002650862527"))
FORCE_SUB_CHANNEL_2 = int(os.environ.get("FORCE_SUB_CHANNEL_2", "-1002331321194"))
FORCE_SUB_CHANNEL_3 = int(os.environ.get("FORCE_SUB_CHANNEL_3", "-1001956677010"))
FORCE_SUB_CHANNEL_4 = int(os.environ.get("FORCE_SUB_CHANNEL_4", "-1002508438247"))

TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "4"))
TIME_WINDOW = int(os.getenv("TIME_WINDOW", 60))  # e.g. 60 seconds
MAX_REQUESTS = int(os.getenv("MAX_REQUESTS", 5))  # e.g. 3 requests per TIME_WINDOW

#start message
START_PIC = os.environ.get("START_PIC","")
START_MSG = os.environ.get(
    "START_MESSAGE",
    "👒 Oi oi, {mention}!\n\n<blockquote>LUFFY here! Got a secret map from @CulturedTeluguweeb? I’ll grab that anime treasure faster than Sanji serves dinner! 🍜🏴‍☠️</blockquote>"
)
try:
    ADMINS=[]
    for x in (os.environ.get("ADMINS", " ").split()):
        ADMINS.append(int(x))
except ValueError:
        raise Exception("Your Admins list does not contain valid integers.")

#Force sub message 
FORCE_PIC = os.environ.get("FORCE_PIC", "")

FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "ᴀʀᴀ ᴀʀᴀ!! {mention}\n\n<b><blockquote>ᴀʀᴀ ʏᴏᴜ'ʀᴇ ᴍɪssɪɴɢ ᴏᴜᴛ ᴏɴ sᴏᴍᴇ sᴇʀɪᴏᴜs ᴀᴄᴛɪᴏɴ.ᴛo ᴜɴʟᴏᴄᴋ ᴀʟʟ ғᴇᴀᴛᴜʀᴇs ᴀɴᴅ ᴀᴄᴄᴇss ғɪʟᴇs, ᴊᴏɪɴ ᴀʟʟ of ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ʙᴇʟᴏᴡ: !</blockquote></b>")

#set your Custom Caption here, Keep None for Disable Custom Caption
CUSTOM_CAPTION = os.environ.get("")

#Collection of pics for Bot // #Optional but atleast one pic link should be replaced if you don't want predefined links
PICS = (os.environ.get("PICS", "https://envs.sh/sJX.jpg https://envs.sh/Uc0.jpg https://envs.sh/UkA.jpg https://envs.sh/Uk_.jpg https://envs.sh/Ukc.jpg https://envs.sh/UkZ.jpg https://envs.sh/UkK.jpg")).split() #Required
#set True if you want to prevent users from forwarding files from bot
PROTECT_CONTENT = False if os.environ.get('PROTECT_CONTENT', "True") == "True" else False

# Auto delete time in seconds.
# Auto delete time set to 15 minutes (900 seconds)
AUTO_DELETE_TIME = int(os.getenv("AUTO_DELETE_TIME", "900"))

# Convert to human-readable format
minutes = AUTO_DELETE_TIME // 60
seconds = AUTO_DELETE_TIME % 60

if minutes > 0:
    AUTO_DELETE_HUMAN = f"{minutes} minute{'s' if minutes != 1 else ''} {seconds} second{'s' if seconds != 1 else ''}"
else:
    AUTO_DELETE_HUMAN = f"{seconds} second{'s' if seconds != 1 else ''}"

# Message shown before auto-deletion
AUTO_DELETE_MSG = os.environ.get(
    "AUTO_DELETE_MSG",
    f"⚠️ Dᴜᴇ ᴛᴏ Cᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs....\n\n"
    f"<blockquote>This file won’t stay long! You’ve got {AUTO_DELETE_HUMAN} before I throw it overboard!🏴‍☠️. "
    f"Please ensure you have saved any necessary content before this time.</blockquote>"
)

# Message shown after deletion
AUTO_DEL_SUCCESS_MSG = os.environ.get(
    "AUTO_DEL_SUCCESS_MSG",
    "<blockquote>⚡ Straw Hat LUFFY reporting: File deleted with a Gomu Gomu no Slam! Catch ya later! ♻️</blockquote>"
)


#Set true if you want Disable your Channel Posts Share button
DISABLE_CHANNEL_BUTTON = os.environ.get("DISABLE_CHANNEL_BUTTON", None) == 'False'

BOT_STATS_TEXT = "<b><blockquote>BOT UPTIME</b>\n{uptime}</blockquote>"
USER_REPLY_TEXT = "<blockquote>💖 I’m loyal to one place—@CulturedTeluguweeb! That’s where my real journey begins. For anyone else... sorry, no adventure! 👒</blockquote>"


ADMINS.append(OWNER_ID)
ADMINS.append(6266529037)

LOG_FILE_NAME = "filesharingbot.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
