import os
import time
import asyncio
import random
import contextlib
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from pyrogram.errors import FloodWait

from bot import Bot
from config import (
    GLOBAL_REQUESTS, GLOBAL_TIME_WINDOW, MAX_REQUESTS, TIME_WINDOW,
    ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON,
    PROTECT_CONTENT, START_PIC, FORCE_PIC, AUTO_DELETE_TIME, AUTO_DELETE_MSG,
    JOIN_REQUEST_ENABLE, FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2,
    FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4, DB_CHANNEL
)
from helper_func import subscribed, decode, get_messages, delete_file
from database.database import add_user, present_user

PICS = os.environ.get("PICS", "").split() or [
    "https://i.ibb.co/Kx5mS6V5/x.jpg",
    "https://i.ibb.co/jZQHRzKv/x.jpg",
    "https://i.ibb.co/PvB2DVHQ/x.jpg",
    "https://i.ibb.co/cSYRkdz6/x.jpg",
    "https://i.ibb.co/FjwYKW9/x.jpg"
]

# Boot animations
boot_sequences = [
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
    ],
    [
        "🏴‍☠️ Setting sail...",
        "🗺️ Reading Grand Line coordinates...",
        "🍖 Grabbing meat for the journey...",
        "☠️ LUFFY'S CREW IS READY!!"
    ],
    [
        "🔄 Syncing Haki...",
        "💥 Charging Conqueror's Spirit...",
        "👒 Placing the Straw Hat...",
        "🔥 PIRATE KING MODE: ON!!"
    ]
]

# Flood warning animations
FLOOD_SEQUENCES = [
    [
        "⚠️ Whoa there, sailor!",
        "🌊 You're sending too many requests.",
        "🛑 Slow down before the ship sinks!"
    ],
    [
        "💢 Steam overflowing!",
        "🌀 Gear system overheating...",
        "🥵 Cool down before another command!"
    ],
    [
        "🔥 Too hot to handle!",
        "🔒 Temporarily locked due to spamming.",
        "⏳ Try again in a bit, Captain!"
    ]
]

user_rate_limit = {}
FLOOD_COOLDOWN = 30

# Soft rate limit (per user)
async def is_soft_limited(user_id: int):
    now = time.time()
    limit_data = user_rate_limit.setdefault(user_id, {"timestamps": []})
    limit_data["timestamps"] = [t for t in limit_data["timestamps"] if now - t < TIME_WINDOW]

    if len(limit_data["timestamps"]) >= MAX_REQUESTS:
        return True

    limit_data["timestamps"].append(now)
    return False

# Hard flood control
async def check_flood(user_id: int):
    now = time.time()
    user_data = user_rate_limit.setdefault(user_id, {"timestamps": [], "warn_level": 0})
    user_data["timestamps"] = [t for t in user_data["timestamps"] if now - t < 10]

    if len(user_data["timestamps"]) >= 10:
        user_data["warn_level"] = 2
        return True, 2
    elif len(user_data["timestamps"]) >= 5:
        user_data["warn_level"] = 1
        return True, 1

    user_data["timestamps"].append(now)
    return False, 0

# Create invite links
async def create_invite_links(client: Client):
    links = []
    for channel in [FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4]:
        if channel:
            try:
                links.append(await client.create_chat_invite_link(chat_id=channel, creates_join_request=True))
            except Exception as e:
                print(f"Error creating invite for {channel}: {e}")
    return links

# Auto delete helper
async def auto_delete(msg, user_msg=None):
    if AUTO_DELETE_MSG:
        await asyncio.sleep(AUTO_DELETE_TIME)
        with contextlib.suppress(Exception):
            await msg.delete()
            if user_msg:
                await user_msg.delete()

# Smart reply that auto deletes
async def reply_with_clean(message, text, **kwargs):
    reply = await message.reply(text, **kwargs)
    asyncio.create_task(auto_delete(reply, message))
    return reply

