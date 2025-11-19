from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from app.database.simple_db import db
from app.keyboards.inline import get_cancel_keyboard

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Проверяем существующего пользователя
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (message.from_user.id,))
    user = cursor.fetchone()
    
    if not user:
        # Добавляем нового пользователя
        cursor.execute('''
            INSERT INTO users (user_id, username, first_name, last_name, is_subscribed)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name,
            True
        ))
    else:
        # Обновляем существующего
        cursor.execute('''
            UPDATE users 
            SET username = ?, first_name = ?, last_name = ?, is_subscribed = ?
            WHERE user_id = ?
        ''', (
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name,
            True,
            message.from_user.id
        ))
    
    conn.commit()
    conn.close()
    
    await message.answer(
        "👋 Добро пожаловать! Вы подписались на рассылку.\n"
        "Используйте /stop чтобы отписаться.",
        reply_markup=get_cancel_keyboard()
    )

@router.message(Command("stop"))
async def cmd_stop(message: Message):
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET is_subscribed = ? WHERE user_id = ?', (False, message.from_user.id))
    conn.commit()
    conn.close()
    
    await message.answer(
        "❌ Вы отписались от рассылки.\n"
        "Используйте /start чтобы подписаться снова."
    )