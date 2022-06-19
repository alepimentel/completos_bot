from os import environ

import sqlite3
from telegram.ext import Updater, CommandHandler

from models import *


def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hola!",
    )


def main():
    updater = Updater(token=environ["TOKEN"], use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler("start", start)

    dispatcher.add_handler(start_handler)

    updater.start_polling()


if __name__ == "__main__":
    main()
