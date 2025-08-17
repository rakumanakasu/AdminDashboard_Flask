

from flask import Flask, flash
from route.admin import admin_bp
import os


from flask import send_from_directory
from config import SHARED_PHOTO_FOLDER



app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'devsecretkey')

# Register Blueprint
app.register_blueprint(admin_bp)

@app.route('/photos/<filename>')
def shared_photos(filename):
    return send_from_directory(SHARED_PHOTO_FOLDER, filename)


if __name__ == '__main__':
    app.run(debug=True)
