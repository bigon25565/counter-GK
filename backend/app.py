import os
import time
from flask import Flask, jsonify
from redis import Redis, RedisError
from dotenv import load_dotenv
from pathlib import Path
from flask import send_from_directory, request
from flask_cors import CORS

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

from redis_client import get_redis_client

r = get_redis_client()


HISTORY_KEY = 'counter:history'
MAX_HISTORY = 5

app = Flask(__name__, static_folder=str(BASE_DIR / 'static'), static_url_path='/')
CORS(app)

COUNTER_KEY = 'counter:value'

if r.get(COUNTER_KEY) is None:
    r.set(COUNTER_KEY, 0)

@app.route('/api/counter', methods=['GET'])
def get_counter():
    try:
        v = int(r.get(COUNTER_KEY) or 0)
        return jsonify({"value": v})
    except Exception as e:
        return jsonify({"error": "Redis error"}), 500

@app.route('/api/counter/increment', methods=['POST'])
def increment():
    try:
        v = r.incr(COUNTER_KEY)
        r.lpush(HISTORY_KEY, f"+1 → {v}")
        r.ltrim(HISTORY_KEY, 0, MAX_HISTORY - 1)
        return jsonify({"value": int(v)})
    except Exception as e:
        return jsonify({"error": "Redis error"}), 500

@app.route('/api/counter/decrement', methods=['POST'])
def decrement():
    try:
        current = int(r.get(COUNTER_KEY) or 0)
        if current <= 0:
            return jsonify({"error": "Counter cannot be negative"}), 400
        v = r.decr(COUNTER_KEY)
        return jsonify({"value": int(v)})
    except Exception as e:
        return jsonify({"error": "Redis error"}), 500

@app.route('/api/counter/reset', methods=['POST'])
def reset():
    try:
        r.set(COUNTER_KEY, 0)
        r.lpush(HISTORY_KEY, "reset → 0")
        r.ltrim(HISTORY_KEY, 0, MAX_HISTORY - 1)
        return jsonify({"value": 0})
    except Exception as e:
        return jsonify({"error": "Redis error"}), 500

@app.route('/api/counter/history', methods=['GET'])
def get_history():
    try:
        history = r.lrange(HISTORY_KEY, 0, -1)
        return jsonify({"history": history})
    except Exception as e:
        return jsonify({"error": "Redis error"}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_spa(path):
    static_dir = BASE_DIR / 'static'
    if path != "" and (static_dir / path).exists():
        return send_from_directory(str(static_dir), path)
    return send_from_directory(str(static_dir), 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)))
