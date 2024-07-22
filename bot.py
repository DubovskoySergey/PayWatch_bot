from telegram.ext import Updater, CommandHandler
from config import TELEGRAM_TOKEN
from handlers import start, add_payment, list_payments, delete_payment, update_payment
from database import init_db

def main() -> None:
    # Инициализация базы данных
    init_db()

    # Создание и настройка бота
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    # Обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add_payment", add_payment))
    dispatcher.add_handler(CommandHandler("list_payments", list_payments))
    dispatcher.add_handler(CommandHandler("delete_payment", delete_payment))
    dispatcher.add_handler(CommandHandler("update_payment", update_payment))

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
