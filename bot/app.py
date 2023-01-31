from os import environ

from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    PollHandler,
    filters,
)

from bot.commands import COMMANDS
from bot.handlers import ConfigurationHandler
from bot.handlers import (
    confirm_participation,
    left_chat_member,
    new_chat_members,
    receive_poll_update,
)


def main():
    application = ApplicationBuilder().token(environ["BOT_TOKEN"]).build()

    for name, Command in COMMANDS.items():
        application.add_handler(CommandHandler(name, Command.as_func()))

    application.add_handler(PollHandler(receive_poll_update))
    application.add_handler(
        CallbackQueryHandler(confirm_participation, pattern="^confirm_participation")
    )
    application.add_handler(
        CallbackQueryHandler(ConfigurationHandler.as_func(), pattern="^config")
    )
    application.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_chat_members)
    )
    application.add_handler(
        MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, left_chat_member)
    )

    application.run_polling()
