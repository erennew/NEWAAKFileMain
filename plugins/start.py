import os
import time
import asyncio
import random
import contextlib
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from bot import Bot
PICS = (os.environ.get("PICS", "https://i.ibb.co/Kx5mS6V5/x.jpg https://i.ibb.co/jZQHRzKv/x.jpg https://i.ibb.co/PvB2DVHQ/x.jpg https://i.ibb.co/cSYRkdz6/x.jpg https://i.ibb.co/FjwYKW9/x.jpg")).split()
from config import MAX_REQUESTS, TIME_WINDOW
from config import ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, START_PIC, FORCE_PIC, AUTO_DELETE_TIME, AUTO_DELETE_MSG, JOIN_REQUEST_ENABLE, FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4
from helper_func import subscribed, decode, get_messages, delete_file
from database.database import add_user, del_user, full_userbase, present_user
from helper_func import is_user_limited
from config import START_TEXT
async def create_invite_links(client: Client):
    invite1 = await client.create_chat_invite_link(
        chat_id=FORCE_SUB_CHANNEL_1,
        creates_join_request=True
    )
    invite2 = await client.create_chat_invite_link(
        chat_id=FORCE_SUB_CHANNEL_2,
        creates_join_request=True
    )
    invite3 = await client.create_chat_invite_link(
        chat_id=FORCE_SUB_CHANNEL_3,
        creates_join_request=True
    )
    invite4 = await client.create_chat_invite_link(
        chat_id=FORCE_SUB_CHANNEL_4,
        creates_join_request=True
    )
    return invite1, invite2, invite3, invite4


user_rate_limit = {}

@Bot.on_message(filters.command("start") & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    if not await present_user(user_id):
        try:
            await add_user(user_id)
        except:
            pass
	    # 🧃 Check rate limit
    if is_user_limited(id):
        return await reply_with_clean("Too many requests! Please wait a bit ⏳")

    # Your normal start command logic
    return await reply_with_clean(START_TEXT.format(message.from_user.first_name))
    hour = datetime.now().hour
    if hour >= 22 or hour < 6:
        await reply_with_clean("🌙 Ara Ara~ It’s sleepy hours, but LUFFY's still awake to guard your files! 🛌👒")
	
    # Rate limit check
    now = time.time()
    reqs = user_rate_limit.get(id, [])
    reqs = [t for t in reqs if now - t < TIME_WINDOW]
    if len(reqs) >= MAX_REQUESTS:
        wait_time = int(TIME_WINDOW - (now - reqs[0]))
        await reply_with_clean(f"⚠️ Slow down, nakama! You're too fast for LUFFY! Wait a bit and try again~ 💤\n\nTry again in <b>{wait_time}</b> seconds. 🐢")
	

    reqs.append(now)
    user_rate_limit[id] = reqs

    # Boot animation setup
  #  progress = await message.reply("👒 Booting LUFFY File Core...")

    boot_sequences = [
    [
        "🧭 Setting Sail from East Blue...",
        "🔍 Scouting the Grand Line routes...",
        "🏴‍☠️ Crew check done! Straw Hat systems online!",
        "✅ LUFFY IS READY FOR ADVENTURE! ☠️"
    ],
    [
        "⚙️ Activating Gear 2...",
        "💨 Speeding up Straw Hat Systems...",
        "✅ LUFFY READY TO FIGHT! 💥"
    ],

    [
        "⚙️ Gear 4: Boundman Engaged...",
        "🔄 Recoil Boost Active...",
        "✅ LET'S GO, CREW! 🔥"
    ],
    [
        "⚙️ Gear 5: Nika Mode Loading...",
        "🌟 Drums of Liberation echo...",
        "✅ LUFFY IS IN FULL SWING! 🌀"
    ],
    [
        "🌊 Calling Thousand Sunny...",
        "🎩 Checking Straw Hat integrity...",
        "✅ LUFFY CREW DEPLOYED! 💫"
    ],
    [
        "⚓ Deploying haki across channels...",
        "🌀 Summoning LUFFY clones...",
        "✅ SHISHISHI~ Let's make some trouble! 😎"
    ],
    [
        "🔧 FRANKY’s loading Cola Energy...",
        "🚀 Docking LUFFY-Bot Systems...",
        "✅ SUPER BOOT COMPLETE! 🤖"
    ],
    [
        "🔥 SANJI’s Kitchen Prepping...",
        "🥘 Diable Jambe Cooking in Progress...",
        "✅ STRAW HATS FED AND READY! 🍖"
    ],
    [
        "🗡️ ZORO is sharpening his blades...",
        "🌪️ Santoryu Mode Activated...",
        "✅ NO ONE GETS LOST THIS TIME! 😤"
    ]
]



    steps = random.choice(boot_sequences)

    # Send the initial boot message
    try:
        progress = await message.reply("👒 Booting LUFFY File Core...")
    except Exception as e:
        print(f"Error sending boot message: {e}")
        return  # Stop execution if message fails

    # Loop through each step safely
    for step in steps:
        await asyncio.sleep(random.uniform(0.5, 1.2))
        with contextlib.suppress(Exception):
            await progress.edit(step)

    # Try to delete the boot message safely
    await asyncio.sleep(0.5)
    with contextlib.suppress(Exception):
        await progress.delete()

    # Handle any arguments from /start
    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
        except:
            return
        string = await decode(base64_string)
        argument = string.split("-")

        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except:
                return
            if start <= end:
                ids = range(start, end + 1)
            else:
                ids = []
                i = start
                while True:
                    ids.append(i)
                    i -= 1
                    if i < end:
                        break
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except:
                return
        else:
            return

        # Let user know it's processing
        temp_msg = await message.reply("<blockquote>⚡ Ara~ Getting your file ready... Hold tight!</blockquote>")

        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("<blockquote>😵‍💫 Something went wrong while fetching your files!</blockquote>")
            return

        await temp_msg.delete()
        track_msgs = []


        for msg in messages:
            caption = CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html,
                                            filename=msg.document.file_name) if bool(CUSTOM_CAPTION) and msg.document else (msg.caption.html if msg.caption else "")

            reply_markup = None if not DISABLE_CHANNEL_BUTTON else msg.reply_markup

            try:
                copied_msg = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    protect_content=PROTECT_CONTENT
                )
                if AUTO_DELETE_TIME and AUTO_DELETE_TIME > 0:
                    track_msgs.append(copied_msg)
                await asyncio.sleep(0.5)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                copied_msg = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    protect_content=PROTECT_CONTENT
                )
                if AUTO_DELETE_TIME and AUTO_DELETE_TIME > 0:
                    track_msgs.append(copied_msg)

        if track_msgs:
            delete_data = await client.send_message(
                chat_id=message.from_user.id,
                text=AUTO_DELETE_MSG.format(time=AUTO_DELETE_TIME // 60)
            )
            asyncio.create_task(delete_file(track_msgs, client, delete_data))
        return

    # No encoded file - show greeting UI
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📜 Pirate Log", callback_data="about"),
                InlineKeyboardButton("🗺️ Close Map", callback_data="close")
            ]
        ]
    )

    if START_PIC:
        try:
            reply = await message.reply_photo(
                photo=random.choice(PICS),
                caption=START_MSG.format(
                    first=message.from_user.first_name,
                    last=message.from_user.last_name,
                    username=None if not message.from_user.username else '@' + message.from_user.username,
                    mention=message.from_user.mention,
                    id=message.from_user.id
                ),
                reply_markup=reply_markup,
                quote=True
            )
            await auto_delete(reply, message)
        except Exception as e:
            print(f"Error replying with photo: {e}")
            await message.reply_text("Sorry, there was an issue with the photo.")
    else:
        await message.reply_text(
            text=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            quote=True
        )



