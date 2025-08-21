from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from db_init import init_db
from config import IMAGEKIT_PUBLIC_KEY, IMAGEKIT_PRIVATE_KEY, IMAGEKIT_URL_ENDPOINT
from werkzeug.utils import secure_filename
from imagekitio import ImageKit

# --- Flask app ---
app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("SECRET_KEY", "devsecretkey")

# Initialize DB
init_db()

# ImageKit setup
imagekit = ImageKit(
    public_key=IMAGEKIT_PUBLIC_KEY,
    private_key=IMAGEKIT_PRIVATE_KEY,
    url_endpoint=IMAGEKIT_URL_ENDPOINT
)

# Register blueprint
from route.admin import admin_bp
app.register_blueprint(admin_bp)

# --- Upload to ImageKit ---
@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    upload = imagekit.upload(
        file=file,
        file_name=secure_filename(file.filename),
        options={"folder": "/products/"}
    )

    if upload.get("error"):
        return jsonify({"error": upload["error"]["message"]}), 400

    return jsonify({
        "name": upload["response"]["name"],
        "url": upload["response"]["url"],
        "thumbnail_url": upload["response"]["thumbnailUrl"]
    })

# --- Resize / optimize URL ---
@app.route("/resize/<path:image_path>")
def resize(image_path):
    url = imagekit.url({
        "path": f"/products/{image_path}",
        "transformation": [{"height": 300, "width": 300}]
    })
    return jsonify({"optimized_url": url})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
