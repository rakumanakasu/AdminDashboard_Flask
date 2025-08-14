from flask import Flask, flash
from route.admin import admin_bp  # <-- updated import
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'devsecretkey')

# Register Blueprint
app.register_blueprint(admin_bp)



if __name__ == '__main__':
    app.run(debug=True)
