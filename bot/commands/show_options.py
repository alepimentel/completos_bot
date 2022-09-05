from telegram import Update
from telegram.ext import ContextTypes

from .command import Command
from bot.models import db


class ShowOptions(Command):
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if self.chat.default_options:
            await context.bot.send_message(
                self.chat.chat_id,
                "Las opciones son:\n -"
                + "\n - ".join(
                    map(
                        lambda default_option: default_option.text,
                        self.chat.default_options,
                    )
                ),
            )
        else:
            await context.bot.send_message(self.chat.chat_id, "No hay opciones.")
