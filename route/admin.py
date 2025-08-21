import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
from config import DB_PATH, IMAGEKIT_PUBLIC_KEY, IMAGEKIT_PRIVATE_KEY, IMAGEKIT_URL_ENDPOINT
from werkzeug.utils import secure_filename
from imagekitio import ImageKit

admin_bp = Blueprint(
    'admin',
    __name__,
    template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '../templates'),
)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ImageKit setup
imagekit = ImageKit(
    public_key=IMAGEKIT_PUBLIC_KEY,
    private_key=IMAGEKIT_PRIVATE_KEY,
    url_endpoint=IMAGEKIT_URL_ENDPOINT
)

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

            image_url = None
            if image_file and image_file.filename != '':
                upload = imagekit.upload(
                    file=image_file,
                    file_name=secure_filename(image_file.filename),
                    options={"folder": "/products/"}
                )
                if upload.get("error"):
                    flash(f"Image upload error: {upload['error']['message']}", "danger")
                    return render_template('admin/add_product.html')
                image_url = upload['response']['url']

            conn = get_db_connection()
            conn.execute(
                "INSERT INTO products (title, description, price, category, image) VALUES (?, ?, ?, ?, ?)",
                (title, description, price, category, image_url)
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
    try:
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

        image_url = product['image']

        if image_file and image_file.filename != '':
            upload = imagekit.upload(
                file=image_file,
                file_name=secure_filename(image_file.filename),
                options={"folder": "/products/"}
            )
            if upload.get("error"):
                return jsonify({"status": "error", "message": upload["error"]["message"]}), 400
            image_url = upload['response']['url']

        cur.execute(
            "UPDATE products SET title=?, category=?, price=?, image=? WHERE id=?",
            (title, category, price, image_url, product_id)
        )
        conn.commit()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Product updated successfully",
            "image_url": image_url
        })

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

# ---------------- Delete Product via AJAX ----------------
@admin_bp.route('/product/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    try:
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

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
