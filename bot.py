

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
            "공지테스트",
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
