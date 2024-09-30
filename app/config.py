import os
from dotenv import load_dotenv

load_dotenv()
YOOKASSA_API_TOKEN = os.getenv('YOOKASSA_API_TOKEN')
YOOKASSA_SHOP_ID = os.getenv('YOOKASSA_SHOP_ID')

TELGRAM_API_TOKEN = os.getenv('TELGRAM_API_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')


if not YOOKASSA_API_TOKEN:
    raise Exception("No YOOKASSA_API_TOKEN token found!")

if not YOOKASSA_SHOP_ID:
    raise Exception("No YOOKASSA_SHOP_ID token found!")


if not TELGRAM_API_TOKEN:
    raise Exception("No TELGRAM_API_TOKEN token found!")

if not GROUP_ID:
    raise Exception("No GROUP_ID token found!")
