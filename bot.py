import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, ContextTypes, filters

TOKEN = os.environ["BOT_TOKEN"]

WELCOME_TEXT = """👋 {name}님, 서울에 오신 것을 환영합니다!

원하시는 메뉴를 아래에서 선택해주세요."""

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


# 새 회원 자동 환영
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


# 움직이는 이모지 ID 추출
async def emoji_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message

    if not message:
        return

    found_ids = []

    # 1. 메시지에 들어있는 Premium Custom Emoji
    for entity in (message.entities or []):
        if entity.type == "custom_emoji" and entity.custom_emoji_id:
            found_ids.append(entity.custom_emoji_id)

    # 2. 캡션에 들어있는 Custom Emoji
    for entity in (message.caption_entities or []):
        if entity.type == "custom_emoji" and entity.custom_emoji_id:
            found_ids.append(entity.custom_emoji_id)

    # 3. Custom Emoji Sticker
    if message.sticker:
        sticker = message.sticker

        if sticker.custom_emoji_id:
            found_ids.append(sticker.custom_emoji_id)

    # 중복 제거
    found_ids = list(dict.fromkeys(found_ids))

    if found_ids:
        result = "✅ CUSTOM EMOJI ID\n\n" + "\n".join(found_ids)

        await message.reply_text(result)
    else:
        # 개인톡에서만 안내
        if message.chat.type == "private":
            await message.reply_text(
                "❌ Custom Emoji ID를 찾지 못했습니다.\n"
                "움직이는 Premium 이모지 또는 Custom Emoji 스티커를 보내주세요."
            )


def main():
    app = Application.builder().token(TOKEN).build()

    # 새 회원 자동 환영
    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            welcome
        )
    )

    # 개인톡으로 오는 모든 메시지 검사
    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE,
            emoji_id
        )
    )

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
