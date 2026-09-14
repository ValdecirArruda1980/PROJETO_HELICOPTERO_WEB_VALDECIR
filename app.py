import math
import random
import time
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

BASES_E_ROTAS = [
    {"origem": {"nome": "Aeroporto de Piracicaba (SDPW)", "lat": -22.7610, "lng": -47.6530}, "destino": {"nome": "Intl Viracopos Campinas (SBKP)", "lat": -23.0074, "lng": -47.1345}},
    {"origem": {"nome": "Heliponto Faria Lima SP", "lat": -23.5780, "lng": -46.6900}, "destino": {"nome": "Aeroporto de Jundiaí (SDJD)", "lat": -23.1817, "lng": -46.9422}},
    {"origem": {"nome": "Campo de Marte SP (SBMT)", "lat": -23.5069, "lng": -46.6340}, "destino": {"nome": "Aeroporto de Amarais Campinas (SDAM)", "lat": -22.8586, "lng": -47.0700}},
    {"origem": {"nome": "Heliponto Alphaville Barueri", "lat": -23.4980, "lng": -46.8500}, "destino": {"nome": "Aeroporto de Sorocaba (SDCO)", "lat": -23.4797, "lng": -47.4857}},
    {"origem": {"nome": "Aeroporto de Bauru (SBBX)", "lat": -22.3444, "lng": -49.0538}, "destino": {"nome": "Aeroporto de Ribeirão Preto (SBRP)", "lat": -21.1364, "lng": -47.7725}},
    {"origem": {"nome": "Heliponto Rebouças SP", "lat": -23.5650, "lng": -46.6750}, "destino": {"nome": "Aeroporto de Santos (SBST)", "lat": -23.9275, "lng": -46.2842}},
    {"origem": {"nome": "Plataforma Offshore Bacia de Santos", "lat": -25.2000, "lng": -45.1000}, "destino": {"nome": "Aerop. Jacarepaguá RJ (SBJR)", "lat": -22.9869, "lng": -43.3703}},
    {"origem": {"nome": "Aerop. Bacacheri Curitiba (SBBI)", "lat": -25.4050, "lng": -49.2320}, "destino": {"nome": "Aerop. Hercílio Luz FNC (SBFL)", "lat": -27.6703, "lng": -48.5525}},
    {"origem": {"nome": "Aeroporto de Brasília (SBBR)", "lat": -15.8697, "lng": -47.9172}, "destino": {"nome": "Aeroporto de Goiânia (SBGO)", "lat": -16.6322, "lng": -49.2206}}
]

MODELOS_HELICOPTEROS = [
    {"modelo": "Airbus H145 (EC145)", "fabricante": "Airbus Helicopters", "pax_max": 8, "peso_max": 3800},
    {"modelo": "AgustaWestland AW109 GrandNew", "fabricante": "Leonardo Helicopters", "pax_max": 6, "peso_max": 3175},
    {"modelo": "Bell 429 GlobalRanger", "fabricante": "Bell Helicopter", "pax_max": 7, "peso_max": 3175},
    {"modelo": "Sikorsky S-76C++", "fabricante": "Sikorsky Aircraft", "pax_max": 12, "peso_max": 5306},
    {"modelo": "Robinson R44 Raven II", "fabricante": "Robinson Helicopter", "pax_max": 3, "peso_max": 1134},
    {"modelo": "Airbus H125 Esquilo (HB350)", "fabricante": "Helibras / Airbus", "pax_max": 5, "peso_max": 2250},
    {"modelo": "EC135 T3", "fabricante": "Airbus Helicopters", "pax_max": 6, "peso_max": 2980}
]

TIPOS_OPERACAO = [
    {"tipo": "Executivo", "cor": "#3b82f6"},
    {"tipo": "Policial", "cor": "#ef4444"},
    {"tipo": "Particular", "cor": "#10b981"},
    {"tipo": "Offshore", "cor": "#f59e0b"}
]

frota_simulada = []

def calcular_bearing(lat1, lon1, lat2, lon2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)
    y = math.sin(delta_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)
    return int((math.degrees(math.atan2(y, x)) + 360) % 360)

