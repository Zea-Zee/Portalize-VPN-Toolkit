from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


start_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Начать ", callback_data="start_command")]
    ]
)

trial = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔥Попробовать🔥', callback_data='get_trial')]
    ],
    resize_keyboard=True,
    input_field_placeholder="Попробуйте, это полностью бесплатно)"
)
