import json
import os

import redis
import requests
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

API_KEY = os.environ.get("OPENAI_API_KEY", "")
BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://kurim.ithope.eu/v1").rstrip("/")
MODEL = os.environ.get("OPENAI_MODEL", "gemma3:27b")
r = redis.Redis(host=os.environ.get("REDIS_HOST", "cache"), port=6379, decode_responses=True)

HTML = """
<h1>Finanční AI asistent</h1>
<form method="post">
  <textarea name="prompt" rows="5" style="width:100%%;">{{ prompt }}</textarea><br><br>
  <button type="submit">Odeslat</button>
</form>
{% if answer %}<p><b>Odpověď:</b> {{ answer }}</p>{% endif %}
{% if error %}<p style="color:red;"><b>Chyba:</b> {{ error }}</p>{% endif %}
<p><b>Počet dotazů:</b> {{ total }}</p>
<h3>Historie</h3>
{% for item in history %}
  <p><b>Dotaz:</b> {{ item.prompt }}<br><b>Odpověď:</b> {{ item.answer }}</p><hr>
{% else %}
  <p>Zatím žádná historie.</p>
{% endfor %}
"""

def ask_ai(prompt: str) -> str:
    res = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "Jsi finanční AI asistent. Odpovídej stručně a česky."},
                {"role": "user", "content": prompt},
            ],
        },
        timeout=60,
    )
    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"].strip()

def save(prompt: str, answer: str) -> None:
    r.incr("requests_total")
    r.lpush("history", json.dumps({"prompt": prompt, "answer": answer}, ensure_ascii=False))
    r.ltrim("history", 0, 4)

def history():
    return [json.loads(x) for x in r.lrange("history", 0, 4)]

@app.route("/ping")
def ping():
    return "pong"

@app.route("/status")
def status():
    return jsonify({
        "status": "ok",
        "redis": "cache",
        "model": MODEL,
        "api_key_loaded": bool(API_KEY),
        "requests_total": int(r.get("requests_total") or 0),
    })

@app.route("/ai", methods=["POST"])
def ai():
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "missing prompt"}), 400
    answer = ask_ai(prompt)
    save(prompt, answer)
    return jsonify({"prompt": prompt, "answer": answer})

@app.route("/", methods=["GET", "POST"])
def home():
    prompt = answer = error = ""
    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()
        if not prompt:
            error = "Zadej dotaz."
        else:
            try:
                answer = ask_ai(prompt)
                save(prompt, answer)
            except Exception as e:
                error = str(e)
    return render_template_string(
        HTML,
        prompt=prompt,
        answer=answer,
        error=error,
        history=history(),
        total=int(r.get("requests_total") or 0),
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8081)))
