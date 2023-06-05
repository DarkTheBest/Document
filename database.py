import sqlite3

# Создание соединения с базой данных
conn = sqlite3.connect('documents.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Создание таблицы для документов
cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        file_path TEXT,
        creator TEXT,
        UNIQUE(title, creator)
    )
''')


# Создание таблицы для пользователей
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        UNIQUE(username)
    )
''')

conn.commit()
conn.close()
