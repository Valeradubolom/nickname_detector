```markdown
# Nickname Detector 🔍

Проект для автоматического обнаружения никнеймов на экране с уведомлениями в Telegram.

## 📌 Основные компоненты

### 1. Модуль сканирования экрана
- Захват указанной области экрана
- Распознавание текста через Tesseract OCR
- Сравнение с базой никнеймов

```python
# Пример запуска сканирования
from scanner import ScreenScanner

scanner = ScreenScanner()
scanner.start(area=(100, 100, 500, 500), interval=3)
```

### 2. Telegram-бот
**Доступные команды:**
```
/add <nickname> - Добавить никнейм
/remove <nickname> - Удалить никнейм
/list - Показать все никнеймы
/scan - Начать сканирование
/stop - Остановить сканирование
```

### 3. База данных
Хранит список отслеживаемых никнеймов в PostgreSQL:
```sql
CREATE TABLE nicknames (
    id SERIAL PRIMARY KEY,
    nickname VARCHAR(64) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## ⚙️ Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Настройте конфиг:
```bash
cp config.example.py config.py
```

3. Запустите:
```bash
python main.py
```

## 📋 Пример конфигурации
```python
# config.py
TELEGRAM_TOKEN = "ваш_токен"
SCAN_AREA = (0, 0, 800, 600)  # x1,y1,x2,y2
SCAN_INTERVAL = 5  # секунд
```

## 🌟 Особенности
- Мгновенные уведомления в Telegram
- Поддержка нескольких пользователей
- Настройка области сканирования
- Логирование всех операций

## 📄 Лицензия
MIT License. Подробнее в [LICENSE](LICENSE).
```

Этот README:
1. Готов к копированию и вставке
2. Содержит реальные примеры кода
3. Включает инструкции по установке
4. Имеет четкую структуру
5. Подходит для GitHub/GitLab

Просто замените:
- `ваш_токен` на реальный токен бота
- Параметры `SCAN_AREA` под ваши нужды
- Добавьте свои скриншоты в проект
