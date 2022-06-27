from models import db, Chat, ChatMember, User, Poll, PollOption
from tasks import send_poll


async def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hola!",
    )


@db.transaction()
async def new_poll(update, context):
    chat, _ = Chat.get_or_create(chat_id=update.message.chat.id)
    user, created = User.get_or_create(
        user_id=update.message.from_user.id,
        defaults={
            "username": update.message.from_user.username,
            "bot": update.message.from_user.is_bot,
        },
    )
    if created:
        ChatMember.create(chat=chat, user=user)

    poll = Poll.create(chat=chat, creator=user)
    options = [
        option.strip()
        for option in update.message.text.removeprefix("/new_poll").split(",")
    ]

    if len(options) < 2:
        context.bot.send_message(
            chat.chat_id,
            "Ingresaste muy pocas opciones.",
            reply_to_message_id=update.message.message_id,
        )
        return

    for option in options:
        PollOption.create(poll=poll, text=option)

    poll_response = await context.bot.send_poll(
        chat.chat_id,
        "A dónde vamos?",
        options,
        is_anonymous=False,
        allows_multiple_answers=True,
    )

    poll.poll_id = poll_response.poll.id
    poll.message_id = poll_response.message_id
    poll.save()
