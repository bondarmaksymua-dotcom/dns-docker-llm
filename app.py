import os, json, redis, requests
from flask import Flask, request, render_template_string

app = Flask(__name__)
r = redis.Redis(host=os.getenv("REDIS_HOST", "cache"), decode_responses=True)

API = os.getenv("OPENAI_BASE_URL", "https://kurim.ithope.eu/v1")
KEY = os.getenv("OPENAI_API_KEY", "")
MODEL = os.getenv("OPENAI_MODEL", "gemma3:27b")

HTML = """
<h1>Finanční AI asistent</h1>

<form method="post">
<textarea name="p">{{p}}</textarea><br>
<button>Odeslat</button>
</form>

{% if a %}<p><b>Odpověď:</b> {{a}}</p>{% endif %}
{% if e %}<p style="color:red">{{e}}</p>{% endif %}

<p>Počet: {{t}}</p>

{% for i in h %}
<p>{{i.prompt}} → {{i.answer}}</p>
{% endfor %}
"""

def ai(p):
    r = requests.post(
        f"{API}/chat/completions",
        headers={"Authorization": f"Bearer {KEY}"},
        json={"model": MODEL, "messages":[{"role":"user","content":p}]}
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

@app.route("/", methods=["GET","POST"])
def home():
    p = a = e = ""
    if request.method == "POST":
        p = request.form.get("p","")
        if p:
            try:
                a = ai(p)
                r.incr("t")
                r.lpush("h", json.dumps({"prompt":p,"answer":a}))
                r.ltrim("h",0,4)
            except Exception as x:
                e = str(x)
        else:
            e = "Zadej dotaz"

    h = [json.loads(x) for x in r.lrange("h",0,4)]
    return render_template_string(HTML, p=p, a=a, e=e, h=h, t=int(r.get("t") or 0))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
