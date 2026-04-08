from flask import Flask, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

OLLAMA_URL = "http://172.17.0.1:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"


def build_prompt(user_input: str) -> str:
    return (
        "Jsi finanční poradce. "
        "Odpovídej pouze česky. "
        "Odpovídej stručně a srozumitelně, maximálně 3 věty. "
        "Drž se tématu peněz, úspor, nákupů a finanční rezervy. "
        "Když je dotaz o nákupu, spočítej i kolik peněz zbyde. "
        f"Dotaz: {user_input}"
    )


@app.route("/ping", methods=["GET"])
def ping():
    return "pong", 200


@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "author": "Maksym",
        "status": "ok",
        "time": datetime.now().isoformat(),
        "model": OLLAMA_MODEL
    }), 200


@app.route("/ai", methods=["POST"])
def ai():
    try:
        data = request.get_json(silent=True)

        if not data or "prompt" not in data:
            return jsonify({"error": "Chybí JSON nebo klíč 'prompt'."}), 400

        user_input = str(data["prompt"]).strip()
        if not user_input:
            return jsonify({"error": "Prompt je prázdný."}), 400

        prompt = build_prompt(user_input)

        r = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=900
        )

        r.raise_for_status()
        llm_data = r.json()
        answer = llm_data.get("response", "").strip()

        return jsonify({
            "answer": answer if answer else "Model nevrátil odpověď."
        }), 200

    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": f"Chyba komunikace s Ollamou: {str(e)}"
        }), 500

    except Exception as e:
        return jsonify({
            "error": f"Neočekávaná chyba: {str(e)}"
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
