from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, StateFilter

from src.filters.is_subscriber import IsSubscriberFilter
from src.keyboards.user import UserKeyboards
from src.messages.user import UserMessages
from src.database.users import create_user_if_not_exist
from src.database.requests_counter import get_left_requests_count, increase_counter
from src.utils import TgStatParser, logger


class SubscribeCheckingStates(StatesGroup):
    check_subscription = State()


async def handle_start_command(message: Message, state: FSMContext):
    await state.clear()

    user = message.from_user
    create_user_if_not_exist(telegram_id=user.id, firstname=user.first_name, username=user.username)

    text = UserMessages.get_welcome(user_name=user.first_name)
    await message.answer(text=text)

    if not await IsSubscriberFilter.is_user_subscribed(bot=message.bot, user_id=message.from_user.id):
        await handle_unsubscribed_search_message(message=message, state=state)
    else:
        await message.answer(text=UserMessages.get_prompt_for_requests())


async def handle_unsubscribed_search_message(message: Message, state: FSMContext):
    await message.answer(
        text=UserMessages.get_subscription_needed(),
        reply_markup=UserKeyboards.get_need_to_subscribe()
    )
    await state.set_state(SubscribeCheckingStates.check_subscription)


async def handle_check_subscribe_callback(callback: CallbackQuery, state: FSMContext):
    is_sub = await IsSubscriberFilter.is_user_subscribed(bot=callback.bot, user_id=callback.from_user.id)

    if not is_sub:
        await callback.answer(text='Вы не подписались!')
        return

    await state.clear()
    await callback.answer(text='😉 Можете пользоваться ботом!')
    await callback.message.answer(text=UserMessages.get_prompt_for_requests())
    await callback.message.delete()


async def handle_search_message(message: Message):
    if get_left_requests_count(user_id=message.from_user.id) <= 0:
        await message.answer(UserMessages.get_day_requests_exceeded())
        return

    if len(message.text) >= 100:
        await message.answer(text=UserMessages.get_requests_too_long())
        return

    increase_counter(user_id=message.from_user.id)
    timer_message = await message.answer(UserMessages.get_please_wait_for_result())

    posts = None
    try:
        posts = await TgStatParser.search_key_word(key=message.text)
    except Exception as e:
        logger.error(e)

    await timer_message.delete()
    if not posts:
        await message.reply(text=UserMessages.get_not_found())
    else:
        text = UserMessages.get_request_response(request=message.text, result=posts[:30])
        await message.answer(text=text)

    left_requests = get_left_requests_count(user_id=message.from_user.id)
    if left_requests > 0:
        text = UserMessages.get_prompt_for_requests_left(left_requests_count=left_requests)
        await message.answer(text)


def register_user_handlers(router: Router):
    # Команда /start
    router.message.register(handle_start_command, CommandStart())

    # Поиск если не подписан
    router.message.register(
        handle_unsubscribed_search_message,
        StateFilter(default_state, SubscribeCheckingStates),
        IsSubscriberFilter(should_be_sub=False)
    )
    # Кнопка "Проверить подписку"
    router.callback_query.register(
        handle_check_subscribe_callback, F.data == 'check_subscribe', SubscribeCheckingStates.check_subscription
    )

    # Поиск по базе tgstat
    router.message.register(handle_search_message, StateFilter(default_state), IsSubscriberFilter(should_be_sub=True))
