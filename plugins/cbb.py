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
            text = f"<b><blockquote>○ ᴏᴡɴᴇʀ : <a href='@CulturedTeluguWeebBot'>ʀᴀᴠɪ</a>\n○ ᴍᴀɪɴ ᴄʜᴀɴɴᴇʟ : <a href='https://t.me/CulturedTeluguweeb'>ᴄᴜʟᴛᴜʀᴇᴅ ᴡᴇᴇʙ</a>\n○ ᴏɴɢᴏɪɴɢ : <a href='https://t.me/+BiVvkpD5ieIxZTNl'>ᴄᴛᴡ ᴏɴɢᴏɪɴɢ</a>\n○ ᴅɪꜱᴄᴜꜱꜱ ɢʀᴏᴜᴘ : <a href='https://t.me/+IIgB6RgivTI2NzA1'>ᴄᴜʟᴛᴜʀᴇᴅ ᴡᴇᴇʙꜱ
</a></blockquote></b>",
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("⚡ Cℓσѕє", callback_data = "close")
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
