import sqlite3
from datetime import datetime

# Создаём базу данных
conn = sqlite3.connect('coffee_bot.db', check_same_thread=False)
cursor = conn.cursor()

# Создаём таблицу пользователей
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    bonus_points INTEGER DEFAULT 0,
    total_orders INTEGER DEFAULT 0
)
''')

# Создаём таблицу заказов
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    item_name TEXT,
    price INTEGER,
    order_date TEXT,
    status TEXT DEFAULT 'new'
)
''')

conn.commit()

def get_or_create_user(user_id, username):
    """Получить пользователя или создать нового"""
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    
    if not user:
        cursor.execute(
            'INSERT INTO users (user_id, username) VALUES (?, ?)',
            (user_id, username)
        )
        conn.commit()
        return 0, 0  # бонусы, заказы
    
    return user[2], user[3]  # бонусы, заказы

def add_order(user_id, item_name, price):
    """Добавить заказ"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute(
        'INSERT INTO orders (user_id, item_name, price, order_date) VALUES (?, ?, ?, ?)',
        (user_id, item_name, price, now)
    )
    
    # Увеличиваем счётчик заказов и бонусов
    cursor.execute(
        'UPDATE users SET total_orders = total_orders + 1, bonus_points = bonus_points + 1 WHERE user_id = ?',
        (user_id,)
    )
    
    conn.commit()
    
    # Проверяем, не получил ли пользователь бесплатный кофе
    cursor.execute('SELECT bonus_points, total_orders FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    
    if user[1] % 10 == 0 and user[1] > 0:  # каждый 10-й заказ
        cursor.execute(
            'UPDATE users SET bonus_points = bonus_points + 1 WHERE user_id = ?',
            (user_id,)
        )
        conn.commit()
        return True  # получил бонус
    
    return False

def get_user_stats(user_id):
    """Получить статистику пользователя"""
    cursor.execute(
        'SELECT bonus_points, total_orders FROM users WHERE user_id = ?',
        (user_id,)
    )
    return cursor.fetchone()
