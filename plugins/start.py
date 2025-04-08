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
from helper_func import subscribed, decode, get_messages, delete_file, is_user_limited
from database.database import add_user, present_user

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
    if AUTO_DELETE_MSG:
        await asyncio.sleep(AUTO_DELETE_TIME)
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
    
    # Flood Check
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

    # Check subscription
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
    # Handle file links
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

            # 🎬 Boot Animation before sending files
            boot_msg = await message.reply("🚢 Starting system check...")
            for line in random.choice(boot_sequences):
                await asyncio.sleep(1.2)
                await boot_msg.edit(line)
            await asyncio.sleep(0.5)
            await boot_msg.delete()

            temp_msg = await message.reply(f"<blockquote>⚡ Preparing your files...</blockquote>")
            messages = await get_messages(client, ids)
            await temp_msg.delete()
            
            track_msgs = []
            for msg in messages:
                if not msg or not msg.document:
                    continue
                    
                caption = CUSTOM_CAPTION.format(
                    previouscaption="" if not msg.caption else msg.caption.html,
                    filename=msg.document.file_name
                ) if CUSTOM_CAPTION else (msg.caption.html if msg.caption else "")
                
                reply_markup = msg.reply_markup if not DISABLE_CHANNEL_BUTTON else None
                
                try:
                    if AUTO_DELETE_TIME > 0:
                        copied_msg = await msg.copy(
                            chat_id=message.from_user.id,
                            caption=caption,
                            parse_mode=ParseMode.HTML,
                            reply_markup=reply_markup,
                            protect_content=PROTECT_CONTENT
                        )
                        track_msgs.append(copied_msg)
                    else:
                        await msg.copy(
                            chat_id=message.from_user.id,
                            caption=caption,
                            parse_mode=ParseMode.HTML,
                            reply_markup=reply_markup,
                            protect_content=PROTECT_CONTENT
                        )
                        await asyncio.sleep(0.5)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    if AUTO_DELETE_TIME > 0:
                        copied_msg = await msg.copy(
                            chat_id=message.from_user.id,
                            caption=caption,
                            parse_mode=ParseMode.HTML,
                            reply_markup=reply_markup,
                            protect_content=PROTECT_CONTENT
                        )
                        track_msgs.append(copied_msg)
                    else:
                        await msg.copy(
                            chat_id=message.from_user.id,
                            caption=caption,
                            parse_mode=ParseMode.HTML,
                            reply_markup=reply_markup,
                            protect_content=PROTECT_CONTENT
                        )
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


    # Normal start without payload
    if not await present_user(user_id):
        await add_user(user_id)

    # Night Mode
    if datetime.now().hour >= 22 or datetime.now().hour < 6:
        reply = await message.reply("🌙 Ara Ara~ It's sleepy hours, but LUFFY's still awake! 🛌👒")
        await asyncio.sleep(AUTO_DELETE_TIME)
        await reply.delete()
        await message.delete()
        return

    # Main menu
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("📜 Pirate Log", callback_data="about"),
         InlineKeyboardButton("🗺️ Close Map", callback_data="close")]
    ])

    if START_PIC:
        await message.reply_photo(
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
            link_preview_options={"is_disabled": True},
            quote=True
        )
