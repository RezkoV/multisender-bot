from aiogram.fsm.state import State, StatesGroup

class MailingStates(StatesGroup):
    waiting_for_content = State()
    waiting_for_text = State()
    waiting_for_media = State()
    waiting_for_buttons = State()
    waiting_for_confirmation = State()
    waiting_for_schedule = State()