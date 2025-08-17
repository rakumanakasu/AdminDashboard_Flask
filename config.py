import os

# Absolute path to the shared SQLite database
DB_PATH = r"D:\Dara\PythonAPI\exam\FlaskProject\site.db"

# Central shared folder for images
SHARED_PHOTO_FOLDER = r"D:\Dara\PythonAPI\exam\shared_photos"
os.makedirs(SHARED_PHOTO_FOLDER, exist_ok=True)
