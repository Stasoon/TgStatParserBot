import os
from typing import Final
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

BOT_TOKEN: Final[str] = os.getenv('BOT_TOKEN', 'define me')
OWNER_IDS: Final[tuple] = tuple(int(i) for i in str(os.getenv('BOT_OWNER_IDS')).split(','))

# Информация о канале, на который необходимо подписаться
CHANNEL_ID = -1002014716981  # -1001946589497
CHANNEL_URL = 'https://t.me/+6XdMekElAUxiYzhi'  # 'https://t.me/+QrZzEvA17Eg4Mjg6'

# Максимальное количество запросов от юзера в сутки
MAX_REQUESTS_PER_DAY: Final[int] = 5
