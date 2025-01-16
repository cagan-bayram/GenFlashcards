from flask import Flask, request, jsonify, render_template
import os
import requests

# Create the Flask app instance
app = Flask(__name__)

# Set up your environment variable and base URL
API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# Define routes
@app.route('/')
def index():
    return render_template('index.html')

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

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
