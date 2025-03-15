import asyncio
import logging
from aiogram import Bot, Dispatcher

from Database import create_table
from config import BOT_TOKEN
from handlers import start_handlers, add_apart_handler, search_apart_handlers

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start_handlers.router)
    dp.include_router(add_apart_handler.router)
    dp.include_router(search_apart_handlers.router)
    create_table()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



