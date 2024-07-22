import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import CallbackContext

from database import Session
from models import User, Payment

# Настройки логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    session = Session()
    user = update.effective_user
    if not session.query(User).filter_by(telegram_id=user.id).first():
        new_user = User(telegram_id=user.id, username=user.username)
        session.add(new_user)
        session.commit()
    session.close()
    update.message.reply_text('Привет! Я бот, который поможет тебе не забывать о твоих платежах.')

def add_payment(update: Update, context: CallbackContext) -> None:
    session = Session()
    try:
        user = session.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            update.message.reply_text('Ошибка: Пользователь не найден.')
            return
        
        args = context.args
        title = args[0]
        amount = float(args[1])
        payment_date = datetime.strptime(args[2], '%Y-%m-%d')
        reminder_period = args[3]  # 'weekly', 'biweekly', 'monthly'
        notification_duration = args[4]  # '1 day', '1 month', etc.
        category = args[5]  # 'Кредит', 'Ипотека', etc.

        reminder_intervals = {
            'weekly': timedelta(weeks=1),
            'biweekly': timedelta(weeks=2),
            'monthly': timedelta(days=30)
        }

        notification_durations = {
            'day': timedelta(days=1),
            'month': timedelta(days=30),
            '2 months': timedelta(days=60),
            '3 months': timedelta(days=90),
            '4 months': timedelta(days=120),
            '5 months': timedelta(days=150),
            '6 months': timedelta(days=180),
            'year': timedelta(days=365)
        }

        if reminder_period not in reminder_intervals or notification_duration not in notification_durations:
            update.message.reply_text('Ошибка: Неверный период напоминания или продолжительность уведомления.')
            return

        new_payment = Payment(
            user_id=user.id,
            title=title,
            amount=amount,
            payment_date=payment_date,
            reminder_period=reminder_intervals[reminder_period],
            notification_duration=notification_durations[notification_duration],
            category=category
        )

        session.add(new_payment)
        session.commit()
        update.message.reply_text(f'Платеж "{title}" добавлен.')
    except Exception as e:
        logger.error(f'Ошибка при добавлении платежа: {e}')
        update.message.reply_text('Ошибка: Неверный формат данных.')
    finally:
        session.close()

def list_payments(update: Update, context: CallbackContext) -> None:
    session = Session()
    user = session.query(User).filter_by(telegram_id=update.effective_user.id).first()
    if not user:
        update.message.reply_text('Ошибка: Пользователь не найден.')
        session.close()
        return

    payments = session.query(Payment).filter_by(user_id=user.id).all()
    if not payments:
        update.message.reply_text('Нет активных платежей.')
        session.close()
        return

    message = 'Ваши платежи:\n'
    for payment in payments:
        message += f'{payment.title}: {payment.amount} руб. Дата: {payment.payment_date.strftime("%Y-%m-%d")}\n'
    update.message.reply_text(message)
    session.close()

def delete_payment(update: Update, context: CallbackContext) -> None:
    session = Session()
    try:
        user = session.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            update.message.reply_text('Ошибка: Пользователь не найден.')
            return
        
        payment_id = int(context.args[0])
        payment = session.query(Payment).filter_by(id=payment_id, user_id=user.id).first()
        if not payment:
            update.message.reply_text('Ошибка: Платеж не найден.')
            return
        
        session.delete(payment)
        session.commit()
        update.message.reply_text(f'Платеж "{payment.title}" удален.')
    except Exception as e:
        logger.error(f'Ошибка при удалении платежа: {e}')
        update.message.reply_text('Ошибка: Неверный формат данных.')
    finally:
        session.close()

def update_payment(update: Update, context: CallbackContext) -> None:
    session = Session()
    try:
        user = session.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            update.message.reply_text('Ошибка: Пользователь не найден.')
            return

        args = context.args
        payment_id = int(args[0])  # ID платежа
        field = args[1]  # Поле, которое нужно изменить
        new_value = ' '.join(args[2:])  # Новое значение

        # Проверяем наличие платежа
        payment = session.query(Payment).filter_by(id=payment_id, user_id=user.id).first()
        if not payment:
            update.message.reply_text('Ошибка: Платеж не найден.')
            return

        # Обновляем поле платежа
        if field == 'title':
            payment.title = new_value
        elif field == 'amount':
            payment.amount = float(new_value)
        elif field == 'payment_date':
            payment.payment_date = datetime.strptime(new_value, '%Y-%m-%d')
        elif field == 'reminder_period':
            reminder_intervals = {
                'weekly': timedelta(weeks=1),
                'biweekly': timedelta(weeks=2),
                'monthly': timedelta(days=30)
            }
            if new_value in reminder_intervals:
                payment.reminder_period = reminder_intervals[new_value]
            else:
                update.message.reply_text('Ошибка: Неверный период напоминания.')
                return
        elif field == 'notification_duration':
            notification_durations = {
                'day': timedelta(days=1),
                'month': timedelta(days=30),
                '2 months': timedelta(days=60),
                '3 months': timedelta(days=90),
                '4 months': timedelta(days=120),
                '5 months': timedelta(days=150),
                '6 months': timedelta(days=180),
                'year': timedelta(days=365)
            }
            if new_value in notification_durations:
                payment.notification_duration = notification_durations[new_value]
            else:
                update.message.reply_text('Ошибка: Неверная продолжительность уведомления.')
                return
        elif field == 'category':
            valid_categories = ['Кредит', 'Ипотека', 'Коммунальные платежи', 'Подписки', 'Квартплата', 'Налоги', 'Страховка']
            if new_value in valid_categories:
                payment.category = new_value
            else:
                update.message.reply_text('Ошибка: Неверная категория.')
                return
        else:
            update.message.reply_text('Ошибка: Неверное поле для обновления.')
            return

        session.commit()
        update.message.reply_text(f'Платеж "{payment.title}" успешно обновлен.')
    except Exception as e:
        logger.error(f'Ошибка при обновлении платежа: {e}')
        update.message.reply_text('Ошибка: Неверный формат данных или ошибка при обновлении.')
    finally:
        session.close()
