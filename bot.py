import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MessageEntity,
)
from telegram.constants import ChatMemberStatus
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ["BOT_TOKEN"]


# =========================
# 공지사항 채널
# =========================

NOTICE_CHANNEL = "@Sexnotice"
NOTICE_URL = "https://t.me/Sexnotice"


# =========================
# 구독 인증 움직이는 이모지
# =========================

SUB_WELCOME_EMOJI_ID = "5413825479406789631"
SUB_BUTTON_EMOJI_ID = "5429633836684157942"
SUB_DONE_EMOJI_ID = "5413617405421167103"


# =========================
# 환영문구 움직이는 이모지
# =========================

TITLE_EMOJI_IDS = [
    "5434018732005412781",
    "5386800802151025866",
    "5431554494519329784",
    "5436174182817744875",
    "5431726486484698393",
]

MAIN_EMOJI_ID = "5267239001508554968"


# =========================
# 실제 메뉴 주소
# =========================

MENU_URLS = {
    "notice": "https://t.me/Sexnotice",
    "waiting": "https://t.me/+FnSLuMpzKCc0MTM1",
    "links": "https://t.me/SexLinker2",
    "neto": "https://t.me/GoodSexer2",
    "body": "https://t.me/BodyGood2",
    "partner": "https://t.me/Kingsexer",
}


# =========================
# 메뉴 이름
# =========================

MENU_NAMES = {
    "notice": "공지사항",
    "waiting": "대기조방",
    "links": "링크모아방",
    "neto": "네토방",
    "body": "전국 몸매자랑방",
    "partner": "제휴문의",
}


# =========================
# 정상 6개 메뉴
# =========================

BUTTONS = [
    [
        InlineKeyboardButton(
            "공지사항",
            callback_data="menu:notice",
            icon_custom_emoji_id="5332312390312668778",
        ),
        InlineKeyboardButton(
            "대기조방",
            callback_data="menu:waiting",
            icon_custom_emoji_id="5332381569350905644",
        ),
    ],
    [
        InlineKeyboardButton(
            "링크모아방",
            callback_data="menu:links",
            icon_custom_emoji_id="5332822842880832998",
        ),
        InlineKeyboardButton(
            "네토방",
            callback_data="menu:neto",
            icon_custom_emoji_id="5332443897916306318",
        ),
    ],
    [
        InlineKeyboardButton(
            "전국 몸매자랑방",
            callback_data="menu:body",
            icon_custom_emoji_id="5330458252930986764",
        ),
    ],
    [
        InlineKeyboardButton(
            "제휴문의",
            callback_data="menu:partner",
            icon_custom_emoji_id="5332817676035176022",
        ),
    ],
]


# =========================
# UTF-16 계산
# =========================

def utf16_len(text):
    return len(text.encode("utf-16-le")) // 2


def add_custom_emoji(parts, entities, emoji_id):
    current_text = "".join(parts)
    offset = utf16_len(current_text)

    placeholder = "❤"
    parts.append(placeholder)

    entities.append(
        MessageEntity(
            type=MessageEntity.CUSTOM_EMOJI,
            offset=offset,
            length=utf16_len(placeholder),
            custom_emoji_id=emoji_id,
        )
    )


# =========================
# 환영문구 만들기
# =========================

def build_welcome_message(name):
    parts = []
    entities = []

    parts.append(f"{name}님, ")

    for emoji_id in TITLE_EMOJI_IDS:
        add_custom_emoji(parts, entities, emoji_id)

    parts.append("에 오신걸 환영합니다.\n\n")

    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)
    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)

    parts.append("눈팅 및 타업체 홍보 추방")

    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)
    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)

    parts.append("\n\n")

    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)
    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)

    parts.append("방 분위기 흐리는 행동 추방")

    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)
    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)

    parts.append("\n\n")

    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)
    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)

    parts.append("몸매 좋은사람은 전국 몸매")

    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)
    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)

    parts.append("\n\n\n")

    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)
    parts.append(" 여성 인증하면 본인 홍보가능\n")

    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)
    parts.append(" 제휴 문의 언제든지 환영\n")

    add_custom_emoji(parts, entities, MAIN_EMOJI_ID)
    parts.append(" 이벤트 00방 진행중\n\n")

    parts.append("원하시는 메뉴를 아래에서 선택해주세요.")

    text = "".join(parts)

    entities.insert(
        0,
        MessageEntity(
            type=MessageEntity.BOLD,
            offset=0,
            length=utf16_len(text),
        )
    )

    return text, entities


# =========================
# 공지사항 구독 여부 확인
# =========================

async def is_subscribed(context, user_id):
    try:
        member = await context.bot.get_chat_member(
            chat_id=NOTICE_CHANNEL,
            user_id=user_id,
        )

        return member.status in (
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER,
        )

    except BadRequest:
        return False

    except Exception as e:
        print(f"구독 확인 오류: {e}")
        return False


# =========================
# 정상 환영문구 + 6개 메뉴
# =========================

async def send_normal_welcome(message, member):
    name = member.full_name or member.first_name or "회원"

    text, entities = build_welcome_message(name)

    await message.reply_text(
        text=text,
        entities=entities,
        reply_markup=InlineKeyboardMarkup(BUTTONS),
    )


# =========================
# 미구독자 인증창
# =========================

