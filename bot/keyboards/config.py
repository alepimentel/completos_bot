from gettext import ngettext

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.models import GatheringsConfiguration

KEYBOARD_GATHERINGS_ENABLED = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "Desctivar juntas automáticas", callback_data="config:unset"
            )
        ],
        [
            InlineKeyboardButton(
                "Cambiar periodicidad", callback_data="config:change_period"
            ),
        ],
        [
            InlineKeyboardButton("Cambiar día", callback_data="config:change_day"),
            InlineKeyboardButton("Cambiar hora", callback_data="config:change_time"),
        ],
        [
            InlineKeyboardButton("Cerrar menú", callback_data="config:close"),
        ],
    ]
)
KEYBOARD_GATHERINGS_DISABLED = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "Activar juntas automáticas", callback_data="config:set"
            )
        ],
        [
            InlineKeyboardButton("Cerrar menú", callback_data="config:close"),
        ],
    ]
)


class ConfigKeyboard:
    def __init__(self, chat):
        self.chat = chat
        self.config = chat.config

    async def main_menu(self, bot):
        if self.chat.config.period == 0:
            await bot.send_message(
                self.chat.chat_id,
                "Configuación de las salidas periódicas\n\n"
                "(Las juntas periódicas están desactivadas)",
                reply_markup=KEYBOARD_GATHERINGS_DISABLED,
            )
        else:
            await bot.send_message(
                self.chat.chat_id,
                "Configuación de las salidas periódicas\n\n"
                "La configuración es la siguiente:\n"
                f" - Periodo: cada {self.chat.config.period} {ngettext('semana', 'semanas', self.config.period)}\n"
                f" - Día por defecto: {GatheringsConfiguration.WEEKDAYS[self.config.default_weekday][1]}\n"
                f" - Hora por defecto: {self.config.default_time.isoformat('minutes')}",
                reply_markup=KEYBOARD_GATHERINGS_ENABLED,
            )

    async def back_to_main_menu(self, callback_query):
        if self.config.period == 0:
            await callback_query.edit_message_text(
                "Configuación de las salidas periódicas\n\n"
                "(Las juntas periódicas están desactivadas)",
                reply_markup=KEYBOARD_GATHERINGS_DISABLED,
            )
        else:
            await callback_query.edit_message_text(
                "Configuación de las salidas periódicas\n\n"
                "La configuración es la siguiente:\n"
                f" - Periodo: {self.config.period} {ngettext('semana', 'semanas', self.config.period)}\n"
                f" - Día por defecto: {GatheringsConfiguration.WEEKDAYS[self.config.default_weekday][1]}\n"
                f" - Hora por defecto: {self.config.default_time.isoformat('minutes')}",
                reply_markup=KEYBOARD_GATHERINGS_ENABLED,
            )

    async def change_period_menu(self, callback_query):
        await callback_query.edit_message_text(
            "Configuación de la periodicidad de las salidas",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            f"Cada {n} {ngettext('semana', 'semanas', n)}",
                            callback_data=f"config:change_period:{n}",
                        )
                    ]
                    for n in range(1, 9)
                ]
                + [[InlineKeyboardButton("Volver", callback_data="config:main_menu")]]
            ),
        )

    async def change_time_menu(self, callback_query):
        await callback_query.edit_message_text(
            "Elige la hora por defecto de las salidas",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            f"{h}:00",
                            callback_data=f"config:change_time:{h}:00",
                        ),
                        InlineKeyboardButton(
                            f"{h}:30",
                            callback_data=f"config:change_time:{h}:30",
                        ),
                    ]
                    for h in range(0, 24)
                ]
                + [[InlineKeyboardButton("Volver", callback_data="config:main_menu")]]
            ),
        )

    async def change_day_menu(self, callback_query):
        await callback_query.edit_message_text(
            "Elige el día por defecto de las salidas",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            weekday[1].title(),
                            callback_data=f"config:change_day:{weekday[0]}",
                        )
                    ]
                    for weekday in GatheringsConfiguration.WEEKDAYS
                ]
                + [[InlineKeyboardButton("Volver", callback_data="config:main_menu")]]
            ),
        )
