# -*- coding: utf-8 -*-
"""
Конфигурационный файл для Nickname Detector
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('nknmdtcr.env')

class Config:
    """Основные настройки приложения"""

    # 1. Настройки базы данных
    DATABASE = {
        'PATH': str(Path(__file__).parent / 'data' / 'nicknames.db'),
        'URL': os.getenv('DATABASE_URL', f'sqlite:///{Path(__file__).parent}/data/nicknames.db'),
        'TABLE_NAME': 'tracked_nicknames',
        'BACKUP_DIR': str(Path(__file__).parent / 'backups'),
        'BACKUP_DAYS': 7
    }

    # 2. Настройки API сервера
    API = {
        'HOST': os.getenv('API_HOST', '0.0.0.0'),
        'PORT': int(os.getenv('API_PORT', 5000)),
        'DEBUG': os.getenv('API_DEBUG', 'false').lower() == 'true',
        'SECRET_KEY': os.getenv('API_SECRET_KEY', 'default-secret-key'),
        'RATE_LIMIT': os.getenv('API_RATE_LIMIT', '100/day')
    }

    # 3. Настройки Telegram бота
    TELEGRAM = {
        'BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
        'ADMIN_IDS': [int(x) for x in os.getenv('TELEGRAM_ADMIN_IDS', '').split(',') if x],
        'NOTIFICATION_CHAT_ID': os.getenv('TELEGRAM_NOTIFICATION_CHAT_ID'),
        'MAX_NICKNAME_LENGTH': 25
    }

    # 4. Настройки OCR
    OCR = {
        'SCREEN_REGION': tuple(map(int, os.getenv('OCR_SCREEN_REGION', '100,100,300,200').split(','))) if os.getenv('OCR_SCREEN_REGION') else None,
        'LANG': os.getenv('OCR_LANG', 'rus+eng'),
        'TESSERACT_PATH': os.getenv('TESSERACT_PATH', '/usr/bin/tesseract')
    }

    # 5. Логирование
    LOGGING = {
        'LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
        'FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'FILE': str(Path(__file__).parent / 'logs' / 'server.log'),
        'MAX_SIZE': 5 * 1024 * 1024,
        'BACKUP_COUNT': 3
    }

config = Config()

if __name__ == '__main__':
    print("=== Тест конфигурации ===")
    print("Токен бота:", config.TELEGRAM['BOT_TOKEN'] or 'НЕ НАЙДЕН')
    print("ID админов:", config.TELEGRAM['ADMIN_IDS'])
    print("Путь к БД:", config.DATABASE['PATH'])
