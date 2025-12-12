
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import FSInputFile

from .image_processor import process_user_photo
from .utils import setup_logging

logger = logging.getLogger(__name__)

@Command("start")
async def cmd_start(message: types.Message):
    await message.answer("""
🤖 Умная Городская Фотозона 📸

Привет! Вы только что подключились к нашей профессиональной камере. Ваш смартфон — это пульт управления!

Готовы к идеальному кадру?

1. Смотрите на экран: Вы видите живой предпросмотр с главной достопримечательностью.

2. Выберите режим:

    ✨ AI Магия: Превратитесь в батыра или киберпанк-персонажа.

    🖼️ Идеальный Кадр: Получите кристально чистый снимок высокого разрешения с **улучшением лица и фона**.

3. Сделайте снимок! Ваше фото будет мгновенно обработано ИИ и отправлено вам.

Начните прямо сейчас! 👇
""")

@F.photo
async def handle_photo(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    msg = await message.answer("⏳ 0/4 Запускаю конвейер обработки...")
    
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    
    try:
        final_result = await process_user_photo(file_info, user_id, bot, msg)
    except Exception as e:
        logger.error(f"Критическая ошибка в обработчике фото для {user_id}: {e}")
        await msg.edit_text("❌ Произошла непредвиденная ошибка в конвейере обработки.")
        return

    await msg.delete()
    
    if final_result.startswith("❌"):
        
        await message.answer(final_result)
    else:
        
        caption_text = "✨ Готово! Фото прошло полную 4-этапную обработку: цветокоррекция, улучшение лица, коррекция фона и финальная настройка."
        await message.answer_photo(FSInputFile(final_result), caption=caption_text)