### **Nickname Detector**  

Проект представляет собой систему для мониторинга части экрана в реальном времени, обнаружения никнеймов и их проверки в базе данных с отправкой уведомлений в Telegram.  

---

## **1. Screen Monitor (screen_monitor.py)**  

### Описание  
Основной модуль, который сканирует заданную область экрана, распознает текст (никнеймы) с помощью OCR и проверяет их в базе данных.  

### Основные функции:  
- **Захват области экрана** в реальном времени  
- **Распознавание текста** (Tesseract OCR)  
- **Проверка никнеймов** в базе данных  
- **Логирование** найденных совпадений  

### Технологии:  
- **OpenCV** – захват и обработка изображения  
- **Tesseract OCR** – распознавание текста  
- **Многопоточность** – для плавной работы без зависаний  

### Пример кода:  
```python
import cv2
from PIL import ImageGrab
import pytesseract

def scan_nicknames(x, y, width, height):
    screen = ImageGrab.grab(bbox=(x, y, x+width, y+height))
    text = pytesseract.image_to_string(screen)
    return text
```

---

## **2. База данных (nicknames.db)**  

### Описание  
SQLite база данных для хранения отслеживаемых никнеймов.  

### Структура таблицы `tracked_nicknames`:  
- `id` – уникальный идентификатор  
- `nickname` – сам никнейм  
- `date_added` – дата добавления  

### Пример запроса:  
```sql
INSERT INTO tracked_nicknames (nickname, date_added) 
VALUES ('ExampleUser', datetime('now'));
```

---

## **3. Telegram Bot (bot.py)**  

### Описание  
Бот для управления базой никнеймов и получения уведомлений.  

### Основные команды:  
- **/add nickname** – добавить ник в базу  
- **/del nickname** – удалить ник  
- **/list** – показать все ники  
- Автоматические уведомления о совпадениях  

### Пример кода (aiogram):  
```python
from aiogram import Bot, Dispatcher, types

bot = Bot(token="TOKEN")
dp = Dispatcher(bot)

@dp.message_handler(commands=['add'])
async def add_nickname(message: types.Message):
    # Добавление в БД
    await message.reply("Ник добавлен!")
```

---

## **4. Шифрование**  

### Описание  
Данные между клиентом и сервером передаются в зашифрованном виде.  

### Используется:  
- **AES** – для шифрования трафика  
- **HMAC** – проверка целостности данных  

---

## **5. Запуск проекта**  

1. Установите зависимости:  
```bash
pip install opencv-python pytesseract pillow python-telegram-bot aiogram
```

2. Настройте область сканирования в `config.py`:  
```python
MONITOR_REGION = (100, 100, 300, 200)  # x, y, width, height
```

3. Запустите:  
```bash
python screen_monitor.py
python bot.py
```

---

## **6. Пример работы**  

1. В чате появляется никнейм **"ExampleUser"**  
2. Система обнаруживает его и проверяет в БД  
3. При совпадении бот отправляет:  
```
🔔 Найден ник: ExampleUser!
```

---

## **7. Структура проекта**  

```
nickname-detector/
├── screen_monitor.py   # Монитор экрана
├── bot.py              # Telegram бот
├── nicknames.db        # База данных
├── config.py           # Настройки
└── README.md           # Документация
```

---

## **8. Доработки**  

- Добавить фильтрацию по регистру  
- Поддержка нескольких чатов одновременно  
- Графический интерфейс для настройки  

---

## **9. Лицензия**  

MIT License.