# Main handler
@Bot.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    user_id = message.from_user.id

    if await is_soft_limited(user_id):
        return await reply_with_clean(message, "🍃 Too fast! Please wait a few seconds ⏳")

    is_flooding, level = await check_flood(user_id)
    if is_flooding:
        warning = random.choice(FLOOD_SEQUENCES[min(level, len(FLOOD_SEQUENCES)-1)])
        if level == 2:
            until = int(time.time()) + FLOOD_COOLDOWN
            await client.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=user_id,
                until_date=until,
                permissions=ChatPermissions(can_send_messages=False)
            )
        return await reply_with_clean(message, "\n".join(warning))

    if not await subscribed(client, message):
        invite_links = await create_invite_links(client)
        buttons = []
        for i in range(0, len(invite_links), 2):
            row = [InlineKeyboardButton("• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=invite_links[i].invite_link)]
            if i+1 < len(invite_links):
                row.append(InlineKeyboardButton("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=invite_links[i+1].invite_link))
            buttons.append(row)

        try:
            if len(message.command) > 1:
                payload = message.command[1]
                buttons.append([InlineKeyboardButton(
                    text='• ɴᴏᴡ ᴄʟɪᴄᴋ ʜᴇʀᴇ •',
                    url=f"https://t.me/{client.username}?start={payload}"
                )])
        except IndexError:
            pass

        caption_text = FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=f"@{message.from_user.username}" if message.from_user.username else None,
            mention=message.from_user.mention,
            id=message.from_user.id
        )
        if FORCE_PIC:
            return await message.reply_photo(
                photo=random.choice(PICS),
                caption=caption_text,
                reply_markup=InlineKeyboardMarkup(buttons),
                quote=True
            )
        else:
            return await message.reply(
                text=caption_text,
                reply_markup=InlineKeyboardMarkup(buttons),
                quote=True
            )

    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
            string = await decode(base64_string)
            argument = string.split("-")

            if len(argument) == 3:
                start = int(int(argument[1]) / abs(DB_CHANNEL))
                end = int(int(argument[2]) / abs(DB_CHANNEL))
                ids = range(start, end + 1) if start <= end else list(range(start, end - 1, -1))
            elif len(argument) == 2:
                ids = [int(int(argument[1]) / abs(DB_CHANNEL))]
            else:
                return await message.reply("⚠️ Invalid file link format")

            boot_msg = await message.reply("🚢 Starting system check...")
            for line in random.choice(boot_sequences):
                await asyncio.sleep(1.2)
                await boot_msg.edit(line)
            await asyncio.sleep(0.5)
            await boot_msg.delete()

            temp_msg = await message.reply("<blockquote>⚡ Preparing your files...</blockquote>")
            messages = await get_messages(client, ids)
            await temp_msg.delete()

            track_msgs = []
            for msg in messages:
                if not msg or not msg.document:
                    continue

                caption = CUSTOM_CAPTION.format(
                    previouscaption=msg.caption.html if msg.caption else "",
                    filename=msg.document.file_name
                ) if CUSTOM_CAPTION else (msg.caption.html if msg.caption else "")

                reply_markup = msg.reply_markup if not DISABLE_CHANNEL_BUTTON else None

                try:
                    copied_msg = await msg.copy(
                        chat_id=message.from_user.id,
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                        reply_markup=reply_markup,
                        protect_content=PROTECT_CONTENT
                    )
                    if AUTO_DELETE_TIME > 0:
                        track_msgs.append(copied_msg)
                    else:
                        await asyncio.sleep(0.5)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                except Exception as e:
                    print(f"Error sending file: {e}")
                    await message.reply("⚠️ Failed to send some files. Please try again.")
                    continue

            if track_msgs and AUTO_DELETE_TIME > 0:
                delete_data = await client.send_message(
                    chat_id=message.from_user.id,
                    text=AUTO_DELETE_MSG.format(time=AUTO_DELETE_TIME)
                )
                asyncio.create_task(delete_file(track_msgs, client, delete_data))
            return
        except Exception as e:
            print(f"File link processing error: {e}")
            await message.reply("⚠️ Invalid or broken file link")
            return

    if not await present_user(user_id):
        await add_user(user_id)

    if datetime.now().hour >= 22 or datetime.now().hour < 6:
        reply = await message.reply("🌙 Ara Ara~ It's sleepy hours, but LUFFY's still awake! 🛌👒")
        await asyncio.sleep(AUTO_DELETE_TIME)
        await reply.delete()
        await message.delete()
        return

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("📜 Pirate Log", callback_data="about"),
         InlineKeyboardButton("🗺️ Close Map", callback_data="close")]
    ])

    final_caption = START_MSG.format(
        first=message.from_user.first_name,
        last=message.from_user.last_name,
        username=f"@{message.from_user.username}" if message.from_user.username else None,
        mention=message.from_user.mention,
        id=message.from_user.id
    )

    if START_PIC:
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=final_caption,
            reply_markup=reply_markup,
            quote=True
        )
    else:
        await message.reply_text(
            text=final_caption,
            reply_markup=reply_markup,
            link_preview_options={"is_disabled": True},
            quote=True
        )
