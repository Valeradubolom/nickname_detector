import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect('nicknames.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nicknames (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/check', methods=['POST'])
def check_nickname():
    """Проверка наличия никнейма"""
    data = request.get_json()
    nickname = data.get('nickname')
    
    if not nickname:
        return jsonify({'error': 'Nickname required'}), 400
    
    conn = sqlite3.connect('nicknames.db')
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM nicknames WHERE name = ?', (nickname,))
    exists = cursor.fetchone() is not None
    conn.close()
    
    return jsonify({'exists': exists, 'nickname': nickname})

@app.route('/add', methods=['POST'])
def add_nickname():
    """Добавление нового никнейма"""
    data = request.get_json()
    nickname = data.get('nickname')
    
    if not nickname:
        return jsonify({'error': 'Nickname required'}), 400
    
    try:
        conn = sqlite3.connect('nicknames.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO nicknames (name) VALUES (?)', (nickname,))
        conn.commit()
        return jsonify({'status': 'added', 'nickname': nickname}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Nickname already exists'}), 400
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
