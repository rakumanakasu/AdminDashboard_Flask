# import sqlite3
#
# DB_PATH = r"D:\Dara\PythonAPI\exam\FlaskProject\site.db"
#
# def get_products_from_db():
#     conn = sqlite3.connect(DB_PATH)
#     conn.row_factory = sqlite3.Row
#     cur = conn.cursor()
#     cur.execute("SELECT * FROM products")
#     rows = cur.fetchall()
#     conn.close()
#     return [dict(row) for row in rows]
