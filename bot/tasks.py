from datetime import date, datetime, timedelta
from os import environ

from huey import SqliteHuey, crontab
from peewee import fn
from telegram import Bot

from bot.models import (
    Chat,
    DefaultOption,
    GatheringsConfiguration,
    Meal,
    MealMember,
    Poll,
    PollOption,
    User,
)
from bot.utils import get_self, wait_for

huey = SqliteHuey("/var/lib/sqlite/huey.db")


@huey.periodic_task(crontab(minute="*/5"))
@wait_for
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
@wait_for
async def send_periodic_polls():
    chats = (
        Chat.select()
        .join(GatheringsConfiguration)
        .where(GatheringsConfiguration.period > 0)
        .switch(Chat)
        .join(DefaultOption)
        .group_by(GatheringsConfiguration)
        .having(fn.Count(DefaultOption.id) > 0)
    )

    for chat in chats:
        if chat.config.should_send_poll():
            if chat.default_options.count() == 1:
                await send_default_meal(chat)
            else:
                await send_default_poll(chat)


async def send_default_meal(chat):
    bot = Bot(environ["BOT_TOKEN"])
    bot_ = await get_self()

    meal = Meal.create(
        chat=chat,
        host=bot_,
        place=chat.default_options.get().text,
        date=chat.config.next_default_day(),
    )

    await bot.send_message(
        chat.chat_id,
        f"Esta semana toca junta! Nos vemos en {meal.place} el {meal.date}. Recuerda "
        "que puedes agregar más opciones con el comando /add_option",
    )


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
