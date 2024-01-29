from aiogram import html
from src.utils import PostData

from config import MAX_REQUESTS_PER_DAY


class UserMessages:

    @staticmethod
    def get_welcome(user_name: str) -> str:
        return (
            f'👋 Привет, {html.quote(user_name)}! \n'
            'Это бот от канала <b>Кнопка Заказы</b>. Он позволяет находить товары, которые рекламировались '
            'в Телеграм каналах. \n\n'
            '🔎 <b>Есть три варианта поиска:</b> \n'
            '1. По артикулу - вы вводите артикул интересуемого товара. \n'
            '2. По ссылке - Вставляете ссылку на товар. \n'
            '3. По поисковому запросу - например "Платье женское" \n'
        )

    @staticmethod
    def get_subscription_needed() -> str:
        return 'Для того, чтобы пользоваться ботом, подпишитесь на канал:'

    @staticmethod
    def get_prompt_for_requests() -> str:
        return (
            f'⭐ В день вам доступно {MAX_REQUESTS_PER_DAY} бесплатных запросов. \n\n'
            f'🔍 Введите интересующий вас:'
        )

    @staticmethod
    def get_prompt_for_requests_left(left_requests_count: int) -> str:
        return (
            f'⭐ Осталось бесплатных запросов на сегодня: {left_requests_count} \n\n'
            f'🔍 Введите интересующий вас:'
        )

    @staticmethod
    def get_please_wait_for_result() -> str:
        return 'Ваш запрос находится в обработке. \n⏰ Поиск займёт 1-2 минуты'

    @classmethod
    def get_request_response(cls, request: str, result: list[PostData]) -> str:
        header_text = f'🔍 По запросу <b>"{request}"</b> \nНайдено (за последние 7 дней):'
        results_text = '\n\n'.join([
            f"{n}. {cls.get_post_description(post)} "
            for n, post in enumerate(result, start=1)
        ])
        footer_text = (
            '———————————————— \n'
            'Консультации по внешней рекламе на маркетплейсах. Закрытый телеграм канал по блоггерам, группам где мы '
            'рекламируемся. Интересует? Напишите @knopkazakazyy'
        )
        return f"{header_text} \n\n{results_text} \n\n{footer_text}"

    @staticmethod
    def get_post_description(post_data: PostData) -> str:
        text = (
            f"<a href='{post_data.source_url}'>{html.quote(post_data.source_title)}</a> \n"
            f"📆 Дата публикации: {post_data.publication_date} \n"
            f"👀 Просмотров: {post_data.views_count} \n"
            f"📲 Репостов: {post_data.reposts_count} \n"
            f"🔗 <a href='{post_data.post_url}'>Ссылка на пост</a>"
        )
        return text

    @staticmethod
    def get_not_found() -> str:
        return 'К сожалению, не удалось найти ничего по вашему запросу 😞'

    @staticmethod
    def get_requests_too_long() -> str:
        return '❌ Ваш запрос слишком длинный! \n\nПожалуйста, сократите его до 100 символов.'

    @staticmethod
    def get_day_requests_exceeded() -> str:
        return (
            f'❌ Лимит запросов на сегодня превышен. \n\n'
            f'Завтра Вам будут снова доступны {MAX_REQUESTS_PER_DAY} запросов.'
        )
