# db_init.py
import sqlite3, os
from config import DB_PATH

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        image TEXT,
        category TEXT,
        rating_rate REAL DEFAULT 0,
        rating_count INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

print(f"Initializing DB at: {DB_PATH}")
