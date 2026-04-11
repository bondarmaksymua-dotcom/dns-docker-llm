from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>Finanční AI asistent</h1>
    <p>Aplikace běží správně.</p>
    <p>Dostupné endpointy:</p>
    <ul>
      <li>/ping</li>
      <li>/status</li>
      <li>/ai</li>
    </ul>
    """

@app.route("/ping")
def ping():
    return "OK"

@app.route("/status")
def status():
    return jsonify({
        "redis": "cache",
        "status": "ok"
    })

@app.route("/ai", methods=["POST"])
def ai():
    data = request.get_json()
    prompt = data.get("prompt", "")

    # jednoduchá "AI" odpověď
    answer = f"Zpracováno: {prompt}"

    return jsonify({
        "answer": answer,
        "prompt": prompt
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
