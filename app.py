import requests
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

SDPW_LAT = -22.710556
SDPW_LNG = -47.619444

@app.route('/api/telemetria')
def api_telemetria():
    try:
        # API do OpenSky sem filtros de coordenadas = Mundo Inteiro
        url = 'https://opensky-network.org/api/states/all'
        response = requests.get(url, timeout=8)
        data = response.json()
        
        aeronaves_reais = []
        if data and 'states' in data and data['states']:
            # Pega uma amostra global de ate 400 aeronaves ativas no ar pelo mundo
            ativos = [s for s in data['states'] if s[5] is not None and s[6] is not None and s[8] == False]
            for idx, s in enumerate(ativos[:400]):
                callsign = s[1].strip() if s[1] else f'ICAO-{s[0]}'
                alt_ft = int((s[7] or 0) * 3.28084)
                vel_kts = int((s[9] or 0) * 1.94384)
                
                aeronaves_reais.append({
                    "id": idx + 1,
                    "prefixo": callsign,
                    "icao": s[0],
                    "modelo": "Aeronave Comercial / Real",
                    "fabricante": s[2] or "Global",
                    "tipo_operacao": "Tráfego Global Ao Vivo",
                    "cor_operacao": "#38bdf8",
                    "pax_atual": "Global",
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
                    "destino": {"nome": "Destino Internacional", "lat": s[6], "lng": s[5]}
                })
        return jsonify(aeronaves_reais)
    except Exception as e:
        return jsonify([])

INDEX_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Radar Global Ao Vivo - Mundo Inteiro</title>
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
        <h1>🌍 Radar Global Ao Vivo - Tráfego Aéreo do Mundo Inteiro</h1>
    </header>
    <div class="main-container">
        <div id="map"></div>
        <aside class="sidebar">
            <div class="panel">
                <div class="panel-title">📋 Ficha de Voo Global Selecionado</div>
                <div class="plano-voo">
                    <h3 id="plano-titulo" style="color:#38bdf8; margin-bottom:5px;">Selecione uma aeronave</h3>
                    <div class="plano-item"><span>Status:</span><strong id="p-operacao">Global / Ao Vivo</strong></div>
                    <div class="plano-item"><span>Matrícula / Callsign:</span><strong id="p-modelo">-</strong></div>
                    <div class="plano-item"><span>Altitude / Velocidade:</span><strong id="p-alt-vel">-</strong></div>
                </div>
            </div>
            <div class="panel" style="flex:1; display:flex; flex-direction:column;">
                <div class="panel-title">✈️ Voos Mundiais em Tempo Real</div>
                <div class="tabela-container">
                    <table>
                        <thead>
                            <tr><th>CallSign</th><th>Alt (ft)</th><th>Vel (km/h)</th></tr>
                        </thead>
                        <tbody id="tabela-frota"></tbody>
                    </table>
                </div>
            </div>
        </aside>
    </div>
    <script>
        const map = L.map('map').setView([20.0, 0.0], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

        let marcadores = {};
        let selecaoAtualId = null;

        function selecionarAeronave(id, aeronaves) {
            const aero = aeronaves.find(a => a.id === id);
            if (!aero) return;
            const speedKmh = Math.round(aero.velocidade * 1.852);
            document.getElementById('plano-titulo').innerText = '✈️ ' + aero.prefixo;
            document.getElementById('p-modelo').innerText = aero.prefixo + ' (ICAO: ' + aero.icao + ')';
            document.getElementById('p-alt-vel').innerText = aero.altitude + ' ft | ' + speedKmh + ' km/h';
            selecaoAtualId = aero.id;
        }

        function criarIconeGlobal(prefixo, corHex, heading) {
            const svgIcon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="26" height="26" style="transform: rotate(' + heading + 'deg);">' +
                '<path fill="' + corHex + '" d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>' +
            '</svg>';
            return L.divIcon({
                html: '<div style="text-align:center;">' + svgIcon + '<div style="background-color:rgba(15,23,42,0.85); color:' + corHex + '; font-size:7px; font-weight:bold; border-radius:3px; padding:1px 2px; margin-top:-4px; white-space:nowrap; border:1px solid ' + corHex + ';">' + prefixo + '</div></div>',
                className: '', iconSize: [32, 32], iconAnchor: [16, 16]
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
                    tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; color:#94a3b8;">Carregando tráfego mundial...</td></tr>';
                    return;
                }

                aeronaves.forEach(aero => {
                    const speedKmh = Math.round(aero.velocidade * 1.852);
                    const tr = document.createElement('tr');
                    tr.onclick = (e) => {
                        e.stopPropagation();
                        map.setView([aero.latitude, aero.longitude], 6);
                        selecionarAeronave(aero.id, aeronaves);
                    };
                    tr.innerHTML = '<td style="font-weight:bold; color:' + aero.cor_operacao + ';">' + aero.prefixo + '</td><td>' + aero.altitude + ' ft</td><td>' + speedKmh + ' km/h</td>';
                    tbody.appendChild(tr);

                    const iconCustom = criarIconeGlobal(aero.prefixo, aero.cor_operacao, aero.heading);
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
        setInterval(carregarTelemetria, 15000);
    </script>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