async def send_subscription_message(message, member):
    name = member.full_name or member.first_name or "회원"

    parts = []
    entities = []

    add_custom_emoji(
        parts,
        entities,
        SUB_WELCOME_EMOJI_ID,
    )

    parts.append(
        f" {name} 님 반갑습니다!!\n\n"
        "방 사용에 앞서 먼저 아래 채널 구독을 해주세요\n"
        '구독한 후 "입장 완료" 를 누르면 정상 이용 가능합니다.'
    )

    text = "".join(parts)

    keyboard = InlineKeyboardMarkup(
        [
            [
                # 구독 버튼은 공지채널로 바로 이동
                InlineKeyboardButton(
                    "구독 ( 들어가기 )",
                    url=NOTICE_URL,
                    icon_custom_emoji_id=SUB_BUTTON_EMOJI_ID,
                )
            ],
            [
                # 입장 완료는 해당 신규회원 본인만 사용 가능
                InlineKeyboardButton(
                    "구독 완료 ( 입장 완료 )",
                    callback_data=f"check_sub:{member.id}",
                    icon_custom_emoji_id=SUB_DONE_EMOJI_ID,
                )
            ],
        ]
    )

    await message.reply_text(
        text=text,
        entities=entities,
        reply_markup=keyboard,
    )


# =========================
# 신규회원 입장
# =========================

async def welcome(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    message = update.effective_message

    if not message or not message.new_chat_members:
        return

    for member in message.new_chat_members:
        if member.is_bot:
            continue

        # 신규회원의 공지채널 구독 여부 확인
        subscribed = await is_subscribed(
            context,
            member.id,
        )

        # 이미 공지채널을 구독하고 있으면
        # 인증창 없이 바로 정상 환영문구
        if subscribed:
            await send_normal_welcome(
                message,
                member,
            )

        # 미구독자만 인증창 표시
        else:
            await send_subscription_message(
                message,
                member,
            )


# =========================
# 구독 완료 ( 입장 완료 )
# =========================

async def check_subscription(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    if not query:
        return

    try:
        target_user_id = int(
            query.data.split(":")[1]
        )

    except (IndexError, ValueError):
        await query.answer()
        return

    # =========================
    # 핵심
    # 해당 인증창 주인만
    # 입장 완료 버튼 사용 가능
    # =========================

    if query.from_user.id != target_user_id:
        await query.answer(
            "본인의 입장 완료 버튼만 사용할 수 있습니다.",
            show_alert=True,
        )
        return

    # 본인의 실제 공지채널 구독 여부 확인
    subscribed = await is_subscribed(
        context,
        target_user_id,
    )

    if not subscribed:
        await query.answer(
            "아직 공지사항 채널 구독이 확인되지 않았습니다.\n"
            "먼저 구독 후 다시 눌러주세요.",
            show_alert=True,
        )
        return

    # 구독 성공
    await query.answer(
        "구독이 확인되었습니다!"
    )

    user = query.from_user
    chat = query.message.chat

    # 인증창 즉시 삭제
    try:
        await query.message.delete()

    except Exception as e:
        print(f"인증 메시지 삭제 오류: {e}")

    # 정상 환영문구 + 6개 메뉴 표시
    name = user.full_name or user.first_name or "회원"

    text, entities = build_welcome_message(name)

    await context.bot.send_message(
        chat_id=chat.id,
        text=text,
        entities=entities,
        reply_markup=InlineKeyboardMarkup(BUTTONS),
    )


# =========================
# 정상 6개 메뉴 클릭
# =========================

async def menu_click(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    if not query:
        return

    # =========================
    # 메뉴는 누구의 환영창인지 관계없음
    # 실제 버튼 누른 사람의
    # 현재 공지채널 구독 여부만 확인
    # =========================

    subscribed = await is_subscribed(
        context,
        query.from_user.id,
    )

    # 미구독자는 메뉴 사용 불가
    if not subscribed:
        await query.answer(
            "공지사항 채널을 먼저 구독해주세요.",
            show_alert=True,
        )
        return

    try:
        menu_name = query.data.split(":")[1]

        url = MENU_URLS[menu_name]
        display_name = MENU_NAMES[menu_name]

    except (IndexError, KeyError):
        await query.answer(
            "메뉴 정보를 찾을 수 없습니다.",
            show_alert=True,
        )
        return

    # 구독자에게 이동 링크 전송
    try:
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text=f"{display_name}\n\n{url}",
            disable_web_page_preview=True,
        )

        await query.answer(
            f"{display_name} 이동 링크를 보내드렸습니다."
        )

    except Exception:
        await query.answer(
            "Seoul_freebot 개인채팅에서 먼저 /start를 눌러주세요.",
            show_alert=True,
        )


# =========================
# 움직이는 이모지 ID 추출
# =========================

async def get_emoji_id(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    message = update.effective_message

    if not message:
        return

    found_ids = []

    for entity in (message.entities or []):
        if (
            entity.type == MessageEntity.CUSTOM_EMOJI
            and entity.custom_emoji_id
        ):
            found_ids.append(
                entity.custom_emoji_id
            )

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


# =========================
# 실행
# =========================

def main():
    app = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    # 신규회원 입장
    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            welcome,
        )
    )

    # 구독 완료
    app.add_handler(
        CallbackQueryHandler(
            check_subscription,
            pattern=r"^check_sub:",
        )
    )

    # 정상 6개 메뉴
    app.add_handler(
        CallbackQueryHandler(
            menu_click,
            pattern=r"^menu:",
        )
    )

    # 개인채팅 움직이는 이모지 ID
    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE,
            get_emoji_id,
        )
    )

    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()
