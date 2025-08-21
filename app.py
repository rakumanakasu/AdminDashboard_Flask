from flask import Flask, flash, request, send_from_directory
from flask_cors import CORS
import os
from db_init import init_db   # init_db BEFORE importing admin_bp
from config import SHARED_PHOTO_FOLDER



app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('SECRET_KEY', 'devsecretkey')


# ----------------- Initialize DB -----------------
init_db()



# Register Blueprint
from route.admin import admin_bp
app.register_blueprint(admin_bp)

@app.route('/photos/<filename>')
def shared_photos(filename):
    return send_from_directory(SHARED_PHOTO_FOLDER, filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    filename = file.filename
    file.save(os.path.join(SHARED_PHOTO_FOLDER, filename))
    return {"message": "Uploaded successfully", "url": f"/photos/{filename}"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
