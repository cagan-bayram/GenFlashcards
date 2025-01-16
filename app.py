from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# Set your OpenRouter API key here
API_KEY = "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"
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

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

if __name__ == '__main__':
    app.run(debug=True)