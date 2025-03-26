# -*- coding: utf-8 -*-
"""
Модуль для работы с базой данных Nickname Detector
Реализует все основные операции с никнеймами:
- добавление
- удаление
- проверка
- получение списка
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import logging
from config import config  # Импортируем настройки

# Настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(config.LOGGING['LEVEL'])


class Database:
    """Класс для работы с базой данных SQLite"""

    def __init__(self):
        self.db_path = Path(config.DATABASE['PATH'])
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Создает и возвращает соединение с базой данных"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Для доступа к полям по именам
        return conn

    def _init_db(self) -> None:
        """Инициализирует структуру базы данных"""
        if not self.db_path.exists():
            logger.info(f"Создаем новую базу данных: {self.db_path}")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {config.DATABASE['TABLE_NAME']} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nickname TEXT UNIQUE NOT NULL,
                    source TEXT DEFAULT 'manual',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_detected TIMESTAMP NULL
                )
            """)
            # Создаем индекс для быстрого поиска
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_nickname 
                ON {config.DATABASE['TABLE_NAME']}(nickname)
            """)
            conn.commit()

    def add_nickname(self, nickname: str, source: str = 'manual') -> bool:
        """
        Добавляет никнейм в базу данных
        :param nickname: Никнейм для добавления
        :param source: Источник добавления ('manual', 'telegram', 'auto')
        :return: True если успешно, False если ошибка
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"""
                    INSERT INTO {config.DATABASE['TABLE_NAME']} 
                    (nickname, source) VALUES (?, ?)
                    """,
                    (nickname.strip(), source)
                )
                conn.commit()
                logger.info(f"Добавлен никнейм: {nickname} (источник: {source})")
                return True

        except sqlite3.IntegrityError:
            logger.warning(f"Никнейм уже существует: {nickname}")
            return False
        except Exception as e:
            logger.error(f"Ошибка при добавлении никнейма: {str(e)}")
            return False

    def remove_nickname(self, nickname: str) -> bool:
        """
        Удаляет никнейм из базы данных
        :param nickname: Никнейм для удаления
        :return: True если успешно, False если ошибка
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"""
                    DELETE FROM {config.DATABASE['TABLE_NAME']} 
                    WHERE nickname = ?
                    """,
                    (nickname.strip(),)
                )
                conn.commit()
                if cursor.rowcount > 0:
                    logger.info(f"Удален никнейм: {nickname}")
                    return True
                logger.warning(f"Никнейм не найден: {nickname}")
                return False
        except Exception as e:
            logger.error(f"Ошибка при удалении никнейма: {str(e)}")
            return False

    def check_nickname(self, nickname: str) -> bool:
        """
        Проверяет наличие никнейма в базе
        :param nickname: Никнейм для проверки
        :return: True если найден, False если нет
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"""
                    SELECT 1 FROM {config.DATABASE['TABLE_NAME']} 
                    WHERE nickname = ?
                    """,
                    (nickname.strip(),)
                )
                exists = cursor.fetchone() is not None

                # Обновляем время последнего обнаружения
                if exists:
                    self._update_detection_time(nickname)

                return exists
        except Exception as e:
            logger.error(f"Ошибка при проверке никнейма: {str(e)}")
            return False

    def _update_detection_time(self, nickname: str) -> None:
        """Обновляет время последнего обнаружения никнейма"""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    f"""
                    UPDATE {config.DATABASE['TABLE_NAME']} 
                    SET last_detected = CURRENT_TIMESTAMP 
                    WHERE nickname = ?
                    """,
                    (nickname.strip(),)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Ошибка обновления времени обнаружения: {str(e)}")

    def get_all_nicknames(self) -> List[Dict]:
        """
        Возвращает список всех никнеймов
        :return: Список словарей с данными никнеймов
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"""
                    SELECT 
                        id, 
                        nickname, 
                        source, 
                        datetime(created_at, 'localtime') as created_at,
                        datetime(last_detected, 'localtime') as last_detected
                    FROM {config.DATABASE['TABLE_NAME']}
                    ORDER BY created_at DESC
                    """
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Ошибка при получении списка никнеймов: {str(e)}")
            return []

    def backup_database(self) -> bool:
        """Создает резервную копию базы данных"""
        try:
            backup_dir = Path(config.DATABASE['BACKUP_DIR'])
            backup_dir.mkdir(exist_ok=True)

            backup_name = f"nicknames_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            backup_path = backup_dir / backup_name

            with self._get_connection() as src:
                with sqlite3.connect(backup_path) as dst:
                    src.backup(dst)

            logger.info(f"Создана резервная копия: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при создании резервной копии: {str(e)}")
            return False


# Создаем экземпляр базы данных для использования в других модулях
db = Database()

# Пример использования:
# from database import db
# db.add_nickname("TestUser")
# exists = db.check_nickname("TestUser")
# all_nicks = db.get_all_nicknames()