def inicializar_frota():
    global frota_simulada
    frota_simulada = []
    prefixos_usados = set()

    for i in range(1, 501):
        while True:
            p = f"PP-{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))}{random.randint(10, 99)}"
            if p not in prefixos_usados:
                prefixos_usados.add(p)
                prefixo = p
                break

        rota = random.choice(BASES_E_ROTAS)
        mod = random.choice(MODELOS_HELICOPTEROS)
        op = random.choice(TIPOS_OPERACAO)

        lat_base = rota["origem"]["lat"]
        lng_base = rota["origem"]["lng"]
        lat_dest = rota["destino"]["lat"]
        lng_dest = rota["destino"]["lng"]

        t = random.uniform(0.05, 0.95)
        offset_lat = random.uniform(-0.12, 0.12)
        offset_lng = random.uniform(-0.12, 0.12)

        lat_init = lat_base + t * (lat_dest - lat_base) + offset_lat
        lng_init = lng_base + t * (lng_dest - lng_base) + offset_lng

        heading = calcular_bearing(lat_init, lng_init, lat_dest, lng_dest)
        pax_atual = random.randint(1, mod["pax_max"])
        peso_atual = int(mod["peso_max"] * random.uniform(0.65, 0.92))
        combustivel = random.randint(25, 98)

        frota_simulada.append({
            "id": i,
            "prefixo": prefixo,
            "icao": f"E4{random.randint(1000, 9999):04X}",
            "modelo": mod["modelo"],
            "fabricante": mod["fabricante"],
            "tipo_operacao": op["tipo"],
            "cor_operacao": op["cor"],
            "pax_atual": pax_atual,
            "pax_max": mod["pax_max"],
            "peso_atual": peso_atual,
            "peso_max": mod["peso_max"],
            "combustivel": combustivel,
            "autonomia": f"0{int(combustivel * 0.05)}h {random.randint(10, 59)}m",
            "latitude": lat_init,
            "longitude": lng_init,
            "altitude": random.randint(1200, 4500),
            "velocidade": random.randint(95, 160),
            "heading": heading,
            "origem": rota["origem"],
            "destino": rota["destino"]
        })

inicializar_frota()

def atualizar_posicoes():
    for a in frota_simulada:
        rad = math.radians(a["heading"])
        dist = (a["velocidade"] * 1.852 / 3600) * 3
        delta_lat = (dist / 111.0) * math.cos(rad)
        delta_lng = (dist / (111.0 * math.cos(math.radians(a["latitude"])))) * math.sin(rad)

        a["latitude"] += delta_lat
        a["longitude"] += delta_lng

        dist_dest = math.hypot(a["latitude"] - a["destino"]["lat"], a["longitude"] - a["destino"]["lng"])
        if dist_dest < 0.05:
            a["origem"], a["destino"] = a["destino"], a["origem"]
            a["heading"] = calcular_bearing(a["latitude"], a["longitude"], a["destino"]["lat"], a["destino"]["lng"])

@app.route('/api/telemetria')
def api_telemetria():
    atualizar_posicoes()
    return jsonify(frota_simulada)

