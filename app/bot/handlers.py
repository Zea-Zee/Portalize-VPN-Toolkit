import time
import json
import asyncio

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command

from config import GROUP_ID
import bot.keyboards as kb
import database.requests as rq
from database.requests import get_plan
from payment import create_payment, get_payment_result


router = Router()

with open('./media/bot_replicas.json', 'r', encoding='utf-8') as file:
    bot_replicas = json.load(file)

user_messages = {}
user_payments = {}


async def send_options(message: Message, edit=False):
    user_id = message.from_user.id
    if edit:
        msg = await message.edit_text(bot_replicas['chooseOption'], reply_markup=kb.options)
    else:
        msg = await message.answer(bot_replicas['chooseOption'], reply_markup=kb.options)
    user_messages[user_id] = msg


@router.message(CommandStart())
async def handle_start(message: Message):
    await rq.set_user(message.from_user.id)
    name = message.from_user.first_name
    await message.reply(f"{name}{bot_replicas['greet']}")
    await send_options(message)


@router.callback_query(F.data == 'back_button')
async def back_to_start(callback: CallbackQuery):
    print(callback)
    print(user_messages)
    user_id = callback.from_user.id
    if user_id in user_messages:
        await callback.message.edit_text(
            text=bot_replicas['chooseOption'],
            reply_markup=kb.options
        )
    callback.answer('Вы вернулись назад')


@router.callback_query(F.data == 'trial_button')
async def get_trial(callback: CallbackQuery):
    await callback.message.edit_text(bot_replicas['subscribeText'], reply_markup=kb.subscribe)
    callback.answer()


@router.callback_query(F.data.startswith('choose_plan|'))
async def get_trial(callback: CallbackQuery):
    type = int(callback.data.split('|')[1])
    reply = await kb.build_plans(type)
    await callback.message.edit_text(bot_replicas['chooseBuyPlan'], reply_markup=reply)
    callback.answer(bot_replicas['goToPayment'])


@router.callback_query(F.data.startswith('payment|'))
async def make_payment(callback: CallbackQuery):
    plan_id = int(callback.data.split('|')[1])
    user_id = callback.message.from_user.id
    plan = await get_plan(plan_id)
    print(plan)
    price = plan.price
    description = f"Покупка подписки на {plan.name}"
    payment_url, payment_id = create_payment(price, user_id, description)
    reply = await kb.build_payment_keyboard(payment_url, payment_id, price)
    user_payments[user_id] = payment_id
    await callback.message.edit_text(bot_replicas['goToPayment'], reply_markup=reply)
    await callback.answer()


@router.callback_query(F.data.startswith('check_payment|'))
async def make_payment(callback: CallbackQuery):
    payment_id = callback.data.split('|')[1]
    payment_result = get_payment_result(payment_id)
    if payment_result['status'] == 'succeeded':
        await callback.answer("Оплата прошла успешно, выдаем вам подписку✅")
    await callback.answer("Оплата еще не прошла, попробуйте чуть позже❌")
    # print(json.dumps(check_result))


@router.callback_query(F.data == 'check_subscription')
async def check_subscription(callback: CallbackQuery):
    user_id = callback.from_user.id
    print(GROUP_ID)

    try:
        member = await callback.bot.get_chat_member(chat_id=GROUP_ID, user_id=user_id)
        if member.status != 'left':
            await callback.answer("Вы подписаны на канал ✅")
        else:
            await callback.answer("Вы не подписаны на канал ❌", show_alert=True)
    except Exception as e:
        print(f"check_subscription error: {e}")

    # await callback.message.answer(bot_replicas['instructions']['android'][0])

    # file_path = '../db/configs/test.ovpn'
    # file = FSInputFile(file_path)

    # await callback.message.answer_document(file, caption=bot_replicas['instructions']['android'][1])
    # await callback.message.answer(bot_replicas['instructions']['android'][1])
    # await callback.message.answer(bot_replicas['instructions']['android'][2])
    # await callback.message.answer(bot_replicas['instructions']['android'][4], parse_mode='HTML')
