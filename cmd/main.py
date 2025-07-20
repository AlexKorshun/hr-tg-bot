# app/main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.config import BOT_TOKEN

from app.handlers import handler
from app.handlers import file_manager

from app.cache import UserStateCache
from datetime import timedelta


logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=BOT_TOKEN)

    # ========================================== cache
    cache = UserStateCache(
        bot=bot,
        ttl=timedelta(seconds=20),
        cleanup_interval=timedelta(seconds=1)
    )

    bot.user_state_cache = cache

    dp = Dispatcher()
    dp.include_router(file_manager.router)
    dp.include_router(handler.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    print("АХУЕТЬ, РАБОТАЕТ WW")
    asyncio.run(main())
