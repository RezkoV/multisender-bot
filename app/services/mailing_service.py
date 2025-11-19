from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from app.database.simple_db import db  # Добавьте этот импорт
import asyncio

async def send_mailing(bot: Bot, mailing_data):
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT user_id FROM users WHERE is_subscribed = 1')
    users = cursor.fetchall()
    conn.close()
    
    success_count = 0
    
    for user in users:
        user_id = user[0]
        try:
            if mailing_data.get('media_type') == 'photo':
                await bot.send_photo(
                    chat_id=user_id,
                    photo=mailing_data['media_file_id'],
                    caption=mailing_data['text']
                )
            elif mailing_data.get('media_type') == 'video':
                await bot.send_video(
                    chat_id=user_id,
                    video=mailing_data['media_file_id'],
                    caption=mailing_data['text']
                )
            elif mailing_data.get('media_type') == 'document':
                await bot.send_document(
                    chat_id=user_id,
                    document=mailing_data['media_file_id'],
                    caption=mailing_data['text']
                )
            else:
                await bot.send_message(
                    chat_id=user_id,
                    text=mailing_data['text']
                )
            success_count += 1
        except TelegramBadRequest:
            # Пользователь заблокировал бота - отписываем
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET is_subscribed = 0 WHERE user_id = ?', (user_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Ошибка при отправке пользователю {user_id}: {e}")
        
        await asyncio.sleep(0.05)
    
    return success_count