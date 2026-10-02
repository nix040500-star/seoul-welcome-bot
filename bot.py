import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, ContextTypes, filters

TOKEN = os.environ["BOT_TOKEN"]

# =========================
# 환영 문구
# =========================

WELCOME_TEXT = """👋 {name}님, 서울에 오신 것을 환영합니다!
🤬🤬 눈팅 및 타업체 홍보 추방🤬🤬

🤬🤬방 분위기 흐리는 행동 추방🤬🤬

🤬🤬몸매 좋은사람은 전국 몸매🤬🤬


😊 여성 인증하면 본인 홍보가능 
😄 제휴 문의 언제든지 환영
🥳 이벤트 00방 진행중

원하시는 메뉴를 아래에서 선택해주세요."""


# =========================
# 버튼
# =========================

BUTTONS = [
    [
        InlineKeyboardButton(
            "📢 공지사항",
            url="https://t.me/Sexnotice"
        ),
        InlineKeyboardButton(
            "⏳ 대기조방",
            url="https://t.me/+FnSLuMpzKCc0MTM1"
        ),
    ],
    [
        InlineKeyboardButton(
            "🔗 링크모아방",
            url="https://t.me/SexLinker2"
        ),
        InlineKeyboardButton(
            "💬 네토방",
            url="https://t.me/+oTo6bDLCekUxYjU1"
        ),
    ],
    [
        InlineKeyboardButton(
            "🔥 전국 몸매자랑방",
            url="https://t.me/+-HAXJwNLVz1lYmNl"
        ),
    ],
    [
        InlineKeyboardButton(
            "🤝 제휴문의",
            url="https://t.me/Kingsexer"
        ),
    ],
]


# =========================
# 새 회원 자동 환영
# =========================

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


# =========================
# 움직이는 이모지 ID 추출
# =========================

async def emoji_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message

    if not message:
        return

    found_ids = []

    # 텍스트 Premium Custom Emoji
    for entity in (message.entities or []):

        if (
            entity.type == "custom_emoji"
            and entity.custom_emoji_id
        ):
            found_ids.append(entity.custom_emoji_id)

    # 캡션 Custom Emoji
    for entity in (message.caption_entities or []):

        if (
            entity.type == "custom_emoji"
            and entity.custom_emoji_id
        ):
            found_ids.append(entity.custom_emoji_id)

    # Custom Emoji Sticker
    if message.sticker:

        custom_id = message.sticker.custom_emoji_id

        if custom_id:
            found_ids.append(custom_id)

    # 중복 ID 제거
    found_ids = list(dict.fromkeys(found_ids))

    if found_ids:

        result = (
            "✅ CUSTOM EMOJI ID\n\n"
            + "\n".join(found_ids)
        )

        await message.reply_text(result)

    elif message.chat.type == "private":

        await message.reply_text(
            "❌ Custom Emoji ID를 찾지 못했습니다.\n"
            "움직이는 Premium 이모지를 보내주세요."
        )


# =========================
# 봇 실행
# =========================

def main():

    app = Application.builder().token(TOKEN).build()

    # 새 회원 입장 감지
    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            welcome
        )
    )

    # 개인톡에서 이모지 ID 추출
    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE,
            emoji_id
        )
    )

    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()
