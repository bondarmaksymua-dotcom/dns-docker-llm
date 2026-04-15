import os, json, redis, requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

API_KEY = os.getenv("OPENAI_API_KEY", "")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://kurim.ithope.eu/v1").rstrip("/")
MODEL = os.getenv("OPENAI_MODEL", "gemma3:27b")

r = redis.Redis(host=os.getenv("REDIS_HOST", "cache"), port=6379, decode_responses=True)

HTML = """
<h1>Finanční AI asistent</h1>

<form method="post">
  <textarea name="prompt" rows="4" cols="50">{{prompt}}</textarea><br>
  <button>Odeslat</button>
</form>

{% if answer %}
<p><b>Odpověď:</b> {{answer}}</p>
{% endif %}

{% if error %}
<p style="color:red;"><b>Chyba:</b> {{error}}</p>
{% endif %}

<p><b>Počet dotazů:</b> {{total}}</p>

<h3>Historie:</h3>
{% for i in history %}
<p><b>Dotaz:</b> {{i.prompt}}<br>
<b>Odpověď:</b> {{i.answer}}</p>
{% else %}
<p>Žádná historie</p>
{% endfor %}
"""

def ask_ai(prompt):
    res = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "Jsi finanční AI asistent. Odpovídej česky."},
                {"role": "user", "content": prompt}
            ]
        }
    )
    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"]

def save(prompt, answer):
    r.incr("requests_total")
    r.lpush("history", json.dumps({"prompt": prompt, "answer": answer}))
    r.ltrim("history", 0, 4)

def history():
    return [json.loads(x) for x in r.lrange("history", 0, 4)]

@app.route("/", methods=["GET", "POST"])
def home():
    prompt = answer = error = ""
    if request.method == "POST":
        prompt = request.form.get("prompt", "")
        if prompt:
            try:
                answer = ask_ai(prompt)
                save(prompt, answer)
            except Exception as e:
                error = str(e)
        else:
            error = "Zadej dotaz."

    return render_template_string(
        HTML,
        prompt=prompt,
        answer=answer,
        error=error,
        history=history(),
        total=int(r.get("requests_total") or 0)
    )

@app.route("/status")
def status():
    return jsonify({"status": "ok"})

@app.route("/ping")
def ping():
    return "pong"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