INDEX_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Helicóptero Web Valdecir - Telemetria (500 Helicópteros)</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }
        body { display: flex; flex-direction: column; height: 100vh; background-color: #0f172a; color: #f8fafc; }
        header { background-color: #1e293b; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #334155; }
        h1 { font-size: 1.2rem; color: #38bdf8; display: flex; align-items: center; gap: 10px; }
        .badge-live { background-color: #059669; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; }
        .main-container { display: flex; flex: 1; overflow: hidden; }
        #map { flex: 1; height: 100%; background-color: #1e293b; }
        .sidebar { width: 380px; background-color: #0f172a; border-left: 2px solid #334155; display: flex; flex-direction: column; padding: 15px; gap: 15px; overflow-y: auto; }
        .panel { background-color: #1e293b; border-radius: 8px; padding: 15px; border: 1px solid #334155; }
        .panel-title { font-size: 0.95rem; font-weight: bold; color: #94a3b8; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #334155; padding-bottom: 6px; }
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
        <h1>🚁 Helicóptero Web Valdecir - Telemetria (500 Helicópteros)</h1>
        <span class="badge-live">500 Helicópteros Ao Vivo</span>
    </header>
    <div class="main-container">
        <div id="map"></div>
        <aside class="sidebar">
            <div class="panel">
                <div class="panel-title">📋 Ficha Completa de Voo Selecionado</div>
                <div class="plano-voo">
                    <h3 id="plano-titulo" style="color:#38bdf8; margin-bottom:5px;">Selecione uma aeronave</h3>
                    <div class="plano-item"><span>Tipo de Operação:</span><strong id="p-operacao">-</strong></div>
                    <div class="plano-item"><span>Modelo / Fabricante:</span><strong id="p-modelo">-</strong></div>
                    <div class="plano-item"><span>Origem / Decolagem:</span><strong id="p-origem">-</strong></div>
                    <div class="plano-item"><span>Destino Estimado:</span><strong id="p-destino">-</strong></div>
                    <div class="plano-item"><span>Ocupação Cabine:</span><strong id="p-pax">-</strong></div>
                    <div class="plano-item"><span>Peso Atual / Máximo:</span><strong id="p-peso">-</strong></div>
                    <div class="plano-item"><span>Altitude / Velocidade:</span><strong id="p-alt-vel">-</strong></div>
                    <div class="plano-item"><span>Combustível / Autonomia:</span><strong id="p-combustivel">-</strong></div>
                </div>
            </div>
            <div class="panel" style="flex:1; display:flex; flex-direction:column;">
                <div class="panel-title">🚁 Frota Rastreada (Operação Ao Vivo)</div>
                <div class="tabela-container">
                    <table>
                        <thead>
                            <tr><th>CallSign</th><th>Operação</th><th>PAX</th><th>Alt / Vel</th></tr>
                        </thead>
                        <tbody id="tabela-frota"></tbody>
                    </table>
                </div>
            </div>
        </aside>
    </div>
    <script>
        const map = L.map('map').setView([-22.7610, -47.6530], 8);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

        let marcadores = {};
        let rotaPolyline = null, marcadorOrigem = null, marcadorDestino = null, selecaoAtualId = null;

        function limparRota() {
            if (rotaPolyline) { map.removeLayer(rotaPolyline); rotaPolyline = null; }
            if (marcadorOrigem) { map.removeLayer(marcadorOrigem); marcadorOrigem = null; }
            if (marcadorDestino) { map.removeLayer(marcadorDestino); marcadorDestino = null; }
            selecaoAtualId = null;
        }

        map.on('click', function(e) {
            limparRota();
            document.getElementById('plano-titulo').innerText = 'Selecione uma aeronave';
            document.getElementById('p-operacao').innerText = '-';
            document.getElementById('p-modelo').innerText = '-';
            document.getElementById('p-origem').innerText = '-';
            document.getElementById('p-destino').innerText = '-';
            document.getElementById('p-pax').innerText = '-';
            document.getElementById('p-peso').innerText = '-';
            document.getElementById('p-alt-vel').innerText = '-';
            document.getElementById('p-combustivel').innerText = '-';
        });

        let rotaPercorrida = null, rotaRestante = null;

        function limparRota() {
            if (rotaPercorrida) { map.removeLayer(rotaPercorrida); rotaPercorrida = null; }
            if (rotaRestante) { map.removeLayer(rotaRestante); rotaRestante = null; }
            if (marcadorOrigem) { map.removeLayer(marcadorOrigem); marcadorOrigem = null; }
            if (marcadorDestino) { map.removeLayer(marcadorDestino); marcadorDestino = null; }
            selecaoAtualId = null;
        }

        function desenharRota(aero) {
            limparRota();
            selecaoAtualId = aero.id;
            if (aero.origem && aero.destino) {
                const trechoPercorrido = [[aero.origem.lat, aero.origem.lng], [aero.latitude, aero.longitude]];
                const trechoRestante = [[aero.latitude, aero.longitude], [aero.destino.lat, aero.destino.lng]];

                // Trecho percorrido: Verde
                rotaPercorrida = L.polyline(trechoPercorrido, { color: '#10b981', weight: 4 }).addTo(map);

                // Trecho restante: Vermelho tracejado
                rotaRestante = L.polyline(trechoRestante, { color: '#ef4444', weight: 3, dashArray: '6, 6' }).addTo(map);

                marcadorOrigem = L.circleMarker([aero.origem.lat, aero.origem.lng], { radius: 6, color: '#10b981', fillColor: '#10b981', fillOpacity: 0.9 }).addTo(map).bindPopup(`🛫 <b>Origem:</b> ${aero.origem.nome}`);
                marcadorDestino = L.marker([aero.destino.lat, aero.destino.lng]).addTo(map).bindPopup(`🛬 <b>Destino:</b> ${aero.destino.nome}`);
            }
        }

        function selecionarAeronave(id, aeronaves) {
            const aero = aeronaves.find(a => a.id === id);
            if (!aero) return;
            const speedKmh = Math.round(aero.velocidade * 1.852);
            document.getElementById('plano-titulo').innerText = `🚁 ${aero.prefixo} [ICAO: ${aero.icao}]`;
            document.getElementById('p-operacao').innerText = aero.tipo_operacao;
            document.getElementById('p-modelo').innerText = `${aero.modelo} (${aero.fabricante})`;
            document.getElementById('p-origem').innerText = aero.origem.nome;
            document.getElementById('p-destino').innerText = aero.destino.nome;
            document.getElementById('p-pax').innerText = `${aero.pax_atual} A Bordo / ${aero.pax_max} Max`;
            document.getElementById('p-peso').innerText = `${aero.peso_atual} kg / ${aero.peso_max} kg (MTOW)`;
            document.getElementById('p-alt-vel').innerText = `${aero.altitude} ft | ${speedKmh} km/h (${aero.velocidade} kts)`;
            document.getElementById('p-combustivel').innerText = `${aero.combustivel}% (${aero.autonomia})`;
            desenharRota(aero);
        }

        function criarIconeHelicoptero(prefixo, corHex, heading) {
            const svgIcon = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="32" height="32" style="transform: rotate(${heading}deg);">
                <line x1="2" y1="12" x2="22" y2="12" stroke="${corHex}" stroke-width="2.5" stroke-linecap="round"/>
                <path fill="${corHex}" stroke="#ffffff" stroke-width="1.2" d="M12,4 C10,4 9,6 9,10 L9,14 C9,16 10,17 11,18 L11,21 L13,21 L13,18 C14,17 15,16 15,14 L15,10 C15,6 14,4 12,4 Z"/>
                <line x1="10" y1="21" x2="14" y2="21" stroke="${corHex}" stroke-width="2"/>
            </svg>`;
            return L.divIcon({
                html: `<div style="text-align:center;">${svgIcon}<div style="background-color:rgba(15,23,42,0.85); color:${corHex}; font-size:9px; font-weight:bold; border-radius:3px; padding:1px 3px; margin-top:-4px; white-space:nowrap; border:1px solid ${corHex};">${prefixo}</div></div>`,
                className: '', iconSize: [40, 40], iconAnchor: [20, 20]
            });
        }

        async function carregarTelemetria() {
            try {
                const res = await fetch('/api/telemetria');
                const aeronaves = await res.json();
                const tbody = document.getElementById('tabela-frota');
                tbody.innerHTML = '';

                aeronaves.forEach(aero => {
                    const speedKmh = Math.round(aero.velocidade * 1.852);
                    const tr = document.createElement('tr');
                    tr.onclick = (e) => {
                        e.stopPropagation();
                        map.setView([aero.latitude, aero.longitude], 10);
                        selecionarAeronave(aero.id, aeronaves);
                    };
                    tr.innerHTML = `<td style="font-weight:bold; color:${aero.cor_operacao};">${aero.prefixo}</td><td>${aero.tipo_operacao}</td><td>${aero.pax_atual}/${aero.pax_max} pax</td><td>${aero.altitude}ft / ${speedKmh}km/h</td>`;
                    tbody.appendChild(tr);

                    const iconCustom = criarIconeHelicoptero(aero.prefixo, aero.cor_operacao, aero.heading);
                    const popupContent = `<div style="font-size:12px;"><b>🚁 ${aero.prefixo} (${aero.modelo})</b><br><b>Operação:</b> ${aero.tipo_operacao}<br><b>Passageiros:</b> ${aero.pax_atual} de ${aero.pax_max} pax<br><b>Massa:</b> ${aero.peso_atual} kg<br><b>Altitude:</b> ${aero.altitude} ft | <b>Velocidade:</b> ${speedKmh} km/h (${aero.velocidade} kts)</div>`;

                    if (marcadores[aero.id]) {
                        marcadores[aero.id].setLatLng([aero.latitude, aero.longitude]);
                        marcadores[aero.id].setIcon(iconCustom);
                    } else {
                        const m = L.marker([aero.latitude, aero.longitude], { icon: iconCustom }).addTo(map).bindPopup(popupContent);
                        m.on('click', (e) => { L.DomEvent.stopPropagation(e); selecionarAeronave(aero.id, aeronaves); });
                        marcadores[aero.id] = m;
                    }
                });

                if (selecaoAtualId) {
                    const aeroSel = aeronaves.find(a => a.id === selecaoAtualId);
                    if (aeroSel) desenharRota(aeroSel);
                }
            } catch (err) { console.error(err); }
        }

        carregarTelemetria();
        setInterval(carregarTelemetria, 3000);
    </script>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
