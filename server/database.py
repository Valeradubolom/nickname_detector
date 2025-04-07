# -*- coding: utf-8 -*-
"""
Модуль для работы с базой данных Nickname Detector
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Union
from pathlib import Path
import logging
from config import config

# Настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(config.LOGGING['LEVEL'])


class Database:
    """Класс для работы с базой данных SQLite"""

    def __init__(self):
        self.db_path = Path(config.DATABASE['PATH'])
        self._ensure_db_directory()
        self._init_db()

    def _ensure_db_directory(self) -> None:
        """Создает директорию для БД, если не существует"""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.critical(f"Не удалось создать директорию для БД: {str(e)}")
            raise

    def _get_connection(self) -> sqlite3.Connection:
        """Создает и возвращает соединение с базой данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            # Включаем поддержку внешних ключей
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except sqlite3.Error as e:
            logger.critical(f"Ошибка подключения к БД: {str(e)}")
            raise

    def _init_db(self) -> None:
        """Инициализирует структуру базы данных"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Проверяем существование таблицы
                cursor.execute(f"""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='{config.DATABASE['TABLE_NAME']}'
                """)

                if not cursor.fetchone():
                    logger.info(f"Создаем новую таблицу: {config.DATABASE['TABLE_NAME']}")
                    cursor.execute(f"""
                        CREATE TABLE {config.DATABASE['TABLE_NAME']} (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nickname TEXT UNIQUE NOT NULL,
                            source TEXT DEFAULT 'manual',
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            last_detected TIMESTAMP NULL,
                            is_active BOOLEAN DEFAULT 1
                        )
                    """)
                    cursor.execute(f"""
                        CREATE INDEX idx_nickname_active 
                        ON {config.DATABASE['TABLE_NAME']}(nickname, is_active)
                    """)
                    conn.commit()
        except sqlite3.Error as e:
            logger.critical(f"Ошибка инициализации БД: {str(e)}")
            raise

    def add_nickname(self, nickname: str, source: str = 'manual') -> bool:
        """Добавляет никнейм в базу данных"""
        nickname = nickname.strip()
        if not nickname:
            logger.warning("Попытка добавить пустой никнейм")
            return False

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"""
                    INSERT INTO {config.DATABASE['TABLE_NAME']} 
                    (nickname, source) VALUES (?, ?)
                    ON CONFLICT(nickname) 
                    DO UPDATE SET is_active = 1, source = excluded.source
                    """,
                    (nickname, source)
                )
                conn.commit()
                logger.info(f"Добавлен/активирован никнейм: {nickname}")
                return True
        except sqlite3.Error as e:
            logger.error(f"Ошибка при добавлении никнейма {nickname}: {str(e)}")
            return False

    def remove_nickname(self, nickname: str, soft_delete: bool = True) -> bool:
        """Удаляет или деактивирует никнейм"""
        nickname = nickname.strip()
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                if soft_delete:
                    # Мягкое удаление (деактивация)
                    cursor.execute(
                        f"""
                        UPDATE {config.DATABASE['TABLE_NAME']} 
                        SET is_active = 0 
                        WHERE nickname = ? AND is_active = 1
                        """,
                        (nickname,)
                    )
                else:
                    # Полное удаление
                    cursor.execute(
                        f"""
                        DELETE FROM {config.DATABASE['TABLE_NAME']} 
                        WHERE nickname = ?
                        """,
                        (nickname,)
                    )

                conn.commit()
                if cursor.rowcount > 0:
                    logger.info(f"{'Деактивирован' if soft_delete else 'Удален'} никнейм: {nickname}")
                    return True

                logger.warning(f"Никнейм не найден или уже неактивен: {nickname}")
                return False
        except sqlite3.Error as e:
            logger.error(f"Ошибка при удалении никнейма {nickname}: {str(e)}")
            return False

    def check_nickname(self, nickname: str) -> bool:
        """Проверяет наличие активного никнейма в базе"""
        nickname = nickname.strip()
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"""
                    SELECT 1 FROM {config.DATABASE['TABLE_NAME']} 
                    WHERE nickname = ? AND is_active = 1
                    """,
                    (nickname,)
                )
                exists = cursor.fetchone() is not None

                if exists:
                    self._update_detection_time(nickname)

                return exists
        except sqlite3.Error as e:
            logger.error(f"Ошибка при проверке никнейма {nickname}: {str(e)}")
            return False

    def _update_detection_time(self, nickname: str) -> None:
        """Обновляет время последнего обнаружения"""
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
        except sqlite3.Error as e:
            logger.error(f"Ошибка обновления времени обнаружения: {str(e)}")

    def get_all_nicknames(self, active_only: bool = True) -> List[Dict]:
        """Возвращает список никнеймов с возможностью фильтрации"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = f"""
                    SELECT 
                        id, 
                        nickname, 
                        source, 
                        datetime(created_at, 'localtime') as created_at,
                        datetime(last_detected, 'localtime') as last_detected,
                        is_active
                    FROM {config.DATABASE['TABLE_NAME']}
                """
                if active_only:
                    query += " WHERE is_active = 1"
                query += " ORDER BY created_at DESC"

                cursor.execute(query)
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Ошибка при получении списка никнеймов: {str(e)}")
            return []

    def backup_database(self) -> Optional[Path]:
        """Создает резервную копию базы данных"""
        try:
            backup_dir = Path(config.DATABASE['BACKUP_DIR'])
            backup_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = backup_dir / f"nicknames_backup_{timestamp}.db"

            with self._get_connection() as src:
                with sqlite3.connect(backup_path) as dst:
                    src.backup(dst)

            logger.info(f"Создана резервная копия: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Ошибка при создании резервной копии: {str(e)}")
            return None


# Глобальный экземпляр для использования в других модулях
db = Database()
