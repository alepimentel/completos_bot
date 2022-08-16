from datetime import date, datetime, timedelta
from os import environ

from huey import crontab, MemoryHuey
from telegram import Bot

from bot.models import (
    Chat,
    GatheringsConfiguration,
    Meal,
    MealMember,
    Poll,
    PollOption,
    User,
)
from bot.utils import async_to_sync, get_self


huey = MemoryHuey()


@huey.periodic_task(crontab(minute="*/5"))
@async_to_sync
async def close_old_polls():
    bot = Bot(environ["BOT_TOKEN"])

    one_day_ago = datetime.now() - timedelta(days=1)
    polls_to_close = (
        Poll.select(Poll, Chat)
        .join(Chat)
        .where(Poll.created_at <= one_day_ago, Poll.closed_at.is_null())
    )

    for poll in polls_to_close:
        await bot.stop_poll(poll.chat.chat_id, poll.message_id)

        poll.closed_at = datetime.now()
        poll.save()


@huey.periodic_task(crontab(day_of_week=1, hour="*"))
@async_to_sync
async def send_periodic_polls():
    chats = Chat.select().join(GatheringsConfiguration)

    for chat in chats:
        last_poll = (
            Poll.select().where(Poll.chat == chat).order_by(Poll.id.desc()).first()
        )

        print("last_poll", last_poll)
        if last_poll is None or date.today() - last_poll.created_at.date() >= timedelta(
            weeks=chat.config.period
        ):
            await send_default_poll(chat)


async def send_default_poll(chat):
    bot = Bot(environ["BOT_TOKEN"])

    bot_ = await get_self()

    if not chat.default_options:
        await bot.send_message(
            chat.chat_id,
            "No puedo empezar organizar una salida porque el grupo no tiene opciones "
            "configuradas, puedes agregar opciones con el comando /add_option.",
        )
        return

    poll = Poll.create(chat=chat, creator=bot_)
    for option in chat.default_options:
        PollOption.create(poll=poll, text=option.text)

    await poll.send(bot)


@huey.periodic_task(crontab(hour="7"))
async def announce_gatherings():
    bot = Bot(environ["BOT_TOKEN"])

    meals = Meal.select().where(Meal.date == date.today()).join(MealMember).join(User)
    for meal in meals:
        message = f"Recuerda que hoy vamos a {meal.place}!"
        if meal.participants:
            participants = [
                f"@{participant.user.username}" for participant in meal.participants
            ]
            message = +"\nConfirmados: " + ", ".join(participants)

        await bot.send_message(meal.chat.chat_id, message)
