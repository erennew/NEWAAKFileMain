#(©) WeekendsBotz

import os
import logging
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

load_dotenv()

#Bot token @Botfather
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "7378354734:AAGb8dZm_Ref8Ln3brARcwrllIkZwWgJMhM")

#Your API ID from my.telegram.org
APP_ID = int(os.environ.get("APP_ID", "28744454"))

#Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "debd37cef0ad1a1ce45d0be8e8c3c5e7")

#Your db channel Id
DB_CHANNEL = int(os.environ.get("DB_CHANNEL", "-1002437344784"))

#OWNER ID
OWNER_ID = int(os.environ.get("OWNER_ID", "6266529037"))

#Port
PORT = os.environ.get("PORT", "8080")

#Database 
DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://jeffreymosesdj:Jeffrey@cluster2.cuiux.mongodb.net/?retryWrites=true&w=majority")
DB_NAME = os.environ.get("DATABASE_NAME", "Cluster2")


JOIN_REQUEST_ENABLE = os.environ.get("JOIN_REQUEST_ENABLED", None)
#force sub channel id, if you want enable force sub
FORCE_SUB_CHANNEL_1 = int(os.environ.get("FORCE_SUB_CHANNEL_1", "-1002076655534"))
FORCE_SUB_CHANNEL_2 = int(os.environ.get("FORCE_SUB_CHANNEL_2", "-1002369384920"))
FORCE_SUB_CHANNEL_3 = int(os.environ.get("FORCE_SUB_CHANNEL_3", "-1002172787340"))
FORCE_SUB_CHANNEL_4 = int(os.environ.get("FORCE_SUB_CHANNEL_4", "-1002244170363"))

TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "4"))

#start message
START_PIC = os.environ.get("START_PIC","https://envs.sh/nA8.jpg")
START_MSG = os.environ.get("START_MESSAGE", "ᴋᴏɴɪᴄʜɪᴡᴀ {mention}\n\n<blockquote>ᴋᴏɴɪᴄʜɪᴡᴀ ɪ ᴄᴀɴ sᴛᴏʀᴇ ᴀɴɪᴍᴇ/ᴍᴏᴠɪᴇ ғɪʟᴇs ɪɴ @Anime_Weekends ᴄʜᴀɴɴᴇʟ  ᴀɴᴅ ᴏᴛʜᴇʀ ᴜsᴇʀs ᴄᴀɴ ᴀᴄᴄᴇss ɪᴛ ғʀᴏᴍ sᴘᴇᴄɪᴀʟ ʟɪɴᴋ.</blockquote>")
try:
    ADMINS=[]
    for x in (os.environ.get("ADMINS", "6429532957 6266529037").split()):
        ADMINS.append(int(x))
except ValueError:
        raise Exception("Your Admins list does not contain valid integers.")

#Force sub message 
FORCE_PIC = os.environ.get("FORCE_PIC", "https://envs.sh/KTy.jpg")

FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "ᴀʀᴀ ᴀʀᴀ!! {mention}\n\n<b><blockquote>ᴀʀᴀ ʏᴏᴜ'ʀᴇ ᴍɪssɪɴɢ ᴏᴜᴛ ᴏɴ sᴏᴍᴇ sᴇʀɪᴏᴜs ᴀᴄᴛɪᴏɴ.ᴛo ᴜɴʟᴏᴄᴋ ᴀʟʟ ғᴇᴀᴛᴜʀᴇs ᴀɴᴅ ᴀᴄᴄᴇss ғɪʟᴇs, ᴊᴏɪɴ ᴀʟʟ of ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ʙᴇʟᴏᴡ: !</blockquote></b>")

#set your Custom Caption here, Keep None for Disable Custom Caption
CUSTOM_CAPTION = os.environ.get("@Ongoing_Weekends")

#set True if you want to prevent users from forwarding files from bot
PROTECT_CONTENT = True if os.environ.get('PROTECT_CONTENT', "False") == "True" else False

# Auto delete time in seconds.
AUTO_DELETE_TIME = int(os.getenv("AUTO_DELETE_TIME", "600"))
AUTO_DELETE_MSG = os.environ.get("AUTO_DELETE_MSG", "⚠️ Dᴜᴇ ᴛᴏ Cᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs....\n\n<blockquote>This file will be automatically deleted in {time} seconds. Please ensure you have saved any necessary content before this time.</blockquote>")
AUTO_DEL_SUCCESS_MSG = os.environ.get("AUTO_DEL_SUCCESS_MSG", "<blockquote>уσυя fιℓє нαѕ вєєи ѕυccєѕѕfυℓℓу ∂єℓєтє∂! ♻️</blockquote>")

#Set true if you want Disable your Channel Posts Share button
DISABLE_CHANNEL_BUTTON = os.environ.get("DISABLE_CHANNEL_BUTTON", None) == 'True'

BOT_STATS_TEXT = "<b><blockquote>BOT UPTIME</b>\n{uptime}</blockquote>"
USER_REPLY_TEXT = "<blockquote>ᴀʀᴀ!! ᴀʀᴀ!! ɪᴀᴍ ᴏɴʟʏ ᴡᴏʀᴋ ғᴏʀ ᴍʏ ʟᴏᴠᴇʟʏ ᴋᴀᴡᴀɪɪ 🥰 @JeffreySama !</blockquote>"
WAIT_MSG = os.environ.get(
    "WAIT_MSG",
    "🧮 Luffy's counting the pirate crew... Hold tight, nakama! ⏳"
)

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
