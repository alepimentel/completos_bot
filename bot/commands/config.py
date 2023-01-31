from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from .command import Command
from bot.models import GatheringsConfiguration
from bot.keyboards.config import ConfigKeyboard


class Config(Command):
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await ConfigKeyboard(self.chat).main_menu(context.bot)
