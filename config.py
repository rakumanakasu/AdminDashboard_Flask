import os

# Absolute path to the shared SQLite database
# DB_PATH = os.getenv("DB_PATH", "/data/site.db")

DB_PATH = r"D:\Dara\PythonAPI\exam\AdminDashboard_Flask\site.db"


UPLOAD_FOLDER = os.getenv("SHARED_PHOTO_FOLDER", "/mnt/volume/photos")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)




# ImageKit configuration (replace with your keys)
IMAGEKIT_PUBLIC_KEY = "public_VJCoZU3fQNr1iYoG2obr4vBVelw="
IMAGEKIT_PRIVATE_KEY = "private_dKHoOoUwENeQKiXERhdIk8t/hVw="
IMAGEKIT_URL_ENDPOINT = "https://ik.imagekit.io/rakumanakasu"