from telegram import Update
from telegram.ext import ContextTypes

from bot.models import Chat, User


class Handler:
    def setup(self, update: Update) -> None:
        self.data = update.callback_query.data.split(":")[1:]

        self.chat = Chat.get(chat_id=update.callback_query.message.chat.id)
        self.user, _ = User.get_or_create(
            user_id=update.callback_query.message.from_user.id,
            defaults={
                "username": update.callback_query.message.from_user.username,
                "bot": update.callback_query.message.from_user.is_bot,
            },
        )

    @classmethod
    def as_func(cls):
        async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            self = cls()
            self.setup(update)

            return await self.handle(update, context)

        return handler

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        raise NotImplementedError
