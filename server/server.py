import sqlite3
from flask import Flask, request, jsonify
from datetime import datetime
import logging

# Инициализация Flask-приложения
app = Flask(__name__)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='server.log'
)
logger = logging.getLogger(__name__)

# Конфигурация
DATABASE_PATH = 'nicknames.db'
API_KEYS = ['your-secret-key']  # Для авторизации клиентов

def get_db_connection():
    """Создает и возвращает соединение с базой данных"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Доступ к колонкам по именам
    return conn

def init_db():
    """Инициализация структуры базы данных"""
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS nicknames (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nickname TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source TEXT DEFAULT 'manual'
            )
        ''')
        conn.commit()
    logger.info("База данных инициализирована")

def validate_api_key():
    """Проверка API-ключа в заголовках запроса"""
    api_key = request.headers.get('X-API-KEY')
    if api_key not in API_KEYS:
        logger.warning(f"Неавторизованный доступ с ключом: {api_key}")
        return False
    return True

@app.route('/api/check', methods=['POST'])
def check_nickname():
    """
    Проверяет наличие никнейма в базе
    Пример запроса: {"nickname": "test_user"}
    """
    if not validate_api_key():
        return jsonify({'error': 'Invalid API key'}), 401

    data = request.get_json()
    if not data or 'nickname' not in data:
        return jsonify({'error': 'Nickname is required'}), 400

    nickname = data['nickname'].strip()
    logger.info(f"Проверка никнейма: {nickname}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM nicknames WHERE nickname = ?', 
                (nickname,)
            )
            result = cursor.fetchone()

        exists = bool(result)
        logger.info(f"Результат проверки: {'найден' if exists else 'не найден'}")
        return jsonify({
            'exists': exists,
            'nickname': nickname,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Ошибка при проверке: {str(e)}")
        return jsonify({'error': 'Database error'}), 500

@app.route('/api/add', methods=['POST'])
def add_nickname():
    """
    Добавляет новый никнейм в базу
    Пример запроса: {"nickname": "new_user"}
    """
    if not validate_api_key():
        return jsonify({'error': 'Invalid API key'}), 401

    data = request.get_json()
    if not data or 'nickname' not in data:
        return jsonify({'error': 'Nickname is required'}), 400

    nickname = data['nickname'].strip()
    source = data.get('source', 'manual')
    logger.info(f"Добавление никнейма: {nickname}")

    try:
        with get_db_connection() as conn:
            conn.execute(
                'INSERT INTO nicknames (nickname, source) VALUES (?, ?)',
                (nickname, source)
            )
            conn.commit()

        logger.info("Никнейм успешно добавлен")
        return jsonify({
            'status': 'success',
            'nickname': nickname,
            'source': source
        }), 201

    except sqlite3.IntegrityError:
        logger.warning("Попытка добавить существующий никнейм")
        return jsonify({'error': 'Nickname already exists'}), 400
    except Exception as e:
        logger.error(f"Ошибка при добавлении: {str(e)}")
        return jsonify({'error': 'Database error'}), 500

@app.route('/api/list', methods=['GET'])
def list_nicknames():
    """Возвращает список всех никнеймов"""
    if not validate_api_key():
        return jsonify({'error': 'Invalid API key'}), 401

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM nicknames ORDER BY created_at DESC')
            nicknames = [dict(row) for row in cursor.fetchall()]

        logger.info(f"Возвращено {len(nicknames)} никнеймов")
        return jsonify({'nicknames': nicknames})

    except Exception as e:
        logger.error(f"Ошибка при получении списка: {str(e)}")
        return jsonify({'error': 'Database error'}), 500

if __name__ == '__main__':
    init_db()
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True  # Для обработки нескольких запросов одновременно
    )
