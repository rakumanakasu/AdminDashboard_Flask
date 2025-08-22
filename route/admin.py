import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER, DB_PATH
import sqlite3

admin_bp = Blueprint(
    'admin',
    __name__,
    template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '../templates'),
)

# Make sure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------- DB Connection ----------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


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
            # Secure filename
            filename = secure_filename(image_file.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)

            # Save file to local upload folder
            image_file.save(save_path)

            # Construct **full public URL** for the image
            # Replace this domain with your Railway public URL
            image_url = f"https://admindashboardflask-production-1a1e.up.railway.app/static/uploads/{filename}"

        # Save product to DB
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
