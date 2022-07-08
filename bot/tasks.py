from datetime import datetime, timedelta
from os import environ

from huey import crontab, MemoryHuey
from telegram import Bot

from bot.models import Chat, Poll
from bot.utils import async_to_sync


huey = MemoryHuey()


@huey.periodic_task(crontab(minute="*/5"))
@async_to_sync
async def close_old_polls():
    bot = Bot(environ["BOT_TOKEN"])

    one_day_ago = datetime.now() - timedelta(days=1)
    polls_to_close = (
        Poll.select(Poll, Chat)
        .join(Chat)
        .where(Poll.created_at <= one_day_ago, Poll.closed_at == None)
    )

    for poll in polls_to_close:
        await bot.stop_poll(poll.chat.chat_id, poll.message_id)

        poll.closed_at = datetime.now()
        poll.save()
