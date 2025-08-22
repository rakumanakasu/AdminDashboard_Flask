# AdminDashboard_Flask
AdminDashboard_Flask

An Admin Dashboard built with Flask that allows you to manage products (CRUD: Create, Read, Update, Delete).
It includes features such as product listing, category management, image upload, and inline editing with Vue.js + Bootstrap.

Features

🔑 Admin dashboard for managing products

📦 Add, edit, delete products with images

📂 Upload images (supports local storage or ImageKit)

📊 Table view with ID, Title, Category, Price, and Image

🖼 Modal form for editing products

⚡ Vue.js for reactive frontend actions

Tech Stack

Backend: Flask (Python)

Frontend: Bootstrap + Vue.js

Database: SQLite (default, can switch to MySQL/PostgreSQL)

Deployment: Works on Railway / Render / Localhost

Installation

# Clone the repository
git clone https://github.com/rakumanakasu/AdminDashboard_Flask.git
cd AdminDashboard_Flask

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

Run the App

flask run
App will be available at:
👉 http://127.0.0.1:5000

