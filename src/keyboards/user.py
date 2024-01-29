from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

from config import CHANNEL_URL


class UserKeyboards:

    @staticmethod
    def get_need_to_subscribe() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='Подписаться', url=CHANNEL_URL)
        builder.button(text='✅ Проверить', callback_data='check_subscribe')

        builder.adjust(1)
        return builder.as_markup()
