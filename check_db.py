import sqlite3
from config import DB_PATH

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(products);")
columns = cursor.fetchall()

print("Products table columns:")
for col in columns:
    print(col)

conn.close()
