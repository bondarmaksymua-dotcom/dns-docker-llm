import os
from flask import Flask, jsonify, request
import redis

app = Flask(__name__)

r = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=6379)

@app.route("/ping")
def ping():
    return "pong"

@app.route("/status")
def status():
    try:
        r.ping()
        return jsonify({"redis": "cache", "status": "ok"})
    except Exception:
        return jsonify({"redis": "cache", "status": "error"})

@app.route("/ai", methods=["POST"])
def ai():
    data = request.get_json()

    if not data or "prompt" not in data:
        return jsonify({"error": "missing prompt"}), 400

    prompt = data["prompt"]

    vysledek = f"Processed: {prompt}"

    r.incr("requests")

    return jsonify({
        "prompt": prompt,
        "answer": vysledek,
        "requests_total": int(r.get("requests") or 0)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8081)))
