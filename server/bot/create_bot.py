import asyncio
import logging
import json

from aiogram import Bot, Dispatcher

from config import TELGRAM_API_TOKEN
from handler import router


bot = Bot(token=TELGRAM_API_TOKEN)
dp = Dispatcher()


async def main():
    await dp.start_polling(bot)
    print("Bot turned on")


if __name__ == '__main__':
    dp.include_router(router)
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
