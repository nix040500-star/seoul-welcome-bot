import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, ContextTypes, filters

TOKEN = os.environ["BOT_TOKEN"]

WELCOME_TEXT = """👋 {name}님, 서울에 오신 것을 환영합니다!

원하시는 메뉴를 아래에서 선택해주세요."""

BUTTONS = [
    [
        InlineKeyboardButton("📢 공지사항", url="https://t.me/Sexnotice"),
        InlineKeyboardButton("⏳ 대기조방", url="https://t.me/+FnSLuMpzKCc0MTM1"),
    ],
    [
        InlineKeyboardButton("🔗 링크모아방", url="https://t.me/SexLinker2"),
        InlineKeyboardButton("💬 네토방", url="https://t.me/+oTo6bDLCekUxYjU1"),
    ],
    [
        InlineKeyboardButton("🔥 전국 몸매자랑방", url="https://t.me/+-HAXJwNLVz1lYmNl"),
    ],
]

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message or not message.new_chat_members:
        return

    keyboard = InlineKeyboardMarkup(BUTTONS)

    for member in message.new_chat_members:
        if member.is_bot:
            continue
        name = member.full_name or member.first_name or "회원"
        await message.reply_text(
            WELCOME_TEXT.format(name=name),
            reply_markup=keyboard
        )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
