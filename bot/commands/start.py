from telegram import Update
from telegram.ext import ContextTypes

from .command import Command


class Start(Command):
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await context.bot.send_message(self.chat.chat_id, "Hola!")
