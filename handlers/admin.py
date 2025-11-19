from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import csv
from io import StringIO
from aiogram.types import BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import config
from database.simple_db import db
from keyboards.inline import get_admin_menu, get_mailing_type_keyboard
from utils.states import MailingStates

router = Router()

def is_admin(user_id: int):
    return user_id in config.ADMIN_IDS

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Доступ запрещен")
        return
    
    await message.answer(
        "🛠 Панель администратора",
        reply_markup=get_admin_menu()
    )

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен")
        return
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_subscribed = 1')
    active_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM mailings')
    total_mailings = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM mailings WHERE is_sent = 1')
    sent_mailings = cursor.fetchone()[0]
    
    conn.close()
    
    stats_text = (
        "📊 Статистика бота:\n\n"
        f"👥 Всего пользователей: {total_users}\n"
        f"✅ Активных подписчиков: {active_users}\n"
        f"📨 Всего рассылок: {total_mailings}\n"
        f"📤 Отправлено рассылок: {sent_mailings}"
    )
    
    await callback.message.edit_text(stats_text, reply_markup=get_admin_menu())

@router.callback_query(F.data == "create_mailing")
async def create_mailing(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен")
        return
    
    await callback.message.edit_text(
        "📨 Выберите тип рассылки:",
        reply_markup=get_mailing_type_keyboard()
    )
    await state.set_state(MailingStates.waiting_for_content)

@router.callback_query(F.data == "mailing_history")
async def mailing_history(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен")
        return
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT name, created_at, sent_count, total_count, is_sent FROM mailings ORDER BY created_at DESC LIMIT 10')
    mailings = cursor.fetchall()
    conn.close()
    
    if not mailings:
        text = "📋 История рассылок пуста"
    else:
        text = "📋 История рассылок:\n\n"
        for mailing in mailings:
            name, created_at, sent_count, total_count, is_sent = mailing
            status = "✅ Отправлено" if is_sent else "⏳ Ожидает"
            text += f"📨 {name}\n🕒 {created_at}\n📊 {status} | {sent_count}/{total_count} пользователей\n" + "─" * 30 + "\n"
    
    await callback.message.edit_text(text, reply_markup=get_admin_menu())

@router.callback_query(F.data == "manage_users")
async def manage_users(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен")
        return
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_subscribed = 1')
    active_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_subscribed = 0')
    unsubscribed_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT username, first_name, created_at FROM users WHERE is_subscribed = 1 ORDER BY created_at DESC LIMIT 5')
    recent_users = cursor.fetchall()
    conn.close()
    
    text = f"👥 Управление подписчиками\n\n📊 Статистика:\n• Всего пользователей: {total_users}\n• Активных подписчиков: {active_users}\n• Отписавшихся: {unsubscribed_users}\n\n"
    
    if recent_users:
        text += "🆕 Последние подписчики:\n"
        for user in recent_users:
            username, first_name, created_at = user
            display_name = f"@{username}" if username else first_name
            text += f"• {display_name} - {created_at[:16]}\n"
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="📥 Экспорт пользователей", callback_data="export_users")
    keyboard.button(text="🔄 Обновить", callback_data="manage_users")
    keyboard.button(text="⬅️ Назад", callback_data="admin_menu")
    keyboard.adjust(1)
    
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())

@router.callback_query(F.data == "export_users")
async def export_users(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен")
        return
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT user_id, username, first_name, last_name, is_subscribed, created_at FROM users ORDER BY created_at DESC')
    users = cursor.fetchall()
    conn.close()
    
    if not users:
        await callback.answer("📊 Нет пользователей для экспорта")
        return
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Username', 'First Name', 'Last Name', 'Subscribed', 'Created At'])
    
    for user in users:
        user_id, username, first_name, last_name, is_subscribed, created_at = user
        writer.writerow([user_id, username or '', first_name or '', last_name or '', 'Yes' if is_subscribed else 'No', created_at])
    
    csv_data = output.getvalue().encode('utf-8')
    file = BufferedInputFile(csv_data, filename="users_export.csv")
    
    await callback.message.answer_document(
        document=file,
        caption=f"📊 Экспорт пользователей\nВсего: {len(users)} записей"
    )
    
    await callback.answer("✅ Файл экспортирован")

@router.callback_query(F.data == "cancel")
async def cancel_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback.message.edit_text("❌ Действие отменено", reply_markup=get_admin_menu())
    except:
        await callback.message.answer("❌ Действие отменено", reply_markup=get_admin_menu())
    await callback.answer()

@router.callback_query(F.data == "admin_menu")
async def back_to_admin_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("🛠 Панель администратора", reply_markup=get_admin_menu())