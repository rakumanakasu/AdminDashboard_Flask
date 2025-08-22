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

# ---------------- DB Connection ----------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- ImageKit ----------------
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
            try:
                upload = imagekit.upload(
                    file=image_file,
                    file_name=secure_filename(image_file.filename),
                    options={"folder": "/products/"}  # correct for v4.1.0
                )
                print("UPLOAD RESULT:", upload)

                if upload.get("error"):
                    flash(f"Image upload failed: {upload['error']['message']}", "danger")
                    return redirect(url_for("admin.add_product"))

                image_url = upload["response"].get("url")

            except Exception as e:
                flash(f"Upload error: {str(e)}", "danger")
                return redirect(url_for("admin.add_product"))

        # Save to database
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

# ---------------- Edit Product via AJAX ----------------
@admin_bp.route('/product/edit', methods=['POST'])
def edit_product_ajax():
    try:
        # Validate input
        product_id = request.form.get('product_id')
        title = request.form.get('title')
        category = request.form.get('category')
        price = request.form.get('price')

        if not all([product_id, title, category, price]):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400

        try:
            product_id = int(product_id)
            price = float(price)
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid product ID or price"}), 400

        image_file = request.files.get('image')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT image FROM products WHERE id=?", (product_id,))
        product = cur.fetchone()

        if not product:
            conn.close()
            return jsonify({"status": "error", "message": "Product not found"}), 404

        image_url = product['image']  # existing image

        # Upload new image if provided
        if image_file and image_file.filename != '':
            try:
                upload = imagekit.upload(
                    file=image_file,
                    file_name=secure_filename(image_file.filename),
                    options={"folder": "/products/"}
                )
                if getattr(upload, 'error', None):
                    return jsonify({"status": "error", "message": upload.error.message}), 400

                image_url = upload.get('response', {}).get('url', image_url)
            except Exception as e:
                return jsonify({"status": "error", "message": f"Image upload failed: {str(e)}"}), 500

        # Update database
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
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500

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
