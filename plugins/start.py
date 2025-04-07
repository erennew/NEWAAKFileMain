import os
import time
import asyncio
import random
import contextlib
from datetime import datetime
from helper_func import check_flood
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
    FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4
)
from helper_func import subscribed, decode, get_messages, delete_file, is_user_limited
from database.database import add_user, present_user
from config import DB_CHANNEL
from pyrogram.types import ChatPermissions

PICS = os.environ.get("PICS", "").split() or [
    "https://i.ibb.co/Kx5mS6V5/x.jpg",
    "https://i.ibb.co/jZQHRzKv/x.jpg",
    "https://i.ibb.co/PvB2DVHQ/x.jpg",
    "https://i.ibb.co/cSYRkdz6/x.jpg",
    "https://i.ibb.co/FjwYKW9/x.jpg"
]

user_rate_limit = {}
FLOOD_COOLDOWN = 30

async def check_flood(user_id: int) -> tuple:
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

boot_sequences = [
    [
        "⚡ <b>Gear Second: Activated!</b>",
        "💨 <i>Blood pumping... Systems accelerating!</i>",
        "✅ <b>READY TO SERVE AT JET SPEED!</b> 🏴‍☠️"
    ],
    [
        "⚓ <b>THOUSAND SUNNY DEPLOYED</b>",
        "🌊 <i>Sailing through the Grand Line...</i>",
        "🧭 <i>Navigation systems: ONLINE</i>",
        "✅ <b>ALL HANDS ON DECK!</b> ⛵"
    ],
    [
        "🌀 <b>DRUMS OF LIBERATION DETECTED!</b>",
        "🌟 <i>The Warrior of Liberation awakens...</i>",
        "🥁 <i>Boom-ba-boom-ba-boom...</i>",
        "✨ <i>Reality bending to your will!</i>",
        "✅ <b>GEAR 5: FULLY OPERATIONAL!</b> 🌈"
    ],
    [
        "🔧 <b>FRANKY'S SUPER STARTUP!</b>",
        "⚙️ <i>Cola energy at 9000%!</i>",
        "🤖 <i>Radar systems scanning...</i>",
        "🦾 <i>Robotic arms calibrating...</i>",
        "🚀 <i>Rockets primed for launch!</i>",
        "✅ <b>SUUUUUPER SYSTEMS READY!</b> 💥"
    ],
    [
        "🍰 <b>WHOLE CAKE BOOT SEQUENCE!</b>",
        "🧁 <i>Preparing file buffet...</i>",
        "🍫 <i>Chocolate servers melting in...</i>",
        "🍮 <i>Sweet storage systems loaded</i>",
        "☕ <i>Tea bots standing by...</i>",
        "👑 <i>Big Mom approves this startup</i>",
        "✅ <b>YOUR FILES WILL BE DELICIOUS!</b> 🍩"
    ]
]

FLOOD_SEQUENCES = [
    [
        "🌊 <b>Woah there nakama!</b>",
        "<i>You're moving faster than Gear 2 Luffy!</i>",
        "⏳ Please wait 3 seconds between requests!"
    ],
    [
        "👑 <b>CONQUEROR'S HAKI DETECTED!</b>",
        "⚡ <i>Your spam shakes the server!</i>",
        "💢 Even Rayleigh would tell you to chill!",
        "🛑 5s cooldown activated..."
    ],
    [
        "☠️ <b>MARINE ADMIRAL INTERVENTION!</b>",
        "👮 <i>Akainu detected spam activity!</i>",
        "🔥 <i>Aokiji froze your requests!</i>",
        "⚡ <i>Kizaru says 'Too fast, yooo~'</i>",
        "⏲️ <b>10s TIMEOUT ENFORCED!</b> 🚫"
    ]
]

async def create_invite_links(client: Client):
    links = []
    for channel in [FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4]:
        if channel:
            try:
                links.append(await client.create_chat_invite_link(chat_id=channel, creates_join_request=True))
            except Exception as e:
                print(f"Error creating invite for {channel}: {e}")
    return links

async def auto_delete(msg, user_msg=None):
    from config import AUTO_CLEAN, DELETE_DELAY
    if AUTO_CLEAN:
        await asyncio.sleep(DELETE_DELAY)
        with contextlib.suppress(Exception):
            await msg.delete()
            if user_msg:
                await user_msg.delete()

async def reply_with_clean(message, text, **kwargs):
    reply = await message.reply(text, **kwargs)
    asyncio.create_task(auto_delete(reply, message))
    return reply

