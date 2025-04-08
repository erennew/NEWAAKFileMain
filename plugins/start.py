import os
import asyncio
import random
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from bot import Bot
from config import (
    ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON,
    PROTECT_CONTENT, START_PIC, FORCE_PIC, AUTO_DELETE_TIME, AUTO_DELETE_MSG,
    JOIN_REQUEST_ENABLE, FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2,
    FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4
)
from helper_func import subscribed, decode, get_messages, delete_file
from database.database import add_user, del_user, full_userbase, present_user


# Boot Sequences (Luffy Style)
boot_sequences = [
    ["☠️ Setting Sail on the Grand Line...", "⚙️ Activating Gear 2...", "💥 Gear 2 Activated! Time to stretch reality!"],
    ["🌀 Gear 4: BOUNDMAN!", "💪 Luffy’s power is off the charts!", "🎯 Ready to smash some files your way!"],
    ["🌪️ Gear 5: Nika Mode...", "🤣 Rubber reality bending in 3...2...1...", "🔥 Get ready for some chaos, pirate!"],
    ["🧭 Drawing the treasure map...", "⚓ Docking the Sunny...", "📦 Delivering your files, captain!"],
    ["🍖 Sanji’s cooking up speed...", "⚡ Zoro got lost... again.", "🦴 Chopper says it’s safe to go!"],
    ["🔥 Sabo's fire is lit...", "🌈 Bon-chan believes in you!", "💡 Starting your pirate quest!"]
]

def get_random_boot_sequence():
    return random.choice(boot_sequences)


async def create_invite_links(client: Client):
    invite1 = await client.create_chat_invite_link(chat_id=FORCE_SUB_CHANNEL_1, creates_join_request=True)
    invite2 = await client.create_chat_invite_link(chat_id=FORCE_SUB_CHANNEL_2, creates_join_request=True)
    invite3 = await client.create_chat_invite_link(chat_id=FORCE_SUB_CHANNEL_3, creates_join_request=True)
    invite4 = await client.create_chat_invite_link(chat_id=FORCE_SUB_CHANNEL_4, creates_join_request=True)
    return invite1, invite2, invite3, invite4


@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    if not await present_user(user_id):
        try:
            await add_user(user_id)
        except:
            pass

    # Send boot sequence animation
    boot_sequence = get_random_boot_sequence()
    boot_msg = await message.reply("<b>👒 Starting...</b>")
    for line in boot_sequence:
        await asyncio.sleep(1.3)
        try:
            await boot_msg.edit(line)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await boot_msg.edit(line)

    await asyncio.sleep(0.5)
    await boot_msg.delete()

    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
            string = await decode(base64_string)
            argument = string.split("-")
            if len(argument) == 3:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
                ids = list(range(start, end + 1)) if start <= end else list(range(start, end - 1, -1))
            elif len(argument) == 2:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            else:
                return
        except:
            return

        temp_msg = await message.reply("<blockquote>🧩 Fetching secret treasure...</blockquote>")
        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply("<blockquote>😰 Something went wrong while retrieving files.</blockquote>")
            return
        await temp_msg.delete()

        track_msgs = []
        for msg in messages:
            caption = (CUSTOM_CAPTION.format(previouscaption=msg.caption.html if msg.caption else "", filename=msg.document.file_name)
                       if CUSTOM_CAPTION and msg.document else msg.caption.html if msg.caption else "")
            reply_markup = None if DISABLE_CHANNEL_BUTTON else msg.reply_markup

            try:
                copied_msg = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    protect_content=PROTECT_CONTENT
                )
                if AUTO_DELETE_TIME and AUTO_DELETE_TIME > 0 and copied_msg:
                    track_msgs.append(copied_msg)
                await asyncio.sleep(0.4)
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                print(f"[ERROR] Message copy failed: {e}")

        if track_msgs:
            delete_data = await client.send_message(
                chat_id=message.from_user.id,
                text=AUTO_DELETE_MSG.format(time=AUTO_DELETE_TIME)
            )
            asyncio.create_task(delete_file(track_msgs, client, delete_data))
        return

    # If no file requested
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ ΛΒσυτ", callback_data="about"),
         InlineKeyboardButton("🍀 Cℓσѕє", callback_data="close")]
    ])
    caption = START_MSG.format(
        first=message.from_user.first_name,
        last=message.from_user.last_name,
        username=None if not message.from_user.username else '@' + message.from_user.username,
        mention=message.from_user.mention,
        id=message.from_user.id
    )

    if START_PIC:
        await message.reply_photo(photo=START_PIC, caption=caption, reply_markup=reply_markup, quote=True)
    else:
        await message.reply_text(text=caption, reply_markup=reply_markup, quote=True, disable_web_page_preview=True)


@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    invite1, invite2, invite3, invite4 = await create_invite_links(client)
    buttons = [
        [InlineKeyboardButton("• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=invite1.invite_link),
         InlineKeyboardButton("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=invite2.invite_link)],
        [InlineKeyboardButton("• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=invite3.invite_link),
         InlineKeyboardButton("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=invite4.invite_link)],
    ]
    try:
        buttons.append([InlineKeyboardButton("• ɴᴏᴡ ᴄʟɪᴄᴋ ʜᴇʀᴇ •", url=f"https://t.me/{client.username}?start={message.command[1]}")])
    except IndexError:
        pass

    caption = FORCE_MSG.format(
        first=message.from_user.first_name,
        last=message.from_user.last_name,
        username=None if not message.from_user.username else '@' + message.from_user.username,
        mention=message.from_user.mention,
        id=message.from_user.id
    )

    if FORCE_PIC:
        await message.reply_photo(photo=FORCE_PIC, caption=caption, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply(text=caption, reply_markup=InlineKeyboardMarkup(buttons), quote=True, disable_web_page_preview=True)


@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text="<b><blockquote>🧾 Counting the pirate crew...</blockquote></b>")
    users = await full_userbase()
    await msg.edit_text(f"☠️ <b>{len(users)} pirates</b> have joined our crew! 🏴‍☠️")


@Bot.on_message(filters.command('broadcast') & filters.private & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if not message.reply_to_message:
        msg = await message.reply("<code>Use this command as a reply to any Telegram message without any spaces.</code>")
        await asyncio.sleep(8)
        await msg.delete()
        return

    users = await full_userbase()
    total, successful, blocked, deleted, unsuccessful = 0, 0, 0, 0, 0
    status_msg = await message.reply("<i><blockquote>Broadcasting Message... Hang tight, matey!</blockquote></i>")

    for user_id in users:
        try:
            await message.reply_to_message.copy(user_id)
            successful += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.reply_to_message.copy(user_id)
            successful += 1
        except UserIsBlocked:
            await del_user(user_id)
            blocked += 1
        except InputUserDeactivated:
            await del_user(user_id)
            deleted += 1
        except:
            unsuccessful += 1
        total += 1

    await status_msg.edit_text(f"""<b><u>🏴‍☠️ Broadcast Report</u></b>

Total: <code>{total}</code>
✅ Successful: <code>{successful}</code>
🚫 Blocked: <code>{blocked}</code>
🗑️ Deleted: <code>{deleted}</code>
❌ Failed: <code>{unsuccessful}</code>""")
