import os
import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MessageEntity,
    ChatPermissions,
)

from telegram.constants import ChatMemberStatus

from telegram.ext import (
    Application,
    MessageHandler,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    filters,
)


TOKEN = os.environ["BOT_TOKEN"]


# ==================================================
# 서 울 메인방
# ==================================================

MAIN_GROUP_ID = -1003796235018


# ==================================================
# 공지사항 채널
# ==================================================

NOTICE_CHANNEL = "@Sexnotice"
NOTICE_URL = "https://t.me/Sexnotice"


# ==================================================
# 매일 오전 9시 자동 공지
# ==================================================

KST = ZoneInfo("Asia/Seoul")
DAILY_NOTICE_HOUR = 9

NOTICE_TITLE_EMOJI_IDS = [
    "5434018732005412781",
    "5386800802151025866",
    "5431554494519329784",
    "5436174182817744875",
    "5431726486484698393",
]

NOTICE_LINE1_EMOJI_ID = "5461033346152804686"
NOTICE_LINE2_EMOJI_ID = "5469622950032321924"
NOTICE_WARNING_EMOJI_ID = "5420323339723881652"
NOTICE_FLAG_EMOJI_ID = "5219863085577155639"
NOTICE_SMILE_EMOJI_ID = "5217980545576739208"


# ==================================================
# 미구독자 인증창 저장
#
# user_id : message_id
# ==================================================

PENDING_SUBSCRIPTION_MESSAGES = {}

# ==================================================
# 신규회원 성별 선택 상태
#
# user_id : 성별 선택창 message_id
# ==================================================

PENDING_GENDER_MESSAGES = {}
SELECTED_GENDERS = {}


# ==================================================
# 구독 인증 움직이는 이모지
# ==================================================

SUB_WELCOME_EMOJI_ID = "5413825479406789631"
SUB_BUTTON_EMOJI_ID = "5429633836684157942"
SUB_DONE_EMOJI_ID = "5413617405421167103"


# ==================================================
# 환영문구 움직이는 이모지
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
# 6개 메뉴 - URL 직접 이동
# ==================================================

BUTTONS = [
    [
        InlineKeyboardButton(
            "공지사항",
            url="https://t.me/Sexnotice",
            icon_custom_emoji_id="5332312390312668778",
        ),
        InlineKeyboardButton(
            "대기조방",
            url="https://t.me/+FnSLuMpzKCc0MTM1",
            icon_custom_emoji_id="5332381569350905644",
        ),
    ],
    [
        InlineKeyboardButton(
            "링크모아방",
            url="https://t.me/SexLinker2",
            icon_custom_emoji_id="5332822842880832998",
        ),
        InlineKeyboardButton(
            "네토방",
            url="https://t.me/GoodSexer2",
            icon_custom_emoji_id="5332443897916306318",
        ),
    ],
    [
        InlineKeyboardButton(
            "전국 몸매자랑방",
            url="https://t.me/BodyGood2",
            icon_custom_emoji_id="5330458252930986764",
        ),
    ],
    [
        InlineKeyboardButton(
            "제휴문의",
            url="https://t.me/Kingsexer",
            icon_custom_emoji_id="5332817676035176022",
        ),
    ],
]


# ==================================================
# UTF-16
# ==================================================

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


# ==================================================
# 환영문구
# ==================================================

def build_welcome_message(name):
    parts = []
    entities = []

    parts.append(f"{name}님, ")

    for emoji_id in TITLE_EMOJI_IDS:
        add_custom_emoji(
            parts,
            entities,
            emoji_id,
        )

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

    add_custom_emoji(parts, entities, "5386805659759046018")
    parts.append(" 여성 인증하면 본인 홍보가능\n")

    add_custom_emoji(parts, entities, "5269402556924180806")
    parts.append(" 제휴 문의 언제든지 환영\n")

    add_custom_emoji(parts, entities, "5449800250032143374")
    parts.append(" 이벤트 00방 진행중\n\n")

    parts.append(
        "원하시는 메뉴를 아래에서 선택해주세요."
    )

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


