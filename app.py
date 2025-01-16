# app.py

from flask import Flask, request, jsonify, render_template
import os
import sqlite3
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import requests

# Create the Flask app instance
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Set up your environment variable and base URL
API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('flashcards.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return User(id=row[0], username=row[1])
    return None

# Initialize the database
def init_db():
    conn = sqlite3.connect('flashcards.db')
    cursor = conn.cursor()
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # Create flashcards table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            flashcards TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    hashed_password = generate_password_hash(password)
    try:
        conn = sqlite3.connect('flashcards.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()
        return jsonify({"message": "Signup successful!"}), 200
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    conn = sqlite3.connect('flashcards.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, password FROM users WHERE username = ?', (username,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data and check_password_hash(user_data[2], password):
        user = User(id=user_data[0], username=user_data[1])
        login_user(user)
        return jsonify({"message": "Login successful!"}), 200
    return jsonify({"error": "Invalid credentials"}), 400

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully!"}), 200

@app.route('/generate', methods=['POST'])
def generate_flashcards():
    data = request.json
    topic = data.get('topic', '')

    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "meta-llama/llama-3.2-3b-instruct:free",
            "messages": [
                {"role": "user", "content": f"Generate flashcards for the topic: {topic}. Format as question-answer pairs."}
            ]
        }

        response = requests.post(BASE_URL, headers=headers, json=payload)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"].strip()
        return jsonify({"flashcards": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/save', methods=['POST'])
@login_required
def save_flashcards():
    data = request.json
    topic = data.get('topic', '')
    flashcards = data.get('flashcards', '')

    if not topic or not flashcards:
        return jsonify({"error": "Topic and flashcards are required"}), 400

    try:
        conn = sqlite3.connect('flashcards.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO flashcards (topic, flashcards, user_id) VALUES (?, ?, ?)',
                       (topic, flashcards, current_user.id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Flashcards saved successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/flashcards', methods=['GET'])
@login_required
def get_flashcards_paginated():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit

        conn = sqlite3.connect('flashcards.db')
        cursor = conn.cursor()
        cursor.execute('SELECT topic, flashcards FROM flashcards WHERE user_id = ? LIMIT ? OFFSET ?',
                       (current_user.id, limit, offset))
        rows = cursor.fetchall()
        conn.close()

        flashcards = [{"topic": row[0], "flashcards": row[1]} for row in rows]
        return jsonify(flashcards), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
