"""
app.py — Lightweight Flask web server.
Keeps the bot alive on platforms like Render, Railway, or Heroku
that require an open HTTP port.
"""
import os
import threading
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ok", "bot": "Saini DRM Bot", "alive": True})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


def keep_alive():
    """Start Flask in a background thread so bot can run in main thread."""
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()
