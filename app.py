import requests
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

SDPW_LAT = -22.710556
SDPW_LNG = -47.619444

@app.route('/api/telemetria')
def api_telemetria():
    try:
        url = 'https://opensky-network.org/api/states/all?lamin=-24.5&lamax=-21.0&lomin=-49.5&lomax=-45.0'
        response = requests.get(url, timeout=5)
        data = response.json()
        
        aeronaves_reais = []
        if data and 'states' in data and data['states']:
            for idx, s in enumerate(data['states']):
                if s[5] is not None and s[6] is not None and s[8] == False:
                    callsign = s[1].strip() if s[1] else f'ICAO-{s[0]}'
                    alt_ft = int((s[7] or 0) * 3.28084)
                    vel_kts = int((s[9] or 0) * 1.94384)
                    
                    is_helicoptero = False
                    if vel_kts > 0 and vel_kts < 170 and alt_ft < 10000:
                        if callsign.startswith('PP-') or callsign.startswith('PR-') or callsign.startswith('PT-'):
                            is_helicoptero = True

                    if is_helicoptero:
                        aeronaves_reais.append({
                            "id": len(aeronaves_reais) + 1,
                            "prefixo": callsign,
                            "icao": s[0],
                            "modelo": "Helicóptero (Transponder Real)",
                            "fabricante": s[2] or "Brasil / Exterior",
                            "tipo_operacao": "Asa Rotativa Ao Vivo",
                            "cor_operacao": "#f59e0b",
                            "pax_atual": "Reais",
                            "pax_max": "- ",
                            "peso_atual": "- ",
                            "peso_max": "- ",
                            "combustivel": "- ",
                            "autonomia": "Tempo Real",
                            "latitude": s[6],
                            "longitude": s[5],
                            "altitude": alt_ft,
                            "velocidade": vel_kts,
                            "heading": int(s[10] or 0),
                            "origem": {"nome": "Aeroporto de Piracicaba (SDPW)", "lat": SDPW_LAT, "lng": SDPW_LNG},
                            "destino": {"nome": "Espaço Aéreo Regional", "lat": s[6], "lng": s[5]}
                        })
        return jsonify(aeronaves_reais)
    except Exception as e:
        return jsonify([])

