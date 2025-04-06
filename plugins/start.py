import os
import time
import asyncio
import random
import contextlib
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from bot import Bot
from config import (
    GLOBAL_REQUESTS, GLOBAL_TIME_WINDOW, MAX_REQUESTS, TIME_WINDOW,
    ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON,
    PROTECT_CONTENT, START_PIC, FORCE_PIC, AUTO_DELETE_TIME, AUTO_DELETE_MSG,
    JOIN_REQUEST_ENABLE, FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2,
    FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4
)
from helper_func import subscribed, decode, get_messages, delete_file, is_user_limited
from database.database import add_user, del_user, full_userbase, total_users, present_user

# ===== CONSTANTS ===== #
PICS = os.environ.get("PICS", "").split() or [
    "https://i.ibb.co/Kx5mS6V5/x.jpg",
    "https://i.ibb.co/jZQHRzKv/x.jpg",
    "https://i.ibb.co/PvB2DVHQ/x.jpg",
    "https://i.ibb.co/cSYRkdz6/x.jpg",
    "https://i.ibb.co/FjwYKW9/x.jpg"
]

# ===== FLOOD CONTROL ===== #
user_rate_limit = {}
FLOOD_COOLDOWN = 30  # 30 second timeout for spammers

async def check_flood(user_id: int) -> tuple:
    """Check if user is flooding the bot"""
    now = time.time()
    user_data = user_rate_limit.setdefault(user_id, {
        "timestamps": [],
        "warn_level": 0
    })
    
    # Clean old requests (10s window)
    user_data["timestamps"] = [t for t in user_data["timestamps"] if now - t < 10]
    
    if len(user_data["timestamps"]) >= 10:  # 10 requests/10s = timeout
        user_data["warn_level"] = 2
        return True, 2
    elif len(user_data["timestamps"]) >= 5:  # 5 requests/10s = warning
        user_data["warn_level"] = 1
        return True, 1
    
    user_data["timestamps"].append(now)
    return False, 0

# ===== BOOT SEQUENCES ===== #
boot_sequences = [
    # Gear 2 Turbo (3 lines)
    [
        "⚡ <b>Gear Second: Activated!</b>",
        "💨 <i>Blood pumping... Systems accelerating!</i>",
        "✅ <b>READY TO SERVE AT JET SPEED!</b> 🏴‍☠️"
    ],
    # Thousand Sunny (4 lines)
    [
        "⚓ <b>THOUSAND SUNNY DEPLOYED</b>",
        "🌊 <i>Sailing through the Grand Line...</i>",
        "🧭 <i>Navigation systems: ONLINE</i>",
        "✅ <b>ALL HANDS ON DECK!</b> ⛵"
    ],
    # Nika Awakening (5 lines)
    [
        "🌀 <b>DRUMS OF LIBERATION DETECTED!</b>",
        "🌟 <i>The Warrior of Liberation awakens...</i>",
        "🥁 <i>Boom-ba-boom-ba-boom...</i>",
        "✨ <i>Reality bending to your will!</i>",
        "✅ <b>GEAR 5: FULLY OPERATIONAL!</b> 🌈"
    ],
    # Franky SUPER (6 lines)
    [
        "🔧 <b>FRANKY'S SUPER STARTUP!</b>",
        "⚙️ <i>Cola energy at 9000%!</i>",
        "🤖 <i>Radar systems scanning...</i>",
        "🦾 <i>Robotic arms calibrating...</i>",
        "🚀 <i>Rockets primed for launch!</i>",
        "✅ <b>SUUUUUPER SYSTEMS READY!</b> 💥"
    ],
    # Whole Cake (7 lines)
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

# ===== FLOOD WARNINGS ===== #
FLOOD_SEQUENCES = [
    # Friendly (3 lines)
    [
        "🌊 <b>Woah there nakama!</b>",
        "<i>You're moving faster than Gear 2 Luffy!</i>",
        "⏳ Please wait 3 seconds between requests!"
    ],
    # Conqueror's (4 lines)
    [
        "👑 <b>CONQUEROR'S HAKI DETECTED!</b>",
        "⚡ <i>Your spam shakes the server!</i>",
        "💢 Even Rayleigh would tell you to chill!",
        "🛑 5s cooldown activated..."
    ],
    # Admiral (5 lines)
    [
        "☠️ <b>MARINE ADMIRAL INTERVENTION!</b>",
        "👮 <i>Akainu detected spam activity!</i>",
        "🔥 <i>Aokiji froze your requests!</i>",
        "⚡ <i>Kizaru says 'Too fast, yooo~'</i>",
        "⏲️ <b>10s TIMEOUT ENFORCED!</b> 🚫"
    ]
]

# ===== HELPER FUNCTIONS ===== #
async def create_invite_links(client: Client):
    """Create invite links for force sub channels"""
    links = []
    for channel in [FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, 
                   FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4]:
        if channel:
            try:
                links.append(await client.create_chat_invite_link(
                    chat_id=channel,
                    creates_join_request=True
                ))
            except Exception as e:
                print(f"Error creating invite for {channel}: {e}")
    return links

async def auto_delete(msg, user_msg=None):
    """Auto delete messages after delay"""
    from config import AUTO_CLEAN, DELETE_DELAY
    if AUTO_CLEAN:
        await asyncio.sleep(DELETE_DELAY)
        with contextlib.suppress(Exception):
            await msg.delete()
            if user_msg:
                await user_msg.delete()

async def reply_with_clean(message, text, **kwargs):
    """Reply with auto-delete"""
    reply = await message.reply(text, **kwargs)
    asyncio.create_task(auto_delete(reply, message))
    return reply

# ===== COMMAND HANDLERS ===== #
@Bot.on_message(filters.command("start") & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id

    # Flood control check
    is_flooding, level = await check_flood(user_id)
    if is_flooding:
        warning = random.choice(FLOOD_SEQUENCES[min(level, len(FLOOD_SEQUENCES)-1)])
        if level == 2:  # Timeout
            until = int(time.time()) + FLOOD_COOLDOWN
            await client.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=user_id,
                until_date=until,
                permissions=ChatPermissions(can_send_messages=False)
            )
        return await reply_with_clean(message, "\n".join(warning))

    # Add user to database
    if not await present_user(user_id):
        try:
            await add_user(user_id)
        except Exception as e:
            print(f"Error adding user {user_id}: {e}")

    # Night mode greeting
    hour = datetime.now().hour
    if hour >= 22 or hour < 6:
        reply = await message.reply("🌙 Ara Ara~ It's sleepy hours, but LUFFY's still awake! 🛌👒")
        await asyncio.sleep(AUTO_DELETE_TIME)
        await reply.delete()
        await message.delete()
        return

    # Boot animation
    try:
        progress = await message.reply("👒 Booting LUFFY File Core...")
        steps = random.choice(boot_sequences)
        for step in steps:
            await asyncio.sleep(random.uniform(0.5, 1.2))
            with contextlib.suppress(Exception):
                await progress.edit(step)
        await asyncio.sleep(0.5)
        await progress.delete()
    except Exception as e:
        print(f"Boot animation error: {e}")

    # Handle file requests
    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
            string = await decode(base64_string)
            argument = string.split("-")

            if len(argument) == 3:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
                ids = range(start, end + 1) if start <= end else list(range(start, end - 1, -1))
            elif len(argument) == 2:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            else:
                return

            temp_msg = await message.reply("<blockquote>⚡ Ara~ Getting your file ready... Hold tight!</blockquote>")
            messages = await get_messages(client, ids)
            await temp_msg.delete()

            track_msgs = []
            for msg in messages:
                caption = CUSTOM_CAPTION.format(
                    previouscaption="" if not msg.caption else msg.caption.html,
                    filename=msg.document.file_name
                ) if bool(CUSTOM_CAPTION) and msg.document else (msg.caption.html if msg.caption else "")

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

        except Exception as e:
            print(f"File handling error: {e}")
            await message.reply_text("<blockquote>😵‍💫 Something went wrong while fetching your files!</blockquote>")
            return

    # Show main menu
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📜 Pirate Log", callback_data="about"),
            InlineKeyboardButton("🗺️ Close Map", callback_data="close")
        ]
    ])

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
            print(f"Error sending photo: {e}")
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

