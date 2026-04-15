import json
import os

import redis
import requests
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gemma3:27b")
REDIS_HOST = os.environ.get("REDIS_HOST", "cache")

r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

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
            background: #f8f9fb;
            color: #222;
        }
        .card {
            background: white;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 24px;
        }
        textarea {
            width: 100%;
            min-height: 120px;
            padding: 10px;
            font-size: 16px;
            box-sizing: border-box;
        }
        button {
            margin-top: 10px;
            padding: 10px 16px;
            font-size: 16px;
            cursor: pointer;
        }
        .box {
            margin-top: 20px;
            padding: 15px;
            border: 1px solid #ccc;
            background: #f7f7f7;
            border-radius: 8px;
        }
        .error {
            color: #a00;
            background: #fff3f3;
            border-color: #d66;
            white-space: pre-wrap;
        }
        .history-item {
            margin-bottom: 12px;
            padding-bottom: 12px;
            border-bottom: 1px solid #ddd;
        }
        .small {
            color: #666;
            font-size: 14px;
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

        <div class="box">
            <strong>Počet dotazů:</strong> {{ total_requests }}
        </div>

        <div class="box">
            <strong>Poslední dotazy:</strong>
            {% if history %}
                {% for item in history %}
                <div class="history-item">
                    <div><strong>Dotaz:</strong> {{ item.prompt }}</div>
                    <div><strong>Odpověď:</strong> {{ item.answer }}</div>
                </div>
                {% endfor %}
            {% else %}
                <p>Zatím žádná historie.</p>
            {% endif %}
        </div>

        <p class="small">Dostupné endpointy: /, /ping, /status, /ai</p>
    </div>
</body>
</html>
"""


def ask_ai(prompt: str) -> str:
    if not OPENAI_API_KEY:
        return "Chybí OPENAI_API_KEY."
    if not OPENAI_BASE_URL:
        return "Chybí OPENAI_BASE_URL."

    url = f"{OPENAI_BASE_URL.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Jsi finanční AI asistent. Odpovídej stručně, srozumitelně a česky. "
                    "Pomáhej s běžnými osobními financemi, rozpočtem, spořením a jednoduchými výpočty."
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

    if not response.ok:
        raise Exception(f"AI API error {response.status_code}: {response.text}")

    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


def save_to_redis(prompt: str, answer: str) -> None:
    item = json.dumps({"prompt": prompt, "answer": answer}, ensure_ascii=False)
    r.incr("requests_total")
    r.lpush("history", item)
    r.ltrim("history", 0, 4)


def get_history():
    items = r.lrange("history", 0, 4)
    return [json.loads(item) for item in items]


@app.route("/ping")
def ping():
    return "pong"


@app.route("/status")
def status():
    return jsonify({
        "status": "ok",
        "redis": REDIS_HOST,
        "model": OPENAI_MODEL,
        "openai_base_url": OPENAI_BASE_URL,
        "api_key_loaded": bool(OPENAI_API_KEY),
        "api_key_length": len(OPENAI_API_KEY) if OPENAI_API_KEY else 0,
        "requests_total": int(r.get("requests_total") or 0)
    })


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
        save_to_redis(prompt, answer)
        return jsonify({"prompt": prompt, "answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
                save_to_redis(prompt, answer)
            except Exception as e:
                error = str(e)

    history = get_history()
    total_requests = int(r.get("requests_total") or 0)

    return render_template_string(
        HTML,
        prompt=prompt,
        answer=answer,
        error=error,
        history=history,
        total_requests=total_requests
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8081)))
