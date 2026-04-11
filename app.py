import os
from typing import Any

import requests
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://kurim.ithope.eu/v1").rstrip("/")
MODEL = os.environ.get("OPENAI_MODEL", "gemma3:27b")

HTML = """
<!doctype html>
<html lang="cs">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Finanční AI asistent</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.5;
            background: #f8f9fb;
            color: #222;
        }
        .card {
            background: white;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 24px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.04);
        }
        h1 { margin-top: 0; }
        textarea {
            width: 100%;
            min-height: 140px;
            padding: 12px;
            font-size: 16px;
            box-sizing: border-box;
            border: 1px solid #bbb;
            border-radius: 8px;
            resize: vertical;
        }
        button {
            margin-top: 12px;
            padding: 10px 18px;
            font-size: 16px;
            border: 0;
            border-radius: 8px;
            background: #2563eb;
            color: white;
            cursor: pointer;
        }
        button:hover { background: #1d4ed8; }
        .box {
            margin-top: 20px;
            padding: 16px;
            border: 1px solid #ddd;
            background: #fafafa;
            border-radius: 8px;
            white-space: pre-wrap;
        }
        .error {
            border-color: #d33;
            background: #fff5f5;
            color: #a00;
        }
        .small {
            margin-top: 20px;
            color: #555;
            font-size: 14px;
        }
        code {
            background: #f1f1f1;
            padding: 2px 6px;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>Finanční AI asistent</h1>
        <p>Zadej finanční dotaz a aplikace vrátí odpověď pomocí AI modelu.</p>

        <form method="post" action="/">
            <textarea name="prompt" placeholder="Např. Mám 500 Kč a koupím věc za 320 Kč. Kolik mi zbyde?">{{ prompt }}</textarea>
            <br>
            <button type="submit">Odeslat</button>
        </form>

        {% if answer %}
        <div class="box">
            <strong>Odpověď:</strong><br>
            {{ answer }}
        </div>
        {% endif %}

        {% if error %}
        <div class="box error">
            <strong>Chyba:</strong><br>
            {{ error }}
        </div>
        {% endif %}

        <div class="small">
            Dostupné endpointy: <code>/</code>, <code>/ping</code>, <code>/status</code>, <code>/ai</code>
        </div>
    </div>
</body>
</html>
"""


def ask_ai(prompt: str) -> str:
    if not OPENAI_API_KEY:
        return "Chybí OPENAI_API_KEY v proměnných prostředí."

    url = f"{OPENAI_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload: dict[str, Any] = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Jsi finanční AI asistent. Odpovídej stručně, srozumitelně a česky. "
                    "Pomáhej s běžnými osobními financemi, rozpočtem, spořením a jednoduchými výpočty. "
                    "Neuváděj smyšlené údaje."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.3,
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()

    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError):
        return "AI vrátila nečekanou odpověď."


@app.route("/ping", methods=["GET"])
def ping():
    return "pong"


@app.route("/status", methods=["GET"])
def status():
    return jsonify(
        {
            "status": "ok",
            "redis": "cache",
            "model": MODEL,
            "base_url": OPENAI_BASE_URL,
            "api_key_loaded": bool(OPENAI_API_KEY),
        }
    )


@app.route("/ai", methods=["POST"])
def ai():
    data = request.get_json(silent=True)

    if not data or "prompt" not in data:
        return jsonify({"error": "missing prompt"}), 400

    prompt = str(data["prompt"]).strip()
    if not prompt:
        return jsonify({"error": "empty prompt"}), 400

    try:
        answer = ask_ai(prompt)
        return jsonify({"prompt": prompt, "answer": answer})
    except requests.RequestException as e:
        return jsonify({"error": f"AI request failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.route("/", methods=["GET", "POST"])
def home():
    prompt = ""
    answer = ""
    error = ""

    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()
        if not prompt:
            error = "Zadej dotaz."
        else:
            try:
                answer = ask_ai(prompt)
            except requests.RequestException as e:
                error = f"AI request failed: {str(e)}"
            except Exception as e:
                error = f"Unexpected error: {str(e)}"

    return render_template_string(HTML, prompt=prompt, answer=answer, error=error)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8081)))