# ==================================================
# 공지사항 채널 구독 확인
# ==================================================

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

    except Exception as e:
        print(f"공지채널 확인 오류: {e}")
        return False


# ==================================================
# 서 울 메인방 회원 확인
# ==================================================

async def is_main_group_member(context, user_id):
    try:
        member = await context.bot.get_chat_member(
            chat_id=MAIN_GROUP_ID,
            user_id=user_id,
        )

        return member.status in (
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER,
            ChatMemberStatus.RESTRICTED,
        )

    except Exception as e:
        print(f"메인방 회원 확인 오류: {e}")
        return False


# ==================================================
# 미구독 신규회원 채팅 잠금
# ==================================================

async def lock_member(context, user_id):
    try:
        await context.bot.restrict_chat_member(
            chat_id=MAIN_GROUP_ID,
            user_id=user_id,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_audios=False,
                can_send_documents=False,
                can_send_photos=False,
                can_send_videos=False,
                can_send_video_notes=False,
                can_send_voice_notes=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False,
                can_manage_topics=False,
            ),
        )

        print(f"{user_id} 채팅 잠금 완료")
        return True

    except Exception as e:
        print(f"채팅 잠금 오류: {e}")
        return False


# ==================================================
# 구독 완료 회원 채팅 잠금 해제
# ==================================================

async def unlock_member(context, user_id):
    try:
        await context.bot.restrict_chat_member(
            chat_id=MAIN_GROUP_ID,
            user_id=user_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_audios=True,
                can_send_documents=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_video_notes=True,
                can_send_voice_notes=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=False,
                can_invite_users=True,
                can_pin_messages=False,
                can_manage_topics=False,
            ),
        )

        print(f"{user_id} 채팅 잠금 해제 완료")
        return True

    except Exception as e:
        print(f"채팅 잠금 해제 오류: {e}")
        return False


# ==================================================
# 정상 환영문구 + URL 메뉴
# 독립 메시지
# ==================================================

async def send_normal_welcome(context, chat_id, member):
    name = (
        member.full_name
        or member.first_name
        or "회원"
    )

    text, entities = build_welcome_message(name)

    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        entities=entities,
        reply_markup=InlineKeyboardMarkup(BUTTONS),
    )


# ==================================================
# 신규회원 성별 선택
# 성별 선택 후 기존 구독 인증창으로 이동
# ==================================================

async def send_gender_message(context, chat_id, member):
    name = (
        member.full_name
        or member.first_name
        or "회원"
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "남성",
                    callback_data=f"gender:male:{member.id}",
                    icon_custom_emoji_id="5449749354669682195",
                ),
                InlineKeyboardButton(
                    "여성",
                    callback_data=f"gender:female:{member.id}",
                    icon_custom_emoji_id="5447342287493279609",
                ),
            ],
        ]
    )

    sent_message = await context.bot.send_message(
        chat_id=chat_id,
        text="본인의 성별을 선택해 주세요.",
        reply_markup=keyboard,
    )

    PENDING_GENDER_MESSAGES[member.id] = sent_message.message_id
    print(
        f"{member.id} 성별 선택창 저장: "
        f"{sent_message.message_id}"
    )


