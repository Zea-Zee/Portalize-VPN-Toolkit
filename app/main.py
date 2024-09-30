import asyncio
import logging

from colorama import Fore, Back, Style, init as colorama_init
from aiogram import Bot, Dispatcher

from config import TELGRAM_API_TOKEN
from bot.handlers import router
from database.models import async_main


bot = Bot(token=TELGRAM_API_TOKEN)
dp = Dispatcher()

colorama_init(autoreset=True)


async def main():
    await async_main()
    print(f"{Fore.GREEN}Database is active✅")
    await dp.start_polling(bot, skip_updates=False)
    print(f"{Fore.GREEN}Bot is active✅")


if __name__ == '__main__':
    dp.include_router(router)
    # logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit by keyboard')
    except Exception as e:
        print(f"{Fore.RED}{e}❌")
