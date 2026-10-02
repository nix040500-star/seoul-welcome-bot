import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MessageEntity,
)
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ["BOT_TOKEN"]


# ==================================================
# 움직이는 CUSTOM EMOJI ID
# ==================================================

TITLE_EMOJI_IDS = [
    "5434018732005412781",
    "5386800802151025866",
    "5431554494519329784",
    "5436174182817744875",
    "5431726486484698393",
]

MAIN_EMOJI_ID = "5267239001508554968"


# ==================================================
# 버튼
# ==================================================

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


# ==================================================
# UTF-16 위치 계산
# Telegram MessageEntity는 UTF-16 기준
# ==================================================

def utf16_len(text):
    return len(text.encode("utf-16-le")) // 2


def add_custom_emoji(text_parts, entities, emoji_id):
    """
    움직이는 Custom Emoji 하나 추가
    화면상 placeholder는 ❤ 사용
    """
    current_text = "".join(text_parts)
    offset = utf16_len(current_text)

    placeholder = "❤"
    text_parts.append(placeholder)

    entities.append(
        MessageEntity(
            type=MessageEntity.CUSTOM_EMOJI,
            offset=offset,
            length=utf16_len(placeholder),
            custom_emoji_id=emoji_id,
        )
    )


# ==================================================
# 환영 메시지 생성
# ==================================================

def build_welcome_message(name):
    parts = []
    entities = []

    # ---------- 첫 줄 ----------

    parts.append(f"{name}님, ")

    # 움직이는 글자 5개
    for emoji_id in TITLE_EMOJI_IDS:
        add_custom_emoji(
            parts,
            entities,
            emoji_id
        )

    parts.append("에 오신걸 환영합니다.\n\n")

    # ---------- 추방 안내 1 ----------

    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)
    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)

    parts.append("눈팅 및 타업체 홍보 추방")

    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)
    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)

    parts.append("\n\n")

    # ---------- 추방 안내 2 ----------

    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)
    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)

    parts.append("방 분위기 흐리는 행동 추방")

    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)
    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)

    parts.append("\n\n")

    # ---------- 몸매 ----------

    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)
    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)

    parts.append("몸매 좋은사람은 전국 몸매")

    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)
    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)

    parts.append("\n\n\n")

    # ---------- 여성 인증 ----------

    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)
    parts.append(" 여성 인증하면 본인 홍보가능\n")

    # ---------- 제휴 문의 ----------

    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)
    parts.append(" 제휴 문의 언제든지 환영\n")

    # ---------- 이벤트 ----------

    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)
    parts.append(" 이벤트 00방 진행중\n\n")

    # ---------- 마지막 ----------

    parts.append(
        "원하시는 메뉴를 아래에서 선택해주세요."
    )

    text = "".join(parts)

    # 전체 문구 Bold
    entities.insert(
        0,
        MessageEntity(
            type=MessageEntity.BOLD,
            offset=0,
            length=utf16_len(text),
        )
    )

    return text, entities


# ==================================================
# 새 회원 자동 환영
# ==================================================

async def welcome(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    message = update.effective_message

    if not message or not message.new_chat_members:
        return

    keyboard = InlineKeyboardMarkup(BUTTONS)

    for member in message.new_chat_members:

        if member.is_bot:
            continue

        name = (
            member.full_name
            or member.first_name
            or "회원"
        )

        text, entities = build_welcome_message(name)

        await message.reply_text(
            text=text,
            entities=entities,
            reply_markup=keyboard,
        )


# ==================================================
# CUSTOM EMOJI ID 추출 기능
# ==================================================

async def get_emoji_id(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    message = update.effective_message

    if not message:
        return

    found_ids = []

    # 텍스트 Custom Emoji
    for entity in (message.entities or []):

        if (
            entity.type == MessageEntity.CUSTOM_EMOJI
            and entity.custom_emoji_id
        ):
            found_ids.append(
                entity.custom_emoji_id
            )

    # 스티커 Custom Emoji
    if (
        message.sticker
        and message.sticker.custom_emoji_id
    ):
        found_ids.append(
            message.sticker.custom_emoji_id
        )

    found_ids = list(
        dict.fromkeys(found_ids)
    )

    if found_ids:

        await message.reply_text(
            "✅ 움직이는 이모지 ID\n\n"
            + "\n".join(found_ids)
        )


# ==================================================
# 봇 실행
# ==================================================

def main():

    app = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )

    # 새 회원 자동 환영
    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            welcome
        )
    )

    # 개인톡 Custom Emoji ID 추출
    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE,
            get_emoji_id
        )
    )

    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()