@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    invite_links = await create_invite_links(client)
    buttons = [
        [
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=invite_links[0].invite_link),
            InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=invite_links[1].invite_link),
        ],
        [
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=invite_links[2].invite_link),
            InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=invite_links[3].invite_link),
        ]
    ]
    
    try:
        buttons.append([
            InlineKeyboardButton(
                text='• ɴᴏᴡ ᴄʟɪᴄᴋ ʜᴇʀᴇ •',
                url=f"https://t.me/{client.username}?start={message.command[1]}"
            )
        ])
    except IndexError:
        pass

    if FORCE_PIC:
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
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
    msg = await client.send_message(chat_id=message.chat.id, text="<i>Counting crew members...</i>")
    users = await full_userbase()
    await msg.edit(f"<b>Total Nakamas:</b> {len(users)}")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        stats = {'total': 0, 'success': 0, 'blocked': 0, 'deleted': 0, 'failed': 0}

        pls_wait = await message.reply("<i>Broadcasting to all nakamas...</i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                stats['success'] += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                stats['success'] += 1
            except UserIsBlocked:
                await del_user(chat_id)
                stats['blocked'] += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                stats['deleted'] += 1
            except:
                stats['failed'] += 1
            stats['total'] += 1

        status = f"""<b>Broadcast Complete</b>
Total: {stats['total']}
Success: {stats['success']}
Blocked: {stats['blocked']}
Deleted: {stats['deleted']}
Failed: {stats['failed']}"""
        await pls_wait.edit(status)
    else:
        msg = await message.reply("Reply to a message to broadcast")
        await asyncio.sleep(8)
        await msg.delete()

# ===== UTILITY FUNCTIONS ===== #
WAIT_MESSAGES = [
    "☠️ Yo! Luffy here! Hold on tight...",
    "🌀 GEAR 2... ACTIVATING!",
    "🍖 Meat first, files later!",
    "⚓ Hoisting the sail!",
    "🔥 Gear 5 Vibes Loading..."
]

def get_wait_msg():
    return f"<blockquote>{random.choice(WAIT_MESSAGES)}</blockquote>"

REPLY_ERROR = "<code>Reply to a message to use this command</code>"