INDEX_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Radar de Helicópteros Reais - Piracicaba</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }
        body { display: flex; flex-direction: column; height: 100vh; background-color: #0f172a; color: #f8fafc; }
        header { background-color: #1e293b; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #334155; }
        h1 { font-size: 1.2rem; color: #38bdf8; }
        .main-container { display: flex; flex: 1; overflow: hidden; }
        #map { flex: 1; height: 100%; }
        .sidebar { width: 380px; background-color: #0f172a; border-left: 2px solid #334155; display: flex; flex-direction: column; padding: 15px; gap: 15px; overflow-y: auto; }
        .panel { background-color: #1e293b; border-radius: 8px; padding: 15px; border: 1px solid #334155; }
        .panel-title { font-size: 0.95rem; font-weight: bold; color: #94a3b8; margin-bottom: 12px; border-bottom: 1px solid #334155; padding-bottom: 6px; }
        .plano-voo { display: flex; flex-direction: column; gap: 8px; font-size: 0.85rem; }
        .plano-item { display: flex; justify-content: space-between; border-bottom: 1px dashed #334155; padding-bottom: 4px; }
        .plano-item span { color: #94a3b8; }
        .plano-item strong { color: #38bdf8; }
        .tabela-container { flex: 1; overflow-y: auto; max-height: 400px; }
        table { width: 100%; border-collapse: collapse; font-size: 0.8rem; text-align: left; }
        th { background-color: #1e293b; color: #94a3b8; padding: 8px; position: sticky; top: 0; }
        td { padding: 8px; border-bottom: 1px solid #1e293b; }
        tr:hover { background-color: #1e293b; cursor: pointer; }
    </style>
</head>
<body>
    <header>
        <h1>🚁 Radar de Helicópteros Reais Ao Vivo (Piracicaba / SP)</h1>
    </header>
    <div class="main-container">
        <div id="map"></div>
        <aside class="sidebar">
            <div class="panel">
                <div class="panel-title">📋 Ficha do Helicóptero Selecionado</div>
                <div class="plano-voo">
                    <h3 id="plano-titulo" style="color:#38bdf8; margin-bottom:5px;">Selecione uma aeronave</h3>
                    <div class="plano-item"><span>Tipo:</span><strong id="p-operacao">Helicóptero Real</strong></div>
                    <div class="plano-item"><span>Matrícula:</span><strong id="p-modelo">-</strong></div>
                    <div class="plano-item"><span>Altitude / Velocidade:</span><strong id="p-alt-vel">-</strong></div>
                </div>
            </div>
            <div class="panel" style="flex:1; display:flex; flex-direction:column;">
                <div class="panel-title">🚁 Helicópteros no Céu (Tempo Real)</div>
                <div class="tabela-container">
                    <table>
                        <thead>
                            <tr><th>Matrícula</th><th>Alt (ft)</th><th>Vel (km/h)</th></tr>
                        </thead>
                        <tbody id="tabela-frota"></tbody>
                    </table>
                </div>
            </div>
        </aside>
    </div>
    <script>
        const map = L.map('map').setView([-22.710556, -47.619444], 9);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

        L.circleMarker([-22.710556, -47.619444], { radius: 7, color: '#10b981', fillColor: '#10b981', fillOpacity: 1 })
          .addTo(map)
          .bindPopup('🛫 <b>Aeroporto de Piracicaba (SDPW)</b>');

        let marcadores = {};
        let selecaoAtualId = null;

        function selecionarAeronave(id, aeronaves) {
            const aero = aeronaves.find(a => a.id === id);
            if (!aero) return;
            const speedKmh = Math.round(aero.velocidade * 1.852);
            document.getElementById('plano-titulo').innerText = '🚁 ' + aero.prefixo;
            document.getElementById('p-modelo').innerText = aero.prefixo + ' (ICAO: ' + aero.icao + ')';
            document.getElementById('p-alt-vel').innerText = aero.altitude + ' ft | ' + speedKmh + ' km/h';
            selecaoAtualId = aero.id;
        }

        function criarIconeHelicoptero(prefixo, corHex, heading) {
            const svgIcon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="30" height="30" style="transform: rotate(' + heading + 'deg);">' +
                '<line x1="2" y1="12" x2="22" y2="12" stroke="' + corHex + '" stroke-width="2.5" stroke-linecap="round"/>' +
                '<path fill="' + corHex + '" stroke="#ffffff" stroke-width="1.2" d="M12,4 C10,4 9,6 9,10 L9,14 C9,16 10,17 11,18 L11,21 L13,21 L13,18 C14,17 15,16 15,14 L15,10 C15,6 14,4 12,4 Z"/>' +
                '<line x1="10" y1="21" x2="14" y2="21" stroke="' + corHex + '" stroke-width="2"/>' +
            '</svg>';
            return L.divIcon({
                html: '<div style="text-align:center;">' + svgIcon + '<div style="background-color:rgba(15,23,42,0.85); color:' + corHex + '; font-size:9px; font-weight:bold; border-radius:3px; padding:1px 3px; margin-top:-4px; white-space:nowrap; border:1px solid ' + corHex + ';">' + prefixo + '</div></div>',
                className: '', iconSize: [40, 40], iconAnchor: [20, 20]
            });
        }

        async function carregarTelemetria() {
            try {
                const res = await fetch('/api/telemetria');
                const aeronaves = await res.json();
                const tbody = document.getElementById('tabela-frota');
                tbody.innerHTML = '';

                let idsAtuais = aeronaves.map(a => a.id);
                for (let id in marcadores) {
                    if (!idsAtuais.includes(parseInt(id))) {
                        map.removeLayer(marcadores[id]);
                        delete marcadores[id];
                    }
                }

                if (aeronaves.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; color:#94a3b8;">Nenhum helicóptero com transponder público visível no momento.</td></tr>';
                    return;
                }

                aeronaves.forEach(aero => {
                    const speedKmh = Math.round(aero.velocidade * 1.852);
                    const tr = document.createElement('tr');
                    tr.onclick = (e) => {
                        e.stopPropagation();
                        map.setView([aero.latitude, aero.longitude], 11);
                        selecionarAeronave(aero.id, aeronaves);
                    };
                    tr.innerHTML = '<td style="font-weight:bold; color:' + aero.cor_operacao + ';">' + aero.prefixo + '</td><td>' + aero.altitude + ' ft</td><td>' + speedKmh + ' km/h</td>';
                    tbody.appendChild(tr);

                    const iconCustom = criarIconeHelicoptero(aero.prefixo, aero.cor_operacao, aero.heading);
                    if (marcadores[aero.id]) {
                        marcadores[aero.id].setLatLng([aero.latitude, aero.longitude]);
                        marcadores[aero.id].setIcon(iconCustom);
                    } else {
                        const m = L.marker([aero.latitude, aero.longitude], { icon: iconCustom }).addTo(map);
                        m.on('click', (e) => { L.DomEvent.stopPropagation(e); selecionarAeronave(aero.id, aeronaves); });
                        marcadores[aero.id] = m;
                    }
                });
            } catch (err) {}
        }

        carregarTelemetria();
        setInterval(carregarTelemetria, 12000);
    </script>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
