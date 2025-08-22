# db_init.py
import pymysql
from config import DB_HOST, DB_USER, DB_PASS, DB_NAME, DB_PORT

def init_db():
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        port=DB_PORT,
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        price DECIMAL(10,2) NOT NULL,
        image VARCHAR(255),
        category VARCHAR(100),
        rating_rate FLOAT DEFAULT 0,
        rating_count INT DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

print("MySQL DB initialized!")

