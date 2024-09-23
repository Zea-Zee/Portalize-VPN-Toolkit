import time

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command

import keyboards as kb


router = Router()


@router.message(CommandStart())
async def handle_start(message: Message):
    print("Start message")
    await message.reply(f"""
    {message.from_user.first_name}, приветствуем в Portalizer👋!
Здесь ты сможешь подключить скоростные анонимные туннели для защиты интернет трафика🔐.
Благодаря этому ты сможешь, к примеру, безопасно смотреть видео в 4K на ЛЮБЫХ площадках💨.
Или листать ленту ЛЮБЫХ соцсетей🏄‍♀️.
    """
    )

    await message.answer("Похоже вы у нас впервые, предлагаем вам полностью бесплатный пробный период, от вас ничего не потребуется", reply_markup=kb.trial)


@router.callback_query(F.data == 'get_trial')
async def get_trial(callback: CallbackQuery):
    await callback.message.answer('Оформляем')
    callback.answer('Успешно выдали вам ключ😎')

    await callback.message.answer('Шаг 1. Установи на устройство OpenVPN клиент:\nhttps://play.google.com/store/apps/details?id=net.openvpn.openvpn&hl=ru')

    file_path = './db/configs/test.ovpn'
    file = FSInputFile(file_path)

    await callback.message.answer_document(file, caption='Шаг 2. Нажми на ☝️ этот файл и открой его через OpenVPN (он должен быть скачан к этому времени).')
    await callback.message.answer('Шаг 3. Теперь просто нажми на кнопку-слайдер⏩ и пользуйся в удовольствие.')
    await callback.message.answer('Шаг 4. Убедись в качестве нашей работы, посмотрев свой новый IP на https://2ip.ru \nПроверь скорость на https://www.speedtest.net/.')
    await callback.message.answer('❗️<b>ВНИМАНИЕ</b>❗️ данный туннель предназначен только для одного устройства, <i>при попытке включить его на другом устройстве vpn просто отключится</i>, для получения нового повторите действия, вам доступно еще 1/2', parse_mode='HTML')



@router.callback_query(F.data == 'start_command')
async def get_started(callback: CallbackQuery):
    name = callback.message.from_user.first_name
    await callback.message.answer(f"""
    {name}, приветствуем в Portalizer👋!
Здесь ты сможешь подключить скоростные анонимные туннели для защиты интернет трафика🔐.
Благодаря этому ты сможешь, к примеру, безопасно смотреть видео в 4K на ЛЮБЫХ площадках💨.
Или листать ленту ЛЮБЫХ соцсетей🏄‍♀️.
    """
    )
