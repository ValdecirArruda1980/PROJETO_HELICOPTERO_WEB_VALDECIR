import requests
from flask import Flask, render_template, jsonify


app = Flask(__name__)

OPENSKY_URL = 'https://opensky-network.org/api/states/all'
BR_BOUNDS = {'lamin': -33.75, 'lomin': -73.98, 'lamax': 5.27, 'lomax': -34.79}

@app.route('/api/telemetria')
def api_telemetria():
    try:
        r = requests.get(OPENSKY_URL, params=BR_BOUNDS, headers={'User-Agent': 'HelicopteroWeb/1.0'}, timeout=8)
        if r.status_code != 200: return jsonify([])
        states = r.json().get('states', []) or []
        frota = []
        for i, st in enumerate(states, 1):
            if not st[6] or not st[5] or st[8]: continue
            vel_kts = int((st[9] or 0) * 1.94384)
            prefixo = (st[1] or '').strip() or f'ICAO-e{st[0].upper()}'
            frota.append({
                'id': i, 'prefixo': prefixo, 'icao': st[0].upper(), 'fabricante': st[2],
                'latitude': st[6], 'longitude': st[5], 'altitude': int((st[7] or 0) * 3.28084),
                'velocidade': vel_kts, 'heading': int(st[10] or 0)
            })
        return jsonify(frota)
    except Exception:
        return jsonify([])

@app.route('/')
def index():
    with open('index.html', 'r', encoding='utf-8') as h:
        return h.read()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