async def select_gender(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    if not query:
        return

    try:
        _, gender_code, target_user_id_text = query.data.split(":")
        target_user_id = int(target_user_id_text)
    except (ValueError, AttributeError):
        await query.answer()
        return

    # 본인의 성별 버튼만 클릭 가능
    if query.from_user.id != target_user_id:
        await query.answer(
            "본인의 성별 선택 버튼만 사용할 수 있습니다.",
            show_alert=True,
        )
        return

    # 실제 메인방 회원인지 확인
    main_member = await is_main_group_member(
        context,
        target_user_id,
    )

    if not main_member:
        await query.answer(
            "서 울 메인방 회원이 아닙니다.",
            show_alert=True,
        )
        return

    gender = {
        "male": "남성",
        "female": "여성",
    }.get(gender_code)

    if not gender:
        await query.answer()
        return

    SELECTED_GENDERS[target_user_id] = gender

    user = query.from_user
    chat = query.message.chat
    name = (
        user.full_name
        or user.first_name
        or "회원"
    )

    await query.answer(f"{gender}으로 선택되었습니다.")

    # 성별 선택창 삭제
    try:
        await query.message.delete()
    except Exception as e:
        print(f"성별 선택창 삭제 오류: {e}")

    PENDING_GENDER_MESSAGES.pop(
        target_user_id,
        None,
    )

    # 그룹에 선택 결과 표시
    await context.bot.send_message(
        chat_id=chat.id,
        text=f"{name} 님은 {gender}입니다.",
    )

    # 성별 선택이 끝나면 기존 구독/입장완료 단계로 이동
    await send_subscription_message(
        context,
        chat.id,
        user,
    )


# ==================================================
# 미구독 신규회원 인증창
# 독립 메시지 + message_id 저장
# ==================================================

async def send_subscription_message(context, chat_id, member):
    name = (
        member.full_name
        or member.first_name
        or "회원"
    )

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
        '구독한 후 "입장 완료" 를 누르면 채팅이 활성화됩니다.'
    )

    text = "".join(parts)

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "구독 ( 들어가기 )",
                    url=NOTICE_URL,
                    icon_custom_emoji_id=SUB_BUTTON_EMOJI_ID,
                )
            ],
            [
                InlineKeyboardButton(
                    "구독 완료 ( 입장 완료 )",
                    callback_data=f"check_sub:{member.id}",
                    icon_custom_emoji_id=SUB_DONE_EMOJI_ID,
                )
            ],
        ]
    )

    sent_message = await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        entities=entities,
        reply_markup=keyboard,
    )

    # 이 회원의 구독 인증창 message_id 저장
    PENDING_SUBSCRIPTION_MESSAGES[member.id] = sent_message.message_id

    print(
        f"{member.id} 구독 인증창 저장: "
        f"{sent_message.message_id}"
    )


# ==================================================
# 신규회원 입장
# ==================================================

