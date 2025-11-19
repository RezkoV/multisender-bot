import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import config
from app.database.simple_db import db  # Импортируем простую БД
from app.handlers import admin, user, mailing

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # БД уже инициализирована автоматически
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    dp.include_router(user.router)
    dp.include_router(admin.router)
    dp.include_router(mailing.router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())