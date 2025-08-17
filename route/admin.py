import sqlite3
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash,send_from_directory, current_app
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

@admin_bp.route('/')
def dashboard():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM products")
        products = cur.fetchall()
        conn.close()
        products = [dict(p) for p in products]
        return render_template('dashboard.html', products=products)
    except sqlite3.Error as e:
        flash(f"Database error: {e}", 'danger')
        return render_template('dashboard.html', products=[])

@admin_bp.route('/product/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        category = request.form.get('category')
        image_file = request.files.get('image')

        try:
            price = float(price)
        except ValueError:
            flash("Invalid price value.", "danger")
            return redirect(url_for('admin.add_product'))

        image_filename = None
        if image_file and image_file.filename != '':
            image_filename = image_file.filename
            filepath = os.path.join(SHARED_PHOTO_FOLDER, image_filename)
            try:
                image_file.save(filepath)
            except Exception as e:
                flash(f"Failed to save image: {e}", 'danger')
                return redirect(url_for('admin.add_product'))

        try:
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO products (title, description, price, category, image)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, description, price, category, image_filename))
            conn.commit()
            conn.close()
            flash('Product added successfully!', 'success')
            return redirect(url_for('admin.add_product'))
        except sqlite3.Error as e:
            flash(f'Database error: {e}', 'danger')

    return render_template('admin/add_product.html')

@admin_bp.route('/product/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Get product info to delete image
        cur.execute("SELECT image FROM products WHERE id=?", (product_id,))
        product = cur.fetchone()
        if product:
            image_filename = product['image']
            if image_filename:
                image_path = os.path.join(SHARED_PHOTO_FOLDER, image_filename)
                if os.path.exists(image_path):
                    os.remove(image_path)  # Delete the image file

            # Delete from database
            cur.execute("DELETE FROM products WHERE id=?", (product_id,))
            conn.commit()
            flash('Product deleted successfully!', 'success')
        else:
            flash('Product not found.', 'warning')
        conn.close()
    except Exception as e:
        flash(f'Error deleting product: {e}', 'danger')

    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/exit')
def exit_admin():
    flash('You have exited the dashboard.', 'info')
    return redirect('/')
