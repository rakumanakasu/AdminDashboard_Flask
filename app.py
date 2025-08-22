from flask import Flask
from flask_cors import CORS
import os
from db_init import init_db
from route.admin import admin_bp
from config import UPLOAD_FOLDER

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("SECRET_KEY", "devsecretkey")

# Initialize DB
init_db()

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Register blueprint
app.register_blueprint(admin_bp)

# Route to serve uploaded images dynamically
from flask import send_from_directory

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
