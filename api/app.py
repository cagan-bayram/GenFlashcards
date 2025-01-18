from flask import Flask, request, jsonify, render_template
import os
import json
import firebase_admin
import requests
from firebase_admin import credentials, firestore
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app
app = Flask(__name__, static_folder='../static', template_folder='../templates')
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Initialize Firebase Admin SDK
firebase_config = json.loads(os.getenv("FIREBASE_CONFIG"))
cred = credentials.Certificate(firebase_config)  # Replace with your JSON file path
firebase_admin.initialize_app(cred)
db = firestore.client()

# Flask-Login setup
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
    doc = db.collection("users").document(user_id).get()
    if doc.exists:
        data = doc.to_dict()
        return User(id=doc.id, username=data["username"])
    return None

@app.route('/')
def index():
    return render_template('index.html')

# Signup route
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    hashed_password = generate_password_hash(password)

    try:
        # Add user to Firestore
        user_ref = db.collection("users").where("username", "==", username).get()
        if user_ref:
            return jsonify({"error": "Username already exists"}), 400
        user_doc = db.collection("users").add({"username": username, "password": hashed_password})
        return jsonify({"message": "Signup successful!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Login route
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        user_docs = db.collection("users").where("username", "==", username).get()
        if not user_docs:
            return jsonify({"error": "Invalid credentials"}), 400
        user_data = user_docs[0].to_dict()
        if not check_password_hash(user_data["password"], password):
            return jsonify({"error": "Invalid credentials"}), 400
        user = User(id=user_docs[0].id, username=user_data["username"])
        login_user(user)
        return jsonify({"message": "Login successful!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Logout route
@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully!"}), 200

# Generate flashcards
@app.route('/generate', methods=['POST'])
def generate_flashcards():
    data = request.json
    topic = data.get('topic', '')

    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    try:
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "meta-llama/llama-3.2-3b-instruct:free",
            "messages": [
                {"role": "user", "content": f"Generate flashcards for the topic: {topic}. Format as question-answer pairs."}
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"].strip()
        return jsonify({"flashcards": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Save flashcards
@app.route('/save', methods=['POST'])
@login_required
def save_flashcards():
    data = request.json
    topic = data.get('topic', '')
    flashcards = data.get('flashcards', '')

    if not topic or not flashcards:
        return jsonify({"error": "Topic and flashcards are required"}), 400

    try:
        # Save flashcards to Firestore
        db.collection("flashcards").add({
            "topic": topic,
            "flashcards": flashcards,
            "user_id": current_user.id
        })
        return jsonify({"message": "Flashcards saved successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get flashcards
@app.route('/flashcards', methods=['GET'])
@login_required
def get_flashcards_paginated():
    try:
        user_flashcards = db.collection("flashcards").where("user_id", "==", current_user.id).stream()
        flashcards = [{"topic": doc.to_dict()["topic"], "flashcards": doc.to_dict()["flashcards"]} for doc in user_flashcards]
        return jsonify(flashcards), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

