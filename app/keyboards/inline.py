from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_admin_menu():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="📊 Статистика", callback_data="admin_stats")
    keyboard.button(text="📨 Создать рассылку", callback_data="create_mailing")
    keyboard.button(text="📋 История рассылок", callback_data="mailing_history")
    keyboard.button(text="👥 Управление подписчиками", callback_data="manage_users")
    keyboard.button(text="📥 Экспорт пользователей", callback_data="export_users")
    keyboard.adjust(1)
    return keyboard.as_markup()

def get_mailing_type_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="📝 Только текст", callback_data="mailing_text")
    keyboard.button(text="🖼 Текст + фото", callback_data="mailing_photo")
    keyboard.button(text="🎥 Текст + видео", callback_data="mailing_video")
    keyboard.button(text="📎 Текст + документ", callback_data="mailing_document")
    keyboard.button(text="❌ Отмена", callback_data="cancel")
    keyboard.adjust(1)
    return keyboard.as_markup()

def get_confirmation_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="✅ Отправить сейчас", callback_data="send_now")
    keyboard.button(text="⏰ Запланировать", callback_data="schedule")
    keyboard.button(text="✏️ Редактировать", callback_data="edit")
    keyboard.button(text="❌ Отмена", callback_data="cancel")
    keyboard.adjust(2)
    return keyboard.as_markup()

def get_cancel_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="❌ Отмена", callback_data="cancel")
    return keyboard.as_markup()