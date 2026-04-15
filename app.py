import json
import os

import redis
import requests
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://kurim.ithope.eu/v1").rstrip("/")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gemma3:27b")
REDIS_HOST = os.environ.get("REDIS_HOST", "cache")

r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

HTML = """
<!doctype html>
<html lang="cs">
<head>
    <meta charset="utf-8">
    <title>Finanční AI asistent</title>
</head>
<body style="font-family:Arial; max-width:800px; margin:40px auto;">
    <h1>Finanční AI asistent</h1>
    <p>Zadej finanční dotaz:</p>

    <form method="post">
        <textarea name="prompt" rows="5" style="width:100%;">{{ prompt }}</textarea><br><br>
        <button type="submit">Odeslat</button>
    </form>

    {% if answer %}
        <h3>Odpověď:</h3>
        <p>{{ answer }}</p>
    {% endif %}

    {% if error %}
        <h3>Chyba:</h3>
        <p style="color:red;">{{ error }}</p>
    {% endif %}

    <h3>Počet dotazů: {{ total_requests }}</h3>

    <h3>Poslední dotazy:</h3>
    {% if history %}
        {% for item in history %}
            <p><b>Dotaz:</b> {{ item.prompt }}<br>
            <b>Odpověď:</b> {{ item.answer }}</p>
            <hr>
        {% endfor %}
    {% else %}
        <p>Zatím žádná historie.</p>
    {% endif %}
</body>
</html>
"""

def ask_ai(prompt: str) -> str:
    url = f"{OPENAI_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": "Jsi finanční AI asistent. Odpovídej stručně a česky."},
            {"role": "user", "content": prompt},
        ],
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()

def save_history(prompt: str, answer: str) -> None:
    item = json.dumps({"prompt": prompt, "answer": answer}, ensure_ascii=False)
    r.incr("requests_total")
    r.lpush("history", item)
    r.ltrim("history", 0, 4)

def get_history():
    return [json.loads(item) for item in r.lrange("history", 0, 4)]

@app.route("/ping")
def ping():
    return "pong"

@app.route("/status")
def status():
    return jsonify({
        "status": "ok",
        "redis": "cache",
        "model": OPENAI_MODEL,
        "api_key_loaded": bool(OPENAI_API_KEY),
        "requests_total": int(r.get("requests_total") or 0)
    })

@app.route("/ai", methods=["POST"])
def ai():
    data = request.get_json(silent=True)
    if not data or "prompt" not in data:
        return jsonify({"error": "missing prompt"}), 400

    prompt = data["prompt"].strip()
    answer = ask_ai(prompt)
    save_history(prompt, answer)
    return jsonify({"prompt": prompt, "answer": answer})

@app.route("/", methods=["GET", "POST"])
def home():
    prompt = ""
    answer = ""
    error = ""

    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()
        if prompt:
            try:
                answer = ask_ai(prompt)
                save_history(prompt, answer)
            except Exception as e:
                error = str(e)
        else:
            error = "Zadej dotaz."

    return render_template_string(
        HTML,
        prompt=prompt,
        answer=answer,
        error=error,
        history=get_history(),
        total_requests=int(r.get("requests_total") or 0)
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8081)))

