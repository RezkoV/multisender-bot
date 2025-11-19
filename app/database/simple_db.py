import sqlite3
import json
from datetime import datetime

class SimpleDB:
    def __init__(self, db_path='bot.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                is_subscribed BOOLEAN DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица рассылок
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mailings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                message_text TEXT,
                photo TEXT,
                video TEXT,
                document TEXT,
                buttons TEXT,
                is_sent BOOLEAN DEFAULT 0,
                scheduled_time TEXT,
                sent_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                sent_count INTEGER DEFAULT 0,
                total_count INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)

# Глобальный экземпляр БД
db = SimpleDB()