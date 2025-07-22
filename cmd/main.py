import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.config import BOT_TOKEN

from app.handlers import handler
from app.handlers import file_manager

from app.cache import UserStateCache
from datetime import timedelta
from app.metrics.server import start_metrics_server
from app.metrics.metrics import start_internal_metrics_updating


logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=BOT_TOKEN)

    # ============== metrics
    start_metrics_server(port=2112)
    asyncio.create_task(start_internal_metrics_updating())

    # ========================================== cache
    cache = UserStateCache(
        bot=bot,
        ttl=timedelta(seconds=120),
        cleanup_interval=timedelta(seconds=10)
    )

    bot.user_state_cache = cache

    dp = Dispatcher()
    dp.include_router(handler.router)
    dp.include_router(file_manager.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
