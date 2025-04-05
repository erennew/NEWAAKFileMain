#(©) WeekendsBotz

from pyrogram import __version__
from bot import Bot
from config import OWNER_ID
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "about":
        await query.message.edit_text(
            text = (
                "<b><blockquote>☠️ LUFFY’S MAP ☠️\n\n"
                "👒 ᴄᴀᴘᴛᴀɪɴ : <a href='https://t.me/CulturedTeluguWeebBot'>ʀᴀᴠɪ ᴅᴏɴ!</a>\n"
                "🏴‍☠️ ᴍᴀɪɴ ɪꜱʟᴀɴᴅ : <a href='https://t.me/CulturedTeluguweeb'>ᴄᴜʟᴛᴜʀᴇᴅ ᴡᴇᴇʙ</a>\n"
                "📺 ᴄᴜʀʀᴇɴᴛ ᴀɴɪᴍᴇ ᴍɪssɪᴏɴ : <a href='https://t.me/+BiVvkpD5ieIxZTNl'>ᴄᴛᴡ ᴏɴɢᴏɪɴɢ</a>\n"
                "🗣️ ᴘɪʀᴀᴛᴇ ᴛᴀʟᴋs : <a href='https://t.me/+IIgB6RgivTI2NzA1'>ᴄᴜʟᴛᴜʀᴇᴅ ᴡᴇᴇʙꜱ</a>"
                "</blockquote></b>"
            ),
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🗺️ Close Map", callback_data = "close")
                    ]
                ]
            )
        )
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass
