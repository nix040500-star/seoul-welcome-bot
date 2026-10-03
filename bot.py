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