@Bot.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    user_id = message.from_user.id
    
    # First check if user is subscribed
    if not await subscribed(client, message):
        invite_links = await create_invite_links(client)
        buttons = []

        for i in range(0, len(invite_links), 2):
            row = [
                InlineKeyboardButton("• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=invite_links[i].invite_link)
            ]
            if i + 1 < len(invite_links):
                row.append(
                    InlineKeyboardButton("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=invite_links[i+1].invite_link)
                )
            buttons.append(row)

        try:
            payload = message.command[1]
            buttons.append([
                InlineKeyboardButton(
                    text='• ɴᴏᴡ ᴄʟɪᴄᴋ ʜᴇʀᴇ •',
                    url=f"https://t.me/{client.username}?start={payload}"
                )
            ])
        except IndexError:
            pass

        if FORCE_PIC:
            return await message.reply_photo(
                photo=random.choice(PICS),
                caption=FORCE_MSG.format(
                    first=message.from_user.first_name,
                    last=message.from_user.last_name,
                    username=f"@{message.from_user.username}" if message.from_user.username else None,
                    mention=message.from_user.mention,
                    id=message.from_user.id
                ),
                reply_markup=InlineKeyboardMarkup(buttons),
                quote=True
            )
        else:
            return await message.reply(
                text=FORCE_MSG.format(
                    first=message.from_user.first_name,
                    last=message.from_user.last_name,
                    username=f"@{message.from_user.username}" if message.from_user.username else None,
                    mention=message.from_user.mention,
                    id=message.from_user.id
                ),
                reply_markup=InlineKeyboardMarkup(buttons),
                quote=True
            )

    # Flood Check
    is_flooding, level = await check_flood(user_id)
    if is_flooding:
        warning = random.choice(FLOOD_SEQUENCES[min(level, len(FLOOD_SEQUENCES) - 1)])
        print(f"[⚠️ Flood Triggered] User: {user_id} | Level: {level}")  # 👈 Helpful debug log

        if level == 2:
            until = int(time.time()) + FLOOD_COOLDOWN
            try:
                await client.restrict_chat_member(
                    chat_id=message.chat.id,
                    user_id=user_id,
                    until_date=until,
                    permissions=ChatPermissions(can_send_messages=False)
                )
                print(f"[🚫 Flood Block] User {user_id} muted for {FLOOD_COOLDOWN} seconds.")

                # ✅ Schedule unmute task
                asyncio.create_task(unmute_user(client, message.chat.id, user_id))

            except Exception as e:
                print(f"[❌ Flood Restrict Error] {e}")  # Helpful if user is not in a group

        return await reply_with_clean(message, "\n".join(warning))

    # Add to DB
    if not await present_user(user_id):
        await add_user(user_id)

# Check for payload in start command
try:
    payload = message.command[1]
    if payload:
        file_id = await decode(payload)

        if isinstance(file_id, str) and file_id.startswith("get-"):
            file_id = file_id.replace("get-", "")

        message = await client.get_messages(DB_CHANNEL, int(file_id))

        # Boot sequence before sending files
        try:
            progress = await message.reply("👒 Booting LUFFY File Core...")
            for step in random.choice(boot_sequences):
                await asyncio.sleep(random.uniform(0.5, 1.2))
                await progress.edit(step)
            await asyncio.sleep(0.5)
            await progress.delete()
        except Exception as e:
            print(f"Boot animation error: {e}")

        # Send files
        for msg in messages:
            await msg.copy(
                chat_id=message.chat.id,
                caption=CUSTOM_CAPTION,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("📜 Pirate Log", callback_data="about"),
                    InlineKeyboardButton("🗺️ Close Map", callback_data="close")
                ]]),
                protect_content=PROTECT_CONTENT
            )
            await asyncio.sleep(1)

        # Auto delete if enabled
        if AUTO_DELETE_MSG:
            await asyncio.sleep(AUTO_DELETE_TIME)
            await message.delete()

        return

except (IndexError, ValueError, Exception) as e:
    await reply_with_clean(message, f"⚠️ Invalid or broken link.\n\n<code>{e}</code>")

    # Night Mode
    if datetime.now().hour >= 22 or datetime.now().hour < 6:
        reply = await message.reply("🌙 Ara Ara~ It's sleepy hours, but LUFFY's still awake! 🛌👒")
        await asyncio.sleep(AUTO_DELETE_TIME)
        await reply.delete()
        await message.delete()
        return

    # Normal start without payload
    # Boot sequence
    try:
        progress = await message.reply("👒 Booting LUFFY File Core...")
        for step in random.choice(boot_sequences):
            await asyncio.sleep(random.uniform(0.5, 1.2))
            await progress.edit(step)
        await asyncio.sleep(0.5)
        await progress.delete()
    except Exception as e:
        print(f"Boot animation error: {e}")

    # Main menu
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("📜 Pirate Log", callback_data="about"),
         InlineKeyboardButton("🗺️ Close Map", callback_data="close")]
    ])

    if START_PIC:
        reply = await message.reply_photo(
            photo=random.choice(PICS),
            caption=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=f"@{message.from_user.username}" if message.from_user.username else None,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            quote=True
        )
        await auto_delete(reply, message)
    else:
        await message.reply_text(
            text=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=f"@{message.from_user.username}" if message.from_user.username else None,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            quote=True
        )
