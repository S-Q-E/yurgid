import logging
import os
from datetime import datetime

def setup_logger():
    logger = logging.getLogger("YurGidBot")
    logger.setLevel(logging.INFO)

    # Формат логов
    log_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Логи в файл
    log_file = f"bot_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    # Логи в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    return logger