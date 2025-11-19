import os
from dotenv import load_dotenv

# Покажите текущую рабочую директорию
print(f"Текущая папка: {os.getcwd()}")

# Покажите файлы в текущей папке
print("Файлы в папке:", os.listdir('.'))

load_dotenv()

# Проверьте загрузился ли токен
token_from_env = os.getenv('BOT_TOKEN')
print(f"Токен из .env: {token_from_env}")

class Config:
    BOT_TOKEN = token_from_env or "8559720248:AAHF0pD0hxrYVePMIOzOU0exK8tDcrZoJj0"
    ADMIN_IDS = [5706535253]
    DATABASE_URL = "sqlite:///bot.db"
    
config = Config()
print(f"Итоговый токен: {config.BOT_TOKEN}")