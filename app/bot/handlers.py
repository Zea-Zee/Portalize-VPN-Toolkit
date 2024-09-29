import time
import json

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command


from config import GROUP_ID
import bot.keyboards as kb


router = Router()

with open('./media/bot_replicas.json', 'r', encoding='utf-8') as file:
    bot_replicas = json.load(file)

user_messages = {}


async def send_options(message: Message, edit=False):
    user_id = message.from_user.id
    if edit:
        msg = await message.edit_text(bot_replicas['chooseOption'], reply_markup=kb.options)
    else:
        msg = await message.answer(bot_replicas['chooseOption'], reply_markup=kb.options)
    user_messages[user_id] = msg


@router.message(CommandStart())
async def handle_start(message: Message):
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


@router.callback_query(F.data == 'buy_button')
async def get_trial(callback: CallbackQuery):
    callback.answer(bot_replicas['goToPayment'])
    await callback.message.edit_text(bot_replicas['chooseBuyPlan'], reply_markup=kb.buy_plans)


@router.callback_query(F.data == 'present_button')
async def get_trial(callback: CallbackQuery):
    callback.answer(bot_replicas['goToPayment'])
    await callback.message.edit_text(bot_replicas['choosePresentPlan'], reply_markup=kb.gift_plans)


@router.callback_query(F.data == 'payment')
async def make_payment(callback: CallbackQuery):
    await callback.answer(bot_replicas['notRealized'], show_alert=True)
    await send_options(callback.message, True)


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
