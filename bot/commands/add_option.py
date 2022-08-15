from telegram import Update
from telegram.ext import ContextTypes

from .command import Command
from bot.models import DefaultOption


class AddOption(Command):
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        option = update.message.text.removeprefix("/add_option").strip()
        DefaultOption.create(chat=self.chat, text=option)

        await context.bot.send_message(
            self.chat.chat_id,
            f"👌 ({option})",
            reply_to_message_id=update.message.message_id,
        )
