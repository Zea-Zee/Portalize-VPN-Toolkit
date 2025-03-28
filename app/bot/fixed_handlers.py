import json

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State

from datetime import datetime, timezone

from config import GROUP_ID, XUI_HOST, XUI_USER, XUI_PASSWORD
import bot.keyboards as kb
import database.requests as rq
from database.requests import get_plan
from manage_3xui import X3API, add_date


# Инициализировать API клиент позже, а не глобально
router = Router()

with open('./media/bot_replicas.json', 'r', encoding='utf-8') as file:
    bot_replicas = json.load(file)

user_payments = {}
# Словарь для хранения истории действий пользователей
user_actions = {}


class PaymentProcess(StatesGroup):
    recipient = State()
    plan = State()
    payment = State()
    payment_status = State()


@router.message(CommandStart())
async def handle_start(message: Message):
    id = message.from_user.id
    username = message.from_user.username
    await rq.set_user(id, username)
    name = message.from_user.first_name
    await message.answer(f"{name}{bot_replicas['greet']}")
    await first_time_menu(message)


# TODO add check for trial period
async def first_time_menu(message: Message):
    name = message.from_user.first_name
    tg_id = message.from_user.id
    user_subscriptions = await rq.get_user_subscriptions(tg_id)
    print(user_subscriptions)
    if len(user_subscriptions) == 0:
        keyboard = await kb.build_menu_keyboard(trial=True)
        await message.answer(
            f"{name}, {bot_replicas['trial']}",
            parse_mode='HTML'
        )
    else:
        keyboard = await kb.build_menu_keyboard()
    await message.answer(f"{bot_replicas['menu']}", reply_markup=keyboard)


@router.callback_query(F.data == 'menu_button')
async def second_time_menu(callback: CallbackQuery):
    tg_id = callback.from_user.id
    user_subscriptions = await rq.get_user_subscriptions(tg_id)
    print(user_subscriptions)
    if len(user_subscriptions) == 0:
        keyboard = await kb.build_menu_keyboard(trial=True)
    else:
        keyboard = await kb.build_menu_keyboard()
    await callback.message.edit_text(
        f"{bot_replicas['menu']}",
        reply_markup=keyboard
    )


@router.callback_query(F.data == 'trial_button')
async def get_trial_subscription(callback: CallbackQuery):
    await callback.message.edit_text(
        bot_replicas['subscribeText'],
        reply_markup=kb.subscribe_to_channel
    )
    await callback.answer()


@router.callback_query(F.data.startswith('choose_recipient_button'))
async def choose_recipient(callback: CallbackQuery):
    await callback.message.edit_text(
        bot_replicas['chooseRecipient'],
        reply_markup=kb.choose_recipient
    )
    await callback.answer()


@router.callback_query(F.data.startswith('choose_plan_button|'))
async def choose_plan(callback: CallbackQuery):
    type_id = int(callback.data.split('|')[1])
    reply = await kb.build_plans(type_id)
    if type_id == 2:
        replica = 'chooseBuyPlan'
    elif type_id == 3:
        replica = 'choosePresentPlan'
    await callback.message.edit_text(bot_replicas[replica], reply_markup=reply)
    await callback.answer(bot_replicas['goToPayment'])


@router.callback_query(F.data.startswith('payment|'))
async def make_payment(callback: CallbackQuery):
    plan_id = int(callback.data.split('|')[1])
    plan = await get_plan(plan_id)
    print(plan)
    reply = kb.main_menu
    await callback.message.edit_text(
        bot_replicas['notRealized'],
        reply_markup=reply
    )
    await callback.answer()


@router.callback_query(F.data == 'check_subscription')
async def check_subscription(callback: CallbackQuery):
    user_id = callback.from_user.id
    try:
        # Проверяем наличие подписки на канал
        member = await callback.bot.get_chat_member(
            chat_id=GROUP_ID, user_id=user_id
        )
        
        if member.status != 'left':
            await callback.answer("Вы подписаны на канал ✅")
            tg_id = callback.from_user.id
            tg_username = callback.from_user.username
            client_email = f"{tg_id}_@{tg_username}"

            try:
                # Создаем клиента через асинхронный API
                async with X3API(XUI_HOST, XUI_USER, XUI_PASSWORD) as api:
                    curr_time = datetime.now(timezone.utc)
                    # Подписка на 1 год
                    expiry = add_date(curr_time, years=1)
                    expiry_ts = int(expiry.timestamp())
                    
                    sub_result = await api.create_client(
                        email=client_email, 
                        expiryTime=expiry_ts
                    )
                    
                    if sub_result is None:
                        await callback.message.answer(
                            "Ваша подписка активирована! ✅"
                        )
                    else:
                        msg = "Произошла ошибка при создании подписки. "
                        msg += "Попробуйте позже."
                        await callback.message.answer(msg)
            except Exception as e:
                print(f"Ошибка создания подписки: {e}")
                msg = "Произошла ошибка при активации вашей подписки. "
                msg += "Наши специалисты уже работают над решением проблемы."
                await callback.message.answer(msg)
        else:
            await callback.answer(
                "Вы еще не подписаны на канал ❌",
                show_alert=True
            )
    except Exception as e:
        print(f"check_subscription error: {e}")
        msg = "Произошла ошибка при проверке подписки. "
        msg += "Пожалуйста, попробуйте позже."
        await callback.message.answer(msg)


def save_action(user_id, action, callback):
    """Сохраняет действие пользователя для возможности возврата."""
    if user_id not in user_actions:
        user_actions[user_id] = []
    user_actions[user_id].append((action, callback))


def pop_action(user_id):
    """Извлекает последнее действие пользователя."""
    if user_id in user_actions and user_actions[user_id]:
        return user_actions[user_id].pop()
    return None, None


@router.callback_query(F.data == 'back_button')
async def back_button(callback: CallbackQuery):
    user_id = callback.from_user.id
    last_action, last_callback = pop_action(user_id)

    if last_action:
        await last_action(last_callback)  # Вызываем функцию-обработчик
    else:
        await callback.answer("Нет действий для возврата.") 