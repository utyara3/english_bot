import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from aiogram_sqlite_storage.sqlitestore import SQLStorage

from config import BOT_TOKEN
from bot_logging import setup_logging, get_logger

from handlers import router

setup_logging(
    name="english_bot",
    log_file="bot.log",
    level=logging.INFO
)

logger = get_logger('main')
db_path = "database.db"

async def main() -> None:
    storage = SQLStorage(db_path)

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )
    dp = Dispatcher(storage=storage)

    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logger.info('start')
    asyncio.run(main())


