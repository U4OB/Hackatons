# utils.py
import os
import logging
from dotenv import load_dotenv

# Настройки
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# Папки
INPUT_FOLDER = "input_photos"
OUTPUT_FOLDER = "output_photos"
os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Инициализация логирования
def setup_logging():
    """Настраивает базовое логирование."""
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.info("Логирование настроено.")