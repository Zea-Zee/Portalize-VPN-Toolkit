import uuid
import json

from yookassa import Configuration, Payment

from config import YOOKASSA_SHOP_ID, YOOKASSA_API_TOKEN


# print(YOOKASSA_API_TOKEN, YOOKASSA_SHOP_ID)

Configuration.account_id = YOOKASSA_SHOP_ID
Configuration.secret_key = YOOKASSA_API_TOKEN


def create_payment(price: int, user_tg_id: int, description: str):
    price = str(price) + '.00'
    payment = Payment.create({
        "amount": {
            "value": price,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/Portalizer_VPN_Bot"
        },
        "capture": True,
        "description": description
    }, uuid.uuid4())
    return payment.confirmation.confirmation_url, payment.id


def get_payment_result(payment_id: str):
    payment = json.loads(Payment.find_one(payment_id).json())
    return payment
