from os import environ

from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    filters,
    MessageHandler,
    PollHandler,
)

from bot.commands import NewPoll, Start
from bot.handlers import (
    confirm_participation,
    receive_poll_update,
    new_chat_members,
    left_chat_member,
)


def main():
    application = ApplicationBuilder().token(environ["BOT_TOKEN"]).build()

    application.add_handler(CommandHandler("start", Start().as_func()))
    application.add_handler(CommandHandler("new_poll", NewPoll().as_func()))
    application.add_handler(PollHandler(receive_poll_update))
    application.add_handler(CallbackQueryHandler(confirm_participation))
    application.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_chat_members)
    )
    application.add_handler(
        MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, left_chat_member)
    )

    application.run_polling()