async def welcome(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    message = update.effective_message

    if not message or not message.new_chat_members:
        return

    chat_id = message.chat.id

    for member in message.new_chat_members:

        # 봇 제외
        if member.is_bot:
            continue

        subscribed = await is_subscribed(
            context,
            member.id,
        )

        # 이미 구독한 회원
        if subscribed:

            await unlock_member(
                context,
                member.id,
            )

            await send_normal_welcome(
                context,
                chat_id,
                member,
            )

        # 미구독 회원
        else:

            await lock_member(
                context,
                member.id,
            )

            await send_gender_message(
                context,
                chat_id,
                member,
            )


    # ==================================================
    # Telegram 기본 입장 시스템 메시지 삭제
    # ==================================================

    try:
        await message.delete()
        print("입장 시스템 메시지 삭제 완료")

    except Exception as e:
        print(f"입장 메시지 삭제 오류: {e}")


# ==================================================
# 구독 완료 버튼
# ==================================================

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


    # ==================================================
    # 남의 구독 완료 버튼 클릭 차단
    # ==================================================

    if query.from_user.id != target_user_id:
        await query.answer(
            "본인의 입장 완료 버튼만 사용할 수 있습니다.",
            show_alert=True,
        )
        return


    # ==================================================
    # 실제 메인방 회원인지 확인
    # ==================================================

    main_member = await is_main_group_member(
        context,
        target_user_id,
    )

    if not main_member:
        await query.answer(
            "서 울 메인방 회원이 아닙니다.",
            show_alert=True,
        )
        return


    # ==================================================
    # 실제 공지사항 채널 구독 확인
    # ==================================================

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


    # ==================================================
    # 구독 성공 → 채팅 잠금 해제
    # ==================================================

    unlocked = await unlock_member(
        context,
        target_user_id,
    )

    if not unlocked:
        await query.answer(
            "구독은 확인됐지만 채팅 권한을 활성화하지 못했습니다.\n"
            "관리자에게 문의해주세요.",
            show_alert=True,
        )
        return


    await query.answer(
        "구독 확인 완료! 이제 채팅할 수 있습니다."
    )

    user = query.from_user
    chat = query.message.chat


    # ==================================================
    # 구독 인증창 삭제
    # ==================================================

    try:
        await query.message.delete()

    except Exception as e:
        print(f"인증창 삭제 오류: {e}")


    # 저장 목록에서도 제거
    PENDING_SUBSCRIPTION_MESSAGES.pop(
        target_user_id,
        None,
    )


    # ==================================================
    # 정상 환영문구 + URL 메뉴
    # ==================================================

    name = (
        user.full_name
        or user.first_name
        or "회원"
    )

    text, entities = build_welcome_message(name)

    await context.bot.send_message(
        chat_id=chat.id,
        text=text,
        entities=entities,
        reply_markup=InlineKeyboardMarkup(BUTTONS),
    )


# ==================================================
# 회원 퇴장 처리
#
# 1. 미구독자의 남아있는 구독 인증창 삭제
# 2. Telegram 기본 퇴장 메시지 삭제
# ==================================================

async def delete_left_member_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    message = update.effective_message

    if not message:
        return

    member = message.left_chat_member

    if not member:
        return

    user_id = member.id


    # ==================================================
    # 남아있는 성별 선택창 삭제
    # ==================================================

    gender_message_id = PENDING_GENDER_MESSAGES.pop(
        user_id,
        None,
    )

    SELECTED_GENDERS.pop(
        user_id,
        None,
    )

    if gender_message_id is not None:
        try:
            await context.bot.delete_message(
                chat_id=message.chat.id,
                message_id=gender_message_id,
            )
            print(f"{user_id} 성별 선택창 자동삭제 완료")
        except Exception as e:
            print(f"성별 선택창 삭제 오류: {e}")


    # ==================================================
    # 이 사람이 미구독 상태로 나갔다면
    # 저장되어 있던 구독 인증창 삭제
    # ==================================================

    subscription_message_id = (
        PENDING_SUBSCRIPTION_MESSAGES.pop(
            user_id,
            None,
        )
    )

    if subscription_message_id is not None:

        try:
            await context.bot.delete_message(
                chat_id=message.chat.id,
                message_id=subscription_message_id,
            )

            print(
                f"{user_id} 구독 인증창 자동삭제 완료"
            )

        except Exception as e:
            print(
                f"구독 인증창 삭제 오류: {e}"
            )


    # ==================================================
    # Telegram 기본 퇴장 시스템 메시지 삭제
    # ==================================================

    try:
        await message.delete()
        print("퇴장 시스템 메시지 삭제 완료")

    except Exception as e:
        print(f"퇴장 메시지 삭제 오류: {e}")


# ==================================================
# 매일 오전 9시 공지 메시지 만들기
# ==================================================

def build_daily_notice():
    parts = []
    entities = []

    # 첫 줄: 앞쪽 여백 + 움직이는 이모지 5개
    parts.append("       ")
    for emoji_id in NOTICE_TITLE_EMOJI_IDS:
        add_custom_emoji(parts, entities, emoji_id)

    parts.append("\n")

    # 움직이는 이모지 2개 + 공지사항 필수 확인 + 움직이는 이모지 2개
    add_custom_emoji(parts, entities, NOTICE_WARNING_EMOJI_ID)
    add_custom_emoji(parts, entities, NOTICE_WARNING_EMOJI_ID)

    title_start = utf16_len("".join(parts))
    title_text = " 공지사항 필수 확인 "
    parts.append(title_text)

    entities.append(
        MessageEntity(
            type=MessageEntity.BOLD,
            offset=title_start,
            length=utf16_len(title_text),
        )
    )

    add_custom_emoji(parts, entities, NOTICE_WARNING_EMOJI_ID)
    add_custom_emoji(parts, entities, NOTICE_WARNING_EMOJI_ID)

    parts.append("\n\n")

    # 미숙지 문구
    add_custom_emoji(parts, entities, NOTICE_LINE1_EMOJI_ID)
    parts.append(" 미숙지로 인한 불이익은 본인에게 있습니다\n")

    # 여자한테 잘해줘야 합니다 (오프 합니다)
    add_custom_emoji(parts, entities, NOTICE_LINE2_EMOJI_ID)
    parts.append(" 여자한테 ")

    bold_start = utf16_len("".join(parts))
    bold_text = "잘해줘야 합니다"
    parts.append(bold_text)
    entities.append(
        MessageEntity(
            type=MessageEntity.BOLD,
            offset=bold_start,
            length=utf16_len(bold_text),
        )
    )

    parts.append(" ( ")

    off_start = utf16_len("".join(parts))
    off_text = "오프 합니다"
    parts.append(off_text)
    entities.append(
        MessageEntity(
            type=MessageEntity.BOLD,
            offset=off_start,
            length=utf16_len(off_text),
        )
    )

    parts.append(" )\n\n\n")

    # 아래 공지사항 버튼 안내
    add_custom_emoji(parts, entities, NOTICE_SMILE_EMOJI_ID)
    parts.append(" 아래 공지사항 버튼을 눌러 확인하세요.\n")

    # 맨 아래 움직이는 이모지 8개
    for _ in range(8):
        add_custom_emoji(parts, entities, NOTICE_FLAG_EMOJI_ID)

    text = "".join(parts)
    return text, entities


# ==================================================
# 이전 자동공지 삭제
# ==================================================

async def delete_previous_daily_notice(context):
    try:
        chat = await context.bot.get_chat(MAIN_GROUP_ID)
        pinned = chat.pinned_message

        if not pinned:
            return

        bot_user = await context.bot.get_me()

        # 우리 봇이 올린 자동공지일 때만 삭제
        if (
            pinned.from_user
            and pinned.from_user.id == bot_user.id
            and pinned.text
            and "공지사항 필수 확인" in pinned.text
        ):
            try:
                await context.bot.unpin_chat_message(
                    chat_id=MAIN_GROUP_ID,
                    message_id=pinned.message_id,
                )
            except Exception as e:
                print(f"이전 자동공지 고정 해제 오류: {e}")

            try:
                await context.bot.delete_message(
                    chat_id=MAIN_GROUP_ID,
                    message_id=pinned.message_id,
                )
                print("이전 자동공지 삭제 완료")
            except Exception as e:
                print(f"이전 자동공지 삭제 오류: {e}")

    except Exception as e:
        print(f"이전 자동공지 확인 오류: {e}")


# ==================================================
# 새 자동공지 전송 + 고정
# ==================================================

async def send_daily_notice(context):
    await delete_previous_daily_notice(context)

    text, entities = build_daily_notice()

    # 환영메시지와 동일한 6개 인라인 메뉴 버튼 사용
    keyboard = InlineKeyboardMarkup(BUTTONS)

    sent = await context.bot.send_message(
        chat_id=MAIN_GROUP_ID,
        text=text,
        entities=entities,
        reply_markup=keyboard,
    )

    await context.bot.pin_chat_message(
        chat_id=MAIN_GROUP_ID,
        message_id=sent.message_id,
        disable_notification=True,
    )

    print(f"오전 9시 자동공지 등록 및 고정 완료: {sent.message_id}")


# ==================================================
# 공지 자동 유지 루프
# ==================================================

async def daily_notice_loop(app):
    # 메인방 공지가 사라졌는지 주기적으로 확인
    # 텔레그램 1일 자동삭제 등으로 공지가 없어지면 자동으로 다시 생성/고정
    while True:
        try:
            chat = await app.bot.get_chat(MAIN_GROUP_ID)
            pinned = chat.pinned_message
            bot_user = await app.bot.get_me()

            notice_exists = (
                pinned
                and pinned.from_user
                and pinned.from_user.id == bot_user.id
                and pinned.text
                and "공지사항 필수 확인" in pinned.text
            )

            if not notice_exists:
                print("고정 공지가 없습니다. 자동으로 새 공지를 생성합니다.")
                await send_daily_notice(app)

        except Exception as e:
            print(f"공지 자동확인 오류: {e}")

        # 5분마다 확인
        await asyncio.sleep(300)


# ==================================================
# 봇 시작 시 공지 자동 유지 시작
# ==================================================

async def post_init(app):
    asyncio.create_task(daily_notice_loop(app))
    print("공지 자동 유지 기능 시작 완료")


# ==================================================
# Telegram 고정 시스템 메시지 자동 삭제
# ==================================================

async def delete_pin_system_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    message = update.effective_message

    if not message:
        return

    try:
        await message.delete()
        print("고정 시스템 메시지 삭제 완료")
    except Exception as e:
        print(f"고정 시스템 메시지 삭제 오류: {e}")


# ==================================================
# 공지 즉시 테스트 명령어
# 개인채팅에서 /공지테스트
# 메인방 관리자만 실행 가능
# ==================================================

async def test_daily_notice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    message = update.effective_message
    user = update.effective_user

    if not message or not user:
        return

    # 개인채팅에서만 실행
    if message.chat.type != "private":
        return

    try:
        member = await context.bot.get_chat_member(
            chat_id=MAIN_GROUP_ID,
            user_id=user.id,
        )

        if member.status not in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER,
        ):
            await message.reply_text(
                "이 명령어는 서 울 메인방 관리자만 사용할 수 있습니다."
            )
            return

    except Exception as e:
        print(f"공지 테스트 관리자 확인 오류: {e}")
        await message.reply_text(
            "관리자 권한을 확인하지 못했습니다."
        )
        return

    await message.reply_text(
        "공지 테스트를 시작합니다."
    )

    try:
        await send_daily_notice(context)
        await message.reply_text(
            "공지 테스트 완료! 서 울 메인방을 확인해주세요."
        )
    except Exception as e:
        print(f"공지 테스트 오류: {e}")
        await message.reply_text(
            f"공지 테스트 중 오류가 발생했습니다: {e}"
        )


