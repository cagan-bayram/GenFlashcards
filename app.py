import os

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

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
