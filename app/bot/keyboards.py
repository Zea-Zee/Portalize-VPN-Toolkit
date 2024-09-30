from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.requests import get_plans


start_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Начать ", callback_data="start_command")]
    ]
)

options = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🤑Получить бесплатно на 7 дней🤑', callback_data='trial_button')],
    [InlineKeyboardButton(text='💸Купить подписку сразу💸', callback_data='choose_plan|0')],
    [InlineKeyboardButton(text='🎁Подарить другу🎁', callback_data='present_button')]
    ],
    resize_keyboard=True,
    input_field_placeholder="Попробуйте, это полностью бесплатно)"
)

subscribe = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Подписаться", url='https://t.me/PortalizerVPN')],
    [InlineKeyboardButton(text='Я подписался ✅', callback_data='check_subscription')]
])

platform_options = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Android 🤖', callback_data='choose_tunnel,android')],
    [InlineKeyboardButton(text='iOS 🍏', callback_data='choose_tunnel,android')],
    [InlineKeyboardButton(text='Windows ', callback_data='choose_tunnel,android')],
    [InlineKeyboardButton(text='Android 🤖', callback_data='choose_tunnel,android')],
    [InlineKeyboardButton(text='Назад 🔙', callback_data='back_button')]
    ],
    resize_keyboard=True
)


async def build_plans(type=0):
    plans = (await get_plans(type)).all()
    keyboard = InlineKeyboardBuilder()
    if not plans:
        raise Exception("There are not any plans: build_plans")
    for plan in plans:
        # print(plan.id)
        text = plan.name
        if plan.discount:
            discount_sum = round(plan.price * (plan.discount / 100))
            new_price = round(plan.price - discount_sum)
            text += f" {new_price} рублей (-{round(plan.discount)}% / -{discount_sum}р.)"
        else:
            text += f" {round(plan.price)} рублей"
        callback_data = f"payment|{plan.id}"
        print("callback_data", callback_data)
        keyboard.add(InlineKeyboardButton(text=text, callback_data=callback_data))
    return keyboard.adjust(1).as_markup()


async def build_payment_keyboard(payment_url: str, payment_id: str, price: int):
    payment = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Оплатить {price} рублей", url=payment_url)],
        [InlineKeyboardButton(text='Я оплатил 💲', callback_data=f"check_payment|{payment_id}")]
    ])
    return payment
