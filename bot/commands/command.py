from telegram import Update
from telegram.ext import ContextTypes

from bot.models import Chat, ChatMember, GatheringsConfiguration, User


class Command:
    def setup(self, update: Update) -> None:
        self.chat, chat_created = Chat.get_or_create(chat_id=update.message.chat.id)
        self.user, created = User.get_or_create(
            user_id=update.message.from_user.id,
            defaults={
                "username": update.message.from_user.username,
                "bot": update.message.from_user.is_bot,
            },
        )

        if chat_created:
            GatheringsConfiguration.create(chat=self.chat, period=0)
        if created:
            ChatMember.create(chat=self.chat, user=self.user)

    @classmethod
    def as_func(cls):
        async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            self = cls()
            self.setup(update)

            return await self.handle(update, context)

        return command

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        raise NotImplementedError
