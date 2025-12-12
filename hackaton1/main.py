
import asyncio
import os
from aiogram import Bot, Dispatcher


from handlers import cmd_start, handle_photo
from utils import setup_logging, BOT_TOKEN


setup_logging()

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_TOKEN не найден в переменных окружения.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


dp.message.register(cmd_start)
dp.message.register(handle_photo)
async def main():
    try:
        await dp.start_polling(bot)
    except Exception as e:
        setup_logging().error(f"Критическая ошибка при запуске бота: {e}")

if __name__ == "__main__":
    asyncio.run(main())