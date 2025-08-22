import os
import pymysql
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER, DB_HOST, DB_USER, DB_PASS, DB_NAME, DB_PORT

admin_bp = Blueprint(
    'admin',
    __name__,
    template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '../templates')
)

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- DB Connection ----------------
def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        port=DB_PORT,
        cursorclass=pymysql.cursors.DictCursor
    )

# ---------------- Products API ----------------
@admin_bp.route("/api/products")
def api_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return jsonify(products)

# ---------------- Rate Product ----------------
@admin_bp.route("/api/product/<int:product_id>/rate", methods=["POST", "OPTIONS"])
def rate_product(product_id):
    # Handle OPTIONS preflight
    if request.method == "OPTIONS":
        return '', 200

    data = request.get_json()
    if not data or 'rating' not in data:
        return jsonify({"status": "error", "message": "Missing rating"}), 400

    try:
        rating = float(data['rating'])
        if rating < 0 or rating > 5:
            return jsonify({"status": "error", "message": "Rating must be between 0 and 5"}), 400
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid rating value"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT rating_rate, rating_count FROM products WHERE id=%s", (product_id,))
            product = cursor.fetchone()
            if not product:
                return jsonify({"status": "error", "message": "Product not found"}), 404

            current_rate = product['rating_rate'] or 0
            current_count = product['rating_count'] or 0

            new_count = current_count + 1
            new_rate = ((current_rate * current_count) + rating) / new_count

            cursor.execute(
                "UPDATE products SET rating_rate=%s, rating_count=%s WHERE id=%s",
                (new_rate, new_count, product_id)
            )
        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Rating submitted",
            "rating_rate": round(new_rate, 1),
            "rating_count": new_count
        })
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()