# =====================================================================================##

#WAIT_MSG = """<b><blockquote>I will buy you a lollypop Be patient ...</blockquote></b>"""
#import random

WAIT_MESSAGES = [
    "☠️ Yo! Luffy here! Hold on tight and <b>wait a sec</b>, the adventure’s loading... 🍖",
    "🌀 GEAR 2... ACTIVATING! Give me a moment, nakama! Just <b>wait a little</b>! 💨",
    "🍖 <b>Wait up!</b> Meat first, files later! I'm grabbing it for ya!",
    "⚓ Just <b>wait for it</b>—we're hoisting the sail! Captain Luffy’s on it! ☀️",
    "🔥 Gear 5 Vibes Loading... <b>Wait right there</b>, this’ll be legendary! 💥",
    "💬 Zoro got lost again... So while he’s wandering, <b>you wait</b>, I’m fetching your stuff! 🗺️",
    "🎩 Hold onto your hat! I’m stretching to grab your request! Just <b>wait a sec</b>! 🏴‍☠️",
    "⏳ <b>Wait patiently!</b> This will be faster than Sanji kickin’ someone for disrespectin' Nami! 💨"
]

def get_wait_msg():
    return f"<blockquote>{random.choice(WAIT_MESSAGES)}</blockquote>"

REPLY_ERROR = """<code>Use this command as a replay to any telegram message with out any spaces.</code>"""

# =====================================================================================##

@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    # Create invite links before using them
    invite1, invite2, invite3, invite4 = await create_invite_links(client)

    buttons = [
        [
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=invite1.invite_link),
            InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=invite2.invite_link),
        ],
        [
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=invite3.invite_link),
            InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=invite4.invite_link),
        ]
    ]
    try:
        buttons.append(
            [
                InlineKeyboardButton(
                    text='• ɴᴏᴡ ᴄʟɪᴄᴋ ʜᴇʀᴇ •',
                    url=f"https://t.me/{client.username}?start={message.command[1]}"
                )
            ]
        )
    except IndexError:
        pass


    if FORCE_PIC:  # Check if FORCE_PIC has a value
        await message.reply_photo(
            photo = random.choice(PICS),
            caption = START_MSG.format(
                first = message.from_user.first_name,
                last = message.from_user.last_name,
                username = None if not message.from_user.username else '@' + message.from_user.username,
                mention = message.from_user.mention,
                id = message.from_user.id
            ),
            reply_markup =InlineKeyboardMarkup(buttons),
	      #  message_effect_id=5104841245755180586, #🔥
	    	quote=True
        )
    else:
        await message.reply(
            text=FORCE_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True,
            disable_web_page_preview=True
        )


@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=get_wait_msg())
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0

        pls_wait = await reply_with_clean("<i><blockquote>Broadcasting Message.. This will Take Some Time</blockquote></i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
            total += 1

        status = f"""<b><u><blockquote>Broadcast Completed</blockquote></u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""

        return await pls_wait.edit(status)

    else:
        msg = await reply_with_clean(message,REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()
# 🧹 Auto delete helper
async def auto_delete(msg, user_msg=None):
    from config import AUTO_CLEAN, DELETE_DELAY
    import asyncio
    if AUTO_CLEAN:
        await asyncio.sleep(DELETE_DELAY)
        try:
            await msg.delete()
            if user_msg:
                await user_msg.delete()
        except:
            pass

# Global reply function with auto-clean
async def reply_with_clean(message, text, **kwargs):
    reply = await message.reply(text, **kwargs)
    await auto_delete(reply, message)
    return reply
