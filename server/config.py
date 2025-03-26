
import os
from dotenv import load_dotenv  # Для загрузки переменных окружения

# Загружаем переменные из файла .env (если есть)
load_dotenv()


class Config:
    """Основные настройки приложения"""

    # 1. Настройки базы данных
    DATABASE = {
        'PATH': 'nicknames.db',  # Путь к файлу SQLite
        'TABLE_NAME': 'tracked_nicknames',  # Название таблицы
        'BACKUP_DIR': 'backups',  # Папка для резервных копий
        'BACKUP_DAYS': 7  # Хранить резервные копии N дней
    }

    # 2. Настройки API сервера
    API = {
        'HOST': '0.0.0.0',  # Хост для запуска сервера
        'PORT': 5000,  # Порт сервера
        'DEBUG': True,  # Режим отладки (False в продакшене)
        'SECRET_KEY': os.getenv('API_SECRET_KEY', 'default-secret-key'),  # Ключ API
        'RATE_LIMIT': '100/day'  # Лимит запросов (100 в день)
    }

    # 3. Настройки Telegram бота
    TELEGRAM = {
        'BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN', ''),  # Токен бота(ДОДЕЛАТЬ!)
        'ADMIN_IDS': [123456789],  # ID администраторов (могут удалять)
        'NOTIFY_CHAT_ID': -100123456,  # Чат для уведомлений
        'MAX_NICKNAME_LENGTH': 25  # Макс. длина никнейма
    }

    # 4. Настройки OCR (для будущего расширения)
    OCR = {
        'SCREEN_REGION': (100, 100, 300, 200),  # (x1, y1, x2, y2)
        'LANG': 'rus+eng',  # Языки распознавания
        'TESSERACT_PATH': '/usr/bin/tesseract'  # Путь к Tesseract OCR
    }

    # 5. Логирование
    LOGGING = {
        'LEVEL': 'INFO',  # DEBUG/INFO/WARNING/ERROR
        'FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'FILE': 'server.log'  # Файл для логов
    }


# Создаем экземпляр конфигурации
config = Config()

# Пример использования:
# from config import config
# print(config.API['PORT'])
