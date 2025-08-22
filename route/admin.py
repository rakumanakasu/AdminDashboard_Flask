import os
import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER, DB_PATH

admin_bp = Blueprint(
    'admin',
    __name__,
    template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '../templates')
)

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- DB Connection ----------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- Dashboard ----------------
@admin_bp.route('/')
def dashboard():
    try:
        conn = get_db_connection()
        products = conn.execute("SELECT * FROM products").fetchall()
        conn.close()
        products = [dict(p) for p in products]
        return render_template('dashboard.html', products=products)
    except sqlite3.Error as e:
        flash(f"Database error: {e}", 'danger')
        return render_template('dashboard.html', products=[])

# ---------------- Add Product ----------------
@admin_bp.route("/add", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        price = request.form.get("price")
        category = request.form.get("category")
        image_file = request.files.get("image")

        image_url = None

        if image_file and image_file.filename != "":
            filename = secure_filename(image_file.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            image_file.save(save_path)

            # Full public URL
            image_url = f"https://admindashboardflask-production-1a1e.up.railway.app/uploads/{filename}"

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (title, description, price, category, image) VALUES (?, ?, ?, ?, ?)",
            (title, description, price, category, image_url)
        )
        conn.commit()
        conn.close()

        flash("Product added successfully!", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/add_product.html")

# ---------------- Edit Product ----------------
@admin_bp.route("/product/edit", methods=["POST"])
def edit_product():
    product_id = request.form.get("product_id")
    title = request.form.get("title")
    category = request.form.get("category")
    price = request.form.get("price")
    image_file = request.files.get("image")

    if not all([product_id, title, category, price]):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    try:
        product_id = int(product_id)
        price = float(price)
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid product ID or price"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT image FROM products WHERE id=?", (product_id,))
    product = cur.fetchone()
    if not product:
        conn.close()
        return jsonify({"status": "error", "message": "Product not found"}), 404

    image_url = product["image"]

    # Upload new image if provided
    if image_file and image_file.filename != "":
        filename = secure_filename(image_file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(save_path)
        image_url = f"https://admindashboardflask-production-1a1e.up.railway.app/uploads/{filename}"

    # Update DB
    cur.execute(
        "UPDATE products SET title=?, category=?, price=?, image=? WHERE id=?",
        (title, category, price, image_url, product_id)
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": "Product updated successfully", "image_url": image_url})

# ---------------- Delete Product ----------------
@admin_bp.route('/product/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE id=?", (product_id,))
    product = cur.fetchone()
    if not product:
        conn.close()
        return jsonify({"status": "error", "message": "Product not found"}), 404

    cur.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Product deleted successfully"})
