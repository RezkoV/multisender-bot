from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
import json
from datetime import datetime

from database.simple_db import db
from keyboards.inline import get_confirmation_keyboard, get_cancel_keyboard, get_admin_menu
from utils.states import MailingStates
from services.mailing_service import send_mailing

router = Router()

@router.callback_query(F.data.startswith("mailing_"), StateFilter(MailingStates.waiting_for_content))
async def process_mailing_type(callback: CallbackQuery, state: FSMContext):
    mailing_type = callback.data.split("_")[1]
    await state.update_data(mailing_type=mailing_type)
    
    await callback.message.edit_text(
        "📝 Введите текст рассылки:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(MailingStates.waiting_for_text)

@router.message(StateFilter(MailingStates.waiting_for_text))
async def process_mailing_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    data = await state.get_data()
    
    if data.get('mailing_type') == 'text':
        preview_text = f"📋 Превью рассылки:\n\n{message.text}"
        await message.answer(preview_text, reply_markup=get_confirmation_keyboard())
        await state.set_state(MailingStates.waiting_for_confirmation)
    else:
        await message.answer(
            "📎 Теперь отправьте медиа-файл (фото, видео или документ):",
            reply_markup=get_cancel_keyboard()
        )
        await state.set_state(MailingStates.waiting_for_media)

@router.message(StateFilter(MailingStates.waiting_for_media), F.photo | F.video | F.document)
async def process_mailing_media(message: Message, state: FSMContext):
    data = await state.get_data()
    
    if message.photo:
        await state.update_data(media_type='photo', media_file_id=message.photo[-1].file_id)
    elif message.video:
        await state.update_data(media_type='video', media_file_id=message.video.file_id)
    elif message.document:
        await state.update_data(media_type='document', media_file_id=message.document.file_id)
    
    preview_text = f"📋 Превью рассылки:\n\n{data['text']}"
    
    if data.get('media_type') == 'photo':
        await message.answer_photo(
            photo=data['media_file_id'],
            caption=preview_text,
            reply_markup=get_confirmation_keyboard()
        )
    elif data.get('media_type') == 'video':
        await message.answer_video(
            video=data['media_file_id'],
            caption=preview_text,
            reply_markup=get_confirmation_keyboard()
        )
    elif data.get('media_type') == 'document':
        await message.answer_document(
            document=data['media_file_id'],
            caption=preview_text,
            reply_markup=get_confirmation_keyboard()
        )
    
    await state.set_state(MailingStates.waiting_for_confirmation)

@router.callback_query(F.data == "send_now", StateFilter(MailingStates.waiting_for_confirmation))
async def send_mailing_now(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Считаем количество подписчиков
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_subscribed = 1')
    total_count = cursor.fetchone()[0]
    
    # Создаем запись о рассылке
    cursor.execute('''
        INSERT INTO mailings (name, message_text, photo, video, document, buttons, total_count)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        f"Рассылка {datetime.now()}",
        data.get('text', ''),
        data.get('media_file_id') if data.get('media_type') == 'photo' else None,
        data.get('media_file_id') if data.get('media_type') == 'video' else None,
        data.get('media_file_id') if data.get('media_type') == 'document' else None,
        json.dumps(data.get('buttons', [])),
        total_count
    ))
    
    mailing_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Отправляем рассылку
    success_count = await send_mailing(callback.bot, data)
    
    # Обновляем статистику
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE mailings SET is_sent = 1, sent_count = ? WHERE id = ?', (success_count, mailing_id))
    conn.commit()
    conn.close()
    
    await callback.message.edit_text(
        f"✅ Рассылка отправлена!\n"
        f"Успешно доставлено: {success_count}/{total_count} пользователям",
        reply_markup=get_admin_menu()
    )
    
    await state.clear()