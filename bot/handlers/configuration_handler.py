from datetime import time
import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from .handler import Handler
from bot.models import GatheringsConfiguration
from bot.keyboards.config import ConfigKeyboard


class ConfigurationHandler(Handler):
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if self.data[0] == "main_menu":
            await self.handle_main_menu(update, context)
        elif self.data[0] == "unset":
            await self.handle_unset(update, context)
        elif self.data[0] == "set":
            await self.handle_set(update, context)
        elif self.data[0] == "change_period":
            if len(self.data) == 1:
                await self.handle_change_period(update, context)
            else:
                await self.handle_change_period_option(update, context)
        elif self.data[0] == "change_day":
            if len(self.data) == 1:
                await self.handle_change_day(update, context)
            else:
                await self.handle_change_day_option(update, context)
        elif self.data[0] == "change_time":
            if len(self.data) == 1:
                await self.handle_change_time(update, context)
            else:
                await self.handle_change_time_option(update, context)
        elif self.data[0] == "close":
            await self.handle_close(update, context)

    async def handle_main_menu(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        await ConfigKeyboard(self.chat).back_to_main_menu(update.callback_query)

    async def handle_set(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        config, _ = GatheringsConfiguration.get_or_create(chat=self.chat)
        config.period = 2
        config.save()

        await ConfigKeyboard(config.chat).back_to_main_menu(update.callback_query)

    async def handle_unset(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        config, _ = GatheringsConfiguration.get_or_create(chat=self.chat)
        config.period = 0
        config.save()

        await ConfigKeyboard(config.chat).back_to_main_menu(update.callback_query)

    async def handle_change_period(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        await ConfigKeyboard(self.chat).change_period_menu(update.callback_query)

    async def handle_change_period_option(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        config = self.chat.config
        config.period = int(self.data[-1])
        config.save()

        await ConfigKeyboard(self.chat).back_to_main_menu(update.callback_query)

    async def handle_change_day(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        await ConfigKeyboard(self.chat).change_day_menu(update.callback_query)

    async def handle_change_day_option(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        config = self.chat.config
        config.default_weekday = int(self.data[-1])
        config.save()

        await ConfigKeyboard(self.chat).back_to_main_menu(update.callback_query)

    async def handle_change_time(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        await ConfigKeyboard(self.chat).change_time_menu(update.callback_query)

    async def handle_change_time_option(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        hours, minutes = self.data[-2:]

        config = self.chat.config
        config.default_time = time(int(hours), int(minutes))
        config.save()

        await ConfigKeyboard(self.chat).back_to_main_menu(update.callback_query)

    async def handle_close(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.callback_query.delete_message()
