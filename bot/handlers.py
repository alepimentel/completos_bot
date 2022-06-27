from models import db, Poll, PollOption


@db.transaction()
async def receive_poll_update(update, context):
    poll = Poll.get(Poll.poll_id == update.poll.id)
    for option in update.poll.options:
        poll_option = PollOption.get(
            PollOption.poll == poll, PollOption.text == option.text
        )
        poll_option.votes = option.voter_count
        poll_option.save()

    if poll.chat.member_count() == update.poll.total_voter_count and not poll.closed_at:
        if not update.poll.is_closed:
            await context.bot.stop_poll(poll.chat.chat_id, poll.message_id)
            poll.close()
