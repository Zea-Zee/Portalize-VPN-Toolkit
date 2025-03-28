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
    # description = f"Покупка подписки на {plan.name}"
    # payment_url, payment_id = create_payment(price, user_id, description)
    # reply = await kb.build_payment_keyboard(payment_url, payment_id, price)
    # user_payments[user_id] = payment_id
    # await callback.message.edit_text(
    #     bot_replicas['goToPayment'],
    #     reply_markup=reply
    # )
    # await callback.answer()


# @router.callback_query(F.data.startswith('check_payment|'))
# async def check_payment(callback: CallbackQuery):
#     payment_id = callback.data.split('|')[1]
#     payment_result = get_payment_result(payment_id)
#     if payment_result['status'] == 'succeeded':
#         await callback.answer("Оплата прошла успешно, выдаем вам подписку ✅")
#     await callback.answer("Оплата еще не прошла, попробуйте чуть позже ❌")
#     # print(json.dumps(check_result))


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
                async with X3API(host=XUI_HOST, user=XUI_USER, password=XUI_PASSWORD) as api:
                    current_time = datetime.now(timezone.utc)
                    expiry_time = int(add_date(current_time, days=30).timestamp())
                    sub_result = await api.create_client(tg_id=tg_id, tg_username=tg_username, expiryTime=expiry_time)
                    if sub_result is not None and sub_result['success']:
                        await callback.message.edit_text(
                            f"Ваша подписка активирована! ✅\nСкопируйте ссылку и вставьте в приложение:\n'{sub_result['config']}'")
                        print(f"Клиент с email {client_email} успешно создан.")
                    else:
                        await callback.message.answer(
                            "Произошла ошибка при создании подписки. "
                            "Попробуйте позже."
                        )
            except Exception as e:
                print(f"Ошибка создания подписки: {e}")
                await callback.message.answer(
                    "Произошла ошибка при активации вашей подписки. "
                    "Наши специалисты уже работают над решением проблемы."
                )
        else:
            await callback.answer(
                "Вы еще не подписаны на канал ❌",
                show_alert=True
            )
    except Exception as e:
        print(f"check_subscription error: {e}")
        await callback.message.answer(
            "Произошла ошибка при проверке подписки. "
            "Пожалуйста, попробуйте позже."
        )


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

    # await callback.message.answer(bot_replicas['instructions']['android'][0])

    # file_path = '../db/configs/test.ovpn'
    # file = FSInputFile(file_path)

    # await callback.message.answer_document(file, caption=bot_replicas['instructions']['android'][1])
    # await callback.message.answer(bot_replicas['instructions']['android'][1])
    # await callback.message.answer(bot_replicas['instructions']['android'][2])
    # await callback.message.answer(bot_replicas['instructions']['android'][4], parse_mode='HTML')
