

from flask import Flask, flash
from route.admin import admin_bp
from flask_cors import CORS
import os


from flask import send_from_directory
from config import SHARED_PHOTO_FOLDER



app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('SECRET_KEY', 'devsecretkey')

# Register Blueprint
app.register_blueprint(admin_bp)

@app.route('/photos/<filename>')
def shared_photos(filename):
    return send_from_directory(SHARED_PHOTO_FOLDER, filename)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
