from os import environ

import sqlite3
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    PollHandler,
)

from commands import start, new_poll
from handlers import confirm_participation, receive_poll_update


def main():
    application = ApplicationBuilder().token(environ["BOT_TOKEN"]).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("new_poll", new_poll))
    application.add_handler(PollHandler(receive_poll_update))
    application.add_handler(CallbackQueryHandler(confirm_participation))

    application.run_polling()


if __name__ == "__main__":
    main()
