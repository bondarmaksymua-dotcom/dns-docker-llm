import os, json, redis, requests
from flask import Flask, request, render_template_string

app = Flask(__name__)
db = redis.Redis(host=os.getenv("REDIS_HOST", "cache"), decode_responses=True)

API = os.getenv("OPENAI_BASE_URL", "https://kurim.ithope.eu/v1")
KEY = os.getenv("OPENAI_API_KEY", "")
MODEL = os.getenv("OPENAI_MODEL", "gemma3:27b")

HTML = """
<!doctype html>
<html lang="cs" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Finanční AI asistent</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
  <style>
    body { background: linear-gradient(135deg,#0f172a,#1e293b); min-height: 100vh; }
    main { max-width: 820px; margin: 40px auto; }
    .box { background: rgba(15,23,42,.75); border-radius: 20px; padding: 24px; }
    textarea { min-height: 120px; }
    .item { padding: 12px; border: 1px solid #334155; border-radius: 14px; margin-top: 12px; }
    .muted { color: #94a3b8; }
  </style>
</head>
<body>
  <main class="container">
    <section class="box">
      <h1>Finanční AI asistent</h1>
      <p class="muted">Zeptej se na rozpočet, spoření nebo investice.</p>

      <form method="post">
        <textarea name="p" placeholder="Napiš dotaz...">{{ p }}</textarea>
        <button type="submit">Odeslat</button>
      </form>

      {% if e %}<article><strong>Chyba:</strong> {{ e }}</article>{% endif %}
      {% if a %}<article><strong>Odpověď:</strong><br>{{ a }}</article>{% endif %}

      <p><strong>Počet dotazů:</strong> {{ t }}</p>

      {% for i in h %}
        <div class="item">
          <strong>{{ i.prompt }}</strong><br>
          {{ i.answer }}
        </div>
      {% endfor %}
    </section>
  </main>
</body>
</html>
"""

def ai(prompt):
    res = requests.post(
        f"{API}/chat/completions",
        headers={"Authorization": f"Bearer {KEY}"},
        json={"model": MODEL, "messages": [{"role": "user", "content": prompt}]},
        timeout=60
    )
    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"]

@app.route("/", methods=["GET", "POST"])
def home():
    p = a = e = ""
    if request.method == "POST":
        p = request.form.get("p", "").strip()
        if not p:
            e = "Zadej dotaz."
        else:
            try:
                a = ai(p)
                db.incr("t")
                db.lpush("h", json.dumps({"prompt": p, "answer": a}))
                db.ltrim("h", 0, 4)
            except Exception as x:
                e = str(x)

    h = [json.loads(x) for x in db.lrange("h", 0, 4)]
    t = int(db.get("t") or 0)
    return render_template_string(HTML, p=p, a=a, e=e, h=h, t=t)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
