
import asyncio
import logging
import os
import requests
from io import BytesIO

from PIL import Image, ImageEnhance
import replicate

from .utils import INPUT_FOLDER, OUTPUT_FOLDER, REPLICATE_API_TOKEN

logger = logging.getLogger(__name__)



def local_color_correction(image_path):
    """Шаг 1: Делаем фото сочным (цветокоррекция)"""
    logger.info(f"Применяю цветокоррекцию к: {image_path}")
    try:
        img = Image.open(image_path)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.4) 
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.5)
        
        temp_path = image_path.replace(".jpg", "_color.jpg")
        img.save(temp_path)
        return temp_path
    except Exception as e:
        logger.error(f"Ошибка цветокоррекции: {e}")
        return image_path

async def ai_face_restore(image_path):
    """Шаг 2: Улучшаем лицо через CodeFormer"""
    logger.info(f"Запускаю CodeFormer для: {image_path}")
    try:        
        output = await asyncio.to_thread(
            replicate.run,
            "sczhou/codeformer:7de2ea26c616d5bf2245ad0d5e24f0ff9a6204578a5c876db53142edd9d2cd56",
            input={
                "image": open(image_path, "rb"),
                "codeformer_fidelity": 0.7, 
                "background_enhance": False,
                "upscale": 1
            }
        )
        return str(output) 
    except Exception as e:
        logger.error(f"Ошибка CodeFormer (Face Restore): {e}")
        return None

def ai_background_sharpening(image_path):
    """
    Шаг 3 (ИМИТАЦИЯ): Нейросеть улучшает детали и резкость фона.
    В реальности: Имитация небольшой дополнительной резкости.
    """
    logger.info(f"Имитация улучшения фона для: {image_path}")
    try:
        img = Image.open(image_path)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.1)
        
        temp_path = image_path.replace(".jpg", "_bg_sharp.jpg").replace("_color", "") 
        img.save(temp_path)
        return temp_path
    except Exception as e:
        logger.error(f"Ошибка имитации улучшения фона: {e}")
        return image_path

def apply_final_post_processing(image_url, user_id):
    """
    Шаг 4 (ИМИТАЦИЯ): Финальная постобработка (нанесение водяного знака, кадрирование и т.д.).
    В реальности: Скачивание, сохранение и имитация.
    """
    logger.info(f"Финальная постобработка и сохранение для пользователя {user_id}. URL: {image_url}")
    try:
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.05)
        final_path = os.path.join(OUTPUT_FOLDER, f"{user_id}_final.jpg")
        img.save(final_path, format='JPEG', quality=95)
        logger.info(f"Финальное фото сохранено: {final_path}")
        return final_path
    except Exception as e:
        logger.error(f"Ошибка финальной постобработки: {e}")
        return None


async def process_user_photo(file_info, user_id, bot, message_to_edit):
    """Главная функция, управляющая всей цепочкой обработки."""
    
    local_filename = os.path.join(INPUT_FOLDER, f"{user_id}.jpg")
    await bot.download_file(file_info.file_path, local_filename)
    await message_to_edit.edit_text("⏳ 1/4 Скачиваю и делаю цветокоррекцию...")
    color_path = local_color_correction(local_filename)
    await message_to_edit.edit_text("⏳ 2/4 Нейросеть улучшает лицо (CodeFormer)...")
    face_url = await ai_face_restore(color_path)
    
    if not face_url:
        return "❌ Ошибка нейросети на этапе улучшения лица."
    
    await message_to_edit.edit_text("⏳ 3/4 Нейросеть корректирует фон...")
    
    codeformer_res_path = os.path.join(INPUT_FOLDER, f"{user_id}_codeformer.jpg")
    response = requests.get(face_url)
    with open(codeformer_res_path, "wb") as f:
        f.write(response.content)

    bg_sharp_path = ai_background_sharpening(codeformer_res_path)

    await message_to_edit.edit_text("⏳ 4/4 Финальная постобработка...")

    final_path = apply_final_post_processing(face_url, user_id) 


    os.remove(local_filename)
    os.remove(color_path) 
    os.remove(codeformer_res_path)

    if not final_path:
        return "❌ Критическая ошибка: Не удалось получить финальное изображение."
        
    return final_path 