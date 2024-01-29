from datetime import datetime

from config import MAX_REQUESTS_PER_DAY
from .models import RequestsCounter


def __reset_request_counter_if_outdated(counter: RequestsCounter):
    """ Обнуляет счётчик запросов, если текущий день отличается от последнего """
    if not counter.last_request_time:
        return

    current_time = datetime.utcnow()

    if current_time.date() > counter.last_request_time.date():
        counter.request_count = 0
        counter.save()


def get_left_requests_count(user_id: int) -> int:
    counter, _ = RequestsCounter.get_or_create(user_id=user_id)

    __reset_request_counter_if_outdated(counter)

    if counter.request_count >= MAX_REQUESTS_PER_DAY:
        return 0
    return MAX_REQUESTS_PER_DAY - counter.request_count


def increase_counter(user_id: int):
    """ Увеличивает счётчик запросов на 1 """
    counter, _ = RequestsCounter.get_or_create(user_id=user_id)

    counter.request_count += 1
    current_time = datetime.utcnow()
    counter.last_request_time = current_time

    counter.save()
