from telegram import Update
from telegram.ext import ContextTypes

from .command import Command


class About(Command):
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await context.bot.send_message(
            self.chat.chat_id,
            "Soy un bot para organizar salidas periódicas\\!\n\n"
            "Si tengo cualquier problema, puedes reportarlo en "
            "[mi repositorio](https://github.com/alepimentel/completos_bot)\\.",
            parse_mode="MarkdownV2",
        )
