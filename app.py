
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3.2",
                "messages": data["messages"],
                "stream": False
            },
            timeout=180
        )
        response.raise_for_status()
        answer = response.json()["message"]["content"]
        return jsonify({"reply": answer})

    except requests.RequestException:
        return jsonify({
            "error": "Ollama connection failed. Check Ollama."
        }), 503

if __name__ == "__main__":
    app.run(debug=True, port=5000)