# ==================================================
# 개인채팅 움직이는 이모지 ID 확인
# ==================================================

async def get_emoji_id(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    message = update.effective_message

    if not message:
        return

    found_ids = []

    for entity in message.entities or []:

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


# ==================================================
# 실행
# ==================================================

def main():
    app = (
        Application.builder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )


    # 신규회원
    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            welcome,
        )
    )


    # 회원 퇴장
    # 구독 인증창 + Telegram 퇴장문구 자동삭제
    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.LEFT_CHAT_MEMBER,
            delete_left_member_message,
        )
    )


    # Telegram 고정 시스템 메시지 자동삭제
    # 별도 handler group에서 검사하여 기존 입장/퇴장 handler와 충돌 방지
    app.add_handler(
        MessageHandler(
            filters.ALL,
            delete_pin_system_message,
            block=False,
        ),
        group=1,
    )


    # 성별 선택
    app.add_handler(
        CallbackQueryHandler(
            select_gender,
            pattern=r"^gender:",
        )
    )


    # 구독 완료
    app.add_handler(
        CallbackQueryHandler(
            check_subscription,
            pattern=r"^check_sub:",
        )
    )


    # 공지 즉시 테스트
    # 봇 개인채팅에서 /공지테스트
    app.add_handler(
        CommandHandler(
            "notice_test",
            test_daily_notice,
        )
    )


    # 개인채팅 움직이는 이모지 ID 확인
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
    print("Seoul_freebot 시작")
    try:
        main()
    except Exception as e:
        print(f"봇 시작 오류: {type(e).__name__}: {e}", flush=True)
        raise
