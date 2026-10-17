
import os
import requests
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

OLLAMA_URL = "https://ollama.com/api/chat"
MODEL = "gpt-oss:120b-cloud"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    api_key = os.environ.get("OLLAMA_API_KEY")

    if not api_key:
        return jsonify({
            "error": "OLLAMA_API_KEY is not configured."
        }), 500

    data = request.get_json(silent=True) or {}
    messages = data.get("messages", [])

    if not isinstance(messages, list) or not messages:
        return jsonify({
            "error": "Please enter a message."
        }), 400

    # Validate the message structure
    safe_messages = []

    for message in messages[-20:]:
        if not isinstance(message, dict):
            continue

        role = message.get("role")
        content = message.get("content")

        if role not in ("user", "assistant"):
            continue

        if not isinstance(content, str) or not content.strip():
            continue

        safe_messages.append({
            "role": role,
            "content": content[:4000]
        })

    if not safe_messages or safe_messages[-1]["role"] != "user":
        return jsonify({
            "error": "Please send a valid user message."
        }), 400

    safe_messages.insert(0, {
        "role": "system",
        "content": "You are a helpful AI assistant. "
                   "Give clear and friendly answers."
    })

    try:
        response = requests.post(
            OLLAMA_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": safe_messages,
                "stream": False
            },
            timeout=180
        )

        response.raise_for_status()

        answer = response.json()["message"]["content"]

        return jsonify({"reply": answer})

    except requests.RequestException:
        app.logger.exception("Ollama API request failed")

        return jsonify({
            "error": "AI service request failed. "
                     "Check the Vercel function logs."
        }), 502


if __name__ == "__main__":
    app.run(debug=True, port=5000)
