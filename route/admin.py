import os
import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash

admin_bp = Blueprint(
    'admin',
    __name__,
    template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '../templates'),
    static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '../static')
)

# Path to your existing database
# DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(D:\Dara\PythonAPI\FlaskProject\site.db))), 'site.db')

# Path to your existing database
DB_PATH = r"D:\Dara\PythonAPI\FlaskProject\site.db"




def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Dashboard - list products
@admin_bp.route('/')
def dashboard():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    conn.close()
    return render_template('dashboard.html', products=products)

# Add Product

@admin_bp.route('/product/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        category = request.form.get('category')
        image_file = request.files.get('image')

        image_filename = None
        if image_file:
            image_filename = image_file.filename
            # Save images to static/images
            # image_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images')
            image_folder = r"D:\Dara\PythonAPI\FlaskProject\static\images"
            os.makedirs(image_folder, exist_ok=True)
            image_file.save(os.path.join(image_folder, image_filename))

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO products (title, description, price, category, image)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, description, price, category, image_filename))
            conn.commit()
            conn.close()
            flash('Product added successfully!', 'success')
            return redirect(url_for('admin.add_product'))
        except Exception as e:
            flash(f'Error: {e}', 'danger')

    return render_template('admin/add_product.html')
