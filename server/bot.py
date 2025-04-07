from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from database import db
from config import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}!\n"
        "Я бот для отслеживания никнеймов.\n"
        "Используй /help для списка команд"
    )
    await help_command(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🛠 Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/add <никнейм> - Добавить никнейм в список\n"
        "/list - Показать все отслеживаемые никнеймы\n"
        "/help - Показать это сообщение"
    )
    await update.message.reply_text(help_text)

async def add_nick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажите никнейм: /add <никнейм>")
        return

    nickname = " ".join(context.args)
    if db.add_nickname(nickname, source="telegram"):
        await update.message.reply_text(f"✅ Добавлен: {nickname}")
    else:
        await update.message.reply_text(f"⚠ Ошибка добавления: {nickname}")

async def list_nicks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nicks = db.get_all_nicknames()
    response = "📋 Список никнеймов:\n" + "\n".join([n['nickname'] for n in nicks]) if nicks else "Список пуст"
    await update.message.reply_text(response)

def run_bot():
    app = Application.builder().token(config.TELEGRAM['BOT_TOKEN']).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_nick))
    app.add_handler(CommandHandler("list", list_nicks))
    app.add_handler(CommandHandler("help", help_command))

    logger.info("Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    run_bot()