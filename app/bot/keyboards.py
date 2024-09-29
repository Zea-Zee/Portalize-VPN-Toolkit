from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


start_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Начать ", callback_data="start_command")]
    ]
)

options = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🤑Получить бесплатно на 7 дней🤑', callback_data='trial_button')],
    [InlineKeyboardButton(text='💸Купить подписку сразу💸', callback_data='buy_button')],
    [InlineKeyboardButton(text='🎁Подарить другу🎁', callback_data='present_button')]
    ],
    resize_keyboard=True,
    input_field_placeholder="Попробуйте, это полностью бесплатно)"
)

subscribe = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Подписаться", url='https://t.me/PortalizerVPN')],
    [InlineKeyboardButton(text='Я подписался ✅', callback_data='check_subscription')]
])

buy_plans = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='1 месяц 100 рублей', callback_data='payment')],
    [InlineKeyboardButton(text='3 месяца 270р. (-10% / -30р.)', callback_data='payment')],
    [InlineKeyboardButton(text='6 месяца 480р. (-20% / -120р.)', callback_data='payment')],
    [InlineKeyboardButton(text='12 месяцев 840р. (-30% / -360р.)', callback_data='payment')],
    [InlineKeyboardButton(text='Назад 🔙', callback_data='back_button')]
    ],
    resize_keyboard=True
)

gift_plans = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='1 месяц 80 рублей', callback_data='payment')],
    [InlineKeyboardButton(text='3 месяца 230р. (-5% / -10р.)', callback_data='payment')],
    [InlineKeyboardButton(text='6 месяца 430. (-10% / -50р.)', callback_data='payment')],
    [InlineKeyboardButton(text='12 месяцев 820. (-15% / -140р.)', callback_data='payment')],
    [InlineKeyboardButton(text='Назад 🔙', callback_data='back_button')]
    ],
    resize_keyboard=True
)

platform_options = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Android 🤖', callback_data='choose_tunnel,android')],
    [InlineKeyboardButton(text='iOS 🍏', callback_data='choose_tunnel,android')],
    [InlineKeyboardButton(text='Windows ', callback_data='choose_tunnel,android')],
    [InlineKeyboardButton(text='Android 🤖', callback_data='choose_tunnel,android')],
    [InlineKeyboardButton(text='Назад 🔙', callback_data='back_button')]
    ],
    resize_keyboard=True
)
