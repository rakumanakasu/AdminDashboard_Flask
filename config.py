import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SQLite database (relative path)
DB_PATH = os.path.join(BASE_DIR, "site.db")

# Shared folder for images
SHARED_PHOTO_FOLDER = os.path.join(BASE_DIR, "shared_photos")
os.makedirs(SHARED_PHOTO_FOLDER, exist_ok=True)
