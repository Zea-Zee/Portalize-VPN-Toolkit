import time
import json
import asyncio

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from config import GROUP_ID
import bot.keyboards as kb
import database.requests as rq
from database.requests import get_plan
from payment import create_payment, get_payment_result


router = Router()

with open('./media/bot_replicas.json', 'r', encoding='utf-8') as file:
    bot_replicas = json.load(file)

user_payments = {}


class PaymentProcess(StatesGroup):
    recipient = State()
    plan = State()
    payment = State()
    payment_status = State()


@router.message(CommandStart())
async def handle_start(message: Message):
    id = message.from_user.id
    await rq.set_user(id)
    name = message.from_user.first_name
    await message.answer(f"{name}{bot_replicas['greet']}")
    await first_time_menu(message)


# TODO add check for trial period
async def first_time_menu(message: Message):
    name = message.from_user.first_name
    if True:
        keyboard = await kb.build_menu_keyboard(trial=True)
        await message.answer(f"{name}, {bot_replicas['trial']}", parse_mode='HTML')
    else:
        keyboard = await kb.build_menu_keyboard()
    await message.answer(f"{bot_replicas['menu']}", reply_markup=keyboard)


@router.callback_query(F.data == 'menu_button')
async def second_time_menu(callback: CallbackQuery):
    if True:
        keyboard = await kb.build_menu_keyboard(trial=True)
    else:
        keyboard = await kb.build_menu_keyboard()
    await callback.message.edit_text(f"{bot_replicas['menu']}", reply_markup=keyboard)


@router.callback_query(F.data == 'trial_button')
async def get_trial(callback: CallbackQuery):
    await callback.message.edit_text(bot_replicas['subscribeText'], reply_markup=kb.subscribe_to_channel)
    callback.answer()


@router.callback_query(F.data.startswith('choose_recipient_button'))
async def get_trial(callback: CallbackQuery):
    await callback.message.edit_text(bot_replicas['chooseRecipient'], reply_markup=kb.choose_recipient)
    await callback.answer()


@router.callback_query(F.data.startswith('choose_plan_button|'))
async def get_trial(callback: CallbackQuery):
    type = int(callback.data.split('|')[1])
    reply = await kb.build_plans(type)
    if type == 1:
        replica = 'choosePresentPlan'
    else:
        replica = 'chooseBuyPlan'
    await callback.message.edit_text(bot_replicas[replica], reply_markup=reply)
    callback.answer(bot_replicas['goToPayment'])


@router.callback_query(F.data.startswith('payment|'))
async def make_payment(callback: CallbackQuery):
    plan_id = int(callback.data.split('|')[1])
    user_id = callback.message.from_user.id
    plan = await get_plan(plan_id)
    print(plan)
    price = plan.price
    reply = kb.main_menu
    await callback.message.edit_text(bot_replicas['notRealized'], reply_markup=reply)
    await callback.answer()
    # description = f"Покупка подписки на {plan.name}"
    # payment_url, payment_id = create_payment(price, user_id, description)
    # reply = await kb.build_payment_keyboard(payment_url, payment_id, price)
    # user_payments[user_id] = payment_id
    # await callback.message.edit_text(bot_replicas['goToPayment'], reply_markup=reply)
    # await callback.answer()


# @router.callback_query(F.data.startswith('check_payment|'))
# async def make_payment(callback: CallbackQuery):
#     payment_id = callback.data.split('|')[1]
#     if payment_id
#     payment_result = get_payment_result(payment_id)
#     if payment_result['status'] == 'succeeded':
#         await callback.answer("Оплата прошла успешно, выдаем вам подписку ✅")
#     await callback.answer("Оплата еще не прошла, попробуйте чуть позже ❌")
    # print(json.dumps(check_result))


@router.callback_query(F.data == 'check_subscription')
async def check_subscription(callback: CallbackQuery):
    user_id = callback.from_user.id
    # print(GROUP_ID)
    try:
        member = await callback.bot.get_chat_member(chat_id=GROUP_ID, user_id=user_id)
        if member.status != 'left':
            await callback.answer("Вы подписаны на канал ✅")
            reply = kb.main_menu
            await callback.message.edit_text(bot_replicas['notRealized'], reply_markup=reply)
            await callback.answer()
        else:
            await callback.answer("Вы еще не подписаны на канал ❌", show_alert=True)
    except Exception as e:
        print(f"check_subscription error: {e}")


@router.callback_query(F.data == 'back_button')
async def back_button(callback: CallbackQuery):
    user_id = callback.from_user.id
    last_action, last_callback = pop_action(
        user_id)  # Извлекаем последнее действие

    if last_action:
        action, last_callback = last_action  # Извлекаем функцию и callback
        await action(last_callback)  # Вызываем функцию-обработчик
    else:
        await callback.answer("Нет действий для возврата.")

    # await callback.message.answer(bot_replicas['instructions']['android'][0])

    # file_path = '../db/configs/test.ovpn'
    # file = FSInputFile(file_path)

    # await callback.message.answer_document(file, caption=bot_replicas['instructions']['android'][1])
    # await callback.message.answer(bot_replicas['instructions']['android'][1])
    # await callback.message.answer(bot_replicas['instructions']['android'][2])
    # await callback.message.answer(bot_replicas['instructions']['android'][4], parse_mode='HTML')
