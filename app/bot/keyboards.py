from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.requests import get_plans


start_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отлично, поехали 🚀 ", callback_data="menu_button")]
    ]
)


async def build_menu_keyboard(trial: bool = False):
    keyboard = InlineKeyboardBuilder()
    if trial:
        keyboard.add(InlineKeyboardButton(text='🤑Попробовать VPN бесплатно🤑', callback_data='trial_button'))
    keyboard.add(InlineKeyboardButton(text='💸 Купить подписку 💸', callback_data='choose_recipient_button'))
    keyboard.add(InlineKeyboardButton(text='⚙️ Техподдержка ⚙️', callback_data='support_button'))
    keyboard.add(InlineKeyboardButton(text='📖 Инструкции 📖', callback_data='instructions_button'))
    keyboard.add(InlineKeyboardButton(text='🧍Реферальная программа🧍‍♀️', callback_data='referal_button'))
    return keyboard.adjust(1).as_markup()

main_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ МЕНЮ ↩️", callback_data="menu_button")]
    ]
)

subscribe_to_channel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Подписаться", url='https://t.me/PortalizerVPN')],
    [InlineKeyboardButton(text='Я подписался ✅', callback_data='check_subscription')],
    [InlineKeyboardButton(text='Назад ◀️', callback_data='menu_button')]
])

choose_recipient = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Купить себе 🥰", callback_data='choose_plan_button|2')],
    [InlineKeyboardButton(text='Купить в подарок 🎁', callback_data='choose_plan_button|3')],
    [InlineKeyboardButton(text='Назад ◀️', callback_data='menu_button')]
])

platform_options = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Android 🤖', callback_data='choose_tunnel,android')],
    [InlineKeyboardButton(text='iOS 🍏', callback_data='choose_tunnel,android')],
    [InlineKeyboardButton(text='Windows ', callback_data='choose_tunnel,android')],
    [InlineKeyboardButton(text='Linux 🐧', callback_data='choose_tunnel,android')],
    [InlineKeyboardButton(text='Назад 🔙', callback_data='back_button')]
    ],
    resize_keyboard=True
)


async def build_plans(type=0):
    plans = (await get_plans(type)).all()
    keyboard = InlineKeyboardBuilder()
    if not plans:
        raise Exception("There are not any plans: build_plans")

    sorted_plans = sorted(plans, key=lambda plan: plan.price)
    for plan in sorted_plans:
        # print(plan.id)
        text = plan.name
        if plan.discount:
            # discount_sum = round(plan.price * (plan.discount / 100))
            # new_price = round(plan.price - discount_sum)
            text += f" - {plan.price} руб (-{round(plan.discount)}%)"
        else:
            text += f" - {round(plan.price)} рублей"
        callback_data = f"payment|{plan.id}"
        print("callback_data", callback_data)
        keyboard.add(InlineKeyboardButton(text=text, callback_data=callback_data))
    keyboard.add(InlineKeyboardButton(text="◀️ Назад ◀️", callback_data="choose_recipient_button"))
    return keyboard.adjust(1).as_markup()


async def build_payment_keyboard(payment_url: str, payment_id: str, price: int):
    payment = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Оплатить {price} рублей", url=payment_url)],
        [InlineKeyboardButton(text='Я оплатил 💵', callback_data=f"check_payment|{payment_id}")],
        [InlineKeyboardButton(text='Отменить оплату ❎', callback_data=f"check_payment|-1")]
    ])
    return payment
