import os
import asyncio
from datetime import datetime, timedelta
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

NOTICE_LINE1_EMOJI_ID = "5210820276748566172"
NOTICE_LINE2_EMOJI_ID = "5213400521301313365"
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
