from telegram import Update
from telegram.ext import ContextTypes

from bot.models import Poll, PollOption

from .command import Command


class NewPoll(Command):
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        poll = Poll.create(chat=self.chat, creator=self.user)
        options = [
            option.strip()
            for option in update.message.text.removeprefix("/new_poll").split(",")
        ]

        if len(options) < 2:
            await context.bot.send_message(
                self.chat.chat_id,
                "Ingresaste muy pocas opciones.",
                reply_to_message_id=update.message.message_id,
            )
            return

        for option in options:
            PollOption.create(poll=poll, text=option)

        await poll.send(context.bot)
