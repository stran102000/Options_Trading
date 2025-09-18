"""Flask API server serving the Options Trading Analysis frontend and data API."""
from __future__ import annotations
import os
from pathlib import Path
from flask import Flask, send_from_directory, jsonify, request
from backend.analysis import analyze

BASE_DIR = Path(__file__).parent
FRONTEND_DIR = BASE_DIR / 'frontend'

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path='')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    payload = request.get_json(silent=True) or {}
    tickers_raw = payload.get('tickers') or ''
    expiration = payload.get('expiration') or None
    if isinstance(tickers_raw, str):
        tickers = [t.strip() for t in tickers_raw.split(',') if t.strip()]
    else:
        tickers = tickers_raw if isinstance(tickers_raw, list) else []
    if not tickers:
        return jsonify({'error': 'No tickers provided', 'results': []}), 400
    result = analyze(tickers, expiration)
    return jsonify(result)

# Static file fallback (CSS/JS)
@app.route('/<path:path>')
def static_proxy(path):
    file_path = FRONTEND_DIR / path
    if file_path.is_file():
        return send_from_directory(app.static_folder, path)
    return jsonify({'error': 'Not found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
