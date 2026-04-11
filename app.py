from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

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
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.5;
        }
        h1 {
            margin-bottom: 10px;
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
        .label {
            font-weight: bold;
            margin-bottom: 8px;
        }
        .small {
            color: #555;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>Finanční AI asistent</h1>
    <p>Zadej finanční dotaz a aplikace vrátí odpověď.</p>

    <form method="post" action="/">
        <textarea name="prompt" placeholder="Např. Mám 500 Kč a koupím si věc za 320 Kč. Kolik mi zbyde?">{{ prompt }}</textarea>
        <br>
        <button type="submit">Odeslat</button>
    </form>

    {% if answer %}
    <div class="box">
        <div class="label">Odpověď:</div>
        <div>{{ answer }}</div>
    </div>
    {% endif %}

    <div class="small">
        Dostupné endpointy: /ping, /status, /ai
    </div>
</body>
</html>
"""

def process_prompt(prompt):
    text = prompt.lower()

    if "500" in text and "320" in text:
        return "Zbyde ti 180 Kč."

    if "1000" in text and "250" in text:
        return "Zbyde ti 750 Kč."

    return f"Zpracováno: {prompt}"

@app.route("/", methods=["GET", "POST"])
def home():
    prompt = ""
    answer = ""

    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()
        if prompt:
            answer = process_prompt(prompt)

    return render_template_string(HTML, prompt=prompt, answer=answer)

@app.route("/ping")
def ping():
    return "pong"

@app.route("/status")
def status():
    return jsonify({
        "redis": "cache",
        "status": "ok"
    })

@app.route("/ai", methods=["POST"])
def ai():
    data = request.get_json(silent=True)

    if not data or "prompt" not in data:
        return jsonify({"error": "missing prompt"}), 400

    prompt = str(data["prompt"]).strip()
    answer = process_prompt(prompt)

    return jsonify({
        "answer": answer,
        "prompt": prompt
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
