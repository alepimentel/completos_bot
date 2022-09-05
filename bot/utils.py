import asyncio
import functools
from os import environ

from telegram import Bot

from bot.models import User


def wait_for(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


async def get_self():
    bot = Bot(environ["BOT_TOKEN"])

    bot_ = await bot.get_me()
    bot_user, _ = User.get_or_create(
        user_id=bot_.id,
        defaults={
            "first_name": bot_.first_name,
            "username": bot_.username,
            "bot": bot_.is_bot,
        },
    )

    return bot_user
