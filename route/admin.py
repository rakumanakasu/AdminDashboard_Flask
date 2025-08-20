import sqlite3
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from config import DB_PATH, SHARED_PHOTO_FOLDER

admin_bp = Blueprint(
    'admin',
    __name__,
    template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '../templates'),
)

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
@admin_bp.route('/product/add', methods=['GET', 'POST'])
def add_product():
    try:
        if request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')
            price = float(request.form.get('price'))
            category = request.form.get('category')
            image_file = request.files.get('image')

            image_filename = None
            if image_file and image_file.filename != '':
                from werkzeug.utils import secure_filename
                image_filename = secure_filename(image_file.filename)
                os.makedirs(SHARED_PHOTO_FOLDER, exist_ok=True)
                image_file.save(os.path.join(SHARED_PHOTO_FOLDER, image_filename))

            conn = get_db_connection()
            conn.execute(
                "INSERT INTO products (title, description, price, category, image) VALUES (?, ?, ?, ?, ?)",
                (title, description, price, category, image_filename)
            )
            conn.commit()
            conn.close()
            flash('Product added successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        return render_template('admin/add_product.html')
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        flash(f"Error: {e}", "danger")
        return render_template('admin/add_product.html')



# ---------------- Edit Product via AJAX ----------------
@admin_bp.route('/product/edit', methods=['POST'])
def edit_product_ajax():
    product_id = int(request.form['product_id'])
    title = request.form['title']
    category = request.form['category']
    price = float(request.form['price'])
    image_file = request.files.get('image')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT image FROM products WHERE id=?", (product_id,))
    product = cur.fetchone()

    if not product:
        conn.close()
        return jsonify({"status": "error", "message": "Product not found"}), 404

    image_filename = product['image']
    if image_file and image_file.filename != '':
        # Delete old image
        if image_filename:
            old_path = os.path.join(SHARED_PHOTO_FOLDER, image_filename)
            if os.path.exists(old_path):
                os.remove(old_path)
        # Save new image
        image_filename = image_file.filename
        image_file.save(os.path.join(SHARED_PHOTO_FOLDER, image_filename))

    cur.execute(
        "UPDATE products SET title=?, category=?, price=?, image=? WHERE id=?",
        (title, category, price, image_filename, product_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Product updated successfully"})


# ---------------- Delete Product via AJAX ----------------
@admin_bp.route('/product/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT image FROM products WHERE id=?", (product_id,))
        product = cur.fetchone()

        if not product:
            conn.close()
            return jsonify({"status": "error", "message": "Product not found"}), 404

        image_filename = product['image']
        if image_filename:
            image_path = os.path.join(SHARED_PHOTO_FOLDER, image_filename)
            if os.path.exists(image_path):
                os.remove(image_path)

        cur.execute("DELETE FROM products WHERE id=?", (product_id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Product deleted successfully"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
