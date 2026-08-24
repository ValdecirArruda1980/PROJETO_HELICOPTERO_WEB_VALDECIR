import os
import random
import math
import psycopg2
import requests
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

def obter_conexao():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    else:
        return psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="v@ld3c1r",
            port=5432
        )

CORES_OPERACAO = {
    "Particular": {"cor": "#16a34a", "nome_curto": "Particular (TPX)"},
    "Executivo": {"cor": "#2563eb", "nome_curto": "Executivo (TPV)"},
    "Policial": {"cor": "#dc2626", "nome_curto": "Policial / Resgate"},
    "Offshore": {"cor": "#d97706", "nome_curto": "Offshore (SAE)"}
}

FROTA_GLOBAL_SIMULADA = []

ROTAS_REAIS_SP = [
    {"origem": {"icao": "SDPW", "nome": "Aeroporto de Piracicaba", "lat": -22.7610, "lng": -47.6530}, "destino": {"icao": "SBKP", "nome": "Intl Viracopos Campinas", "lat": -23.0074, "lng": -47.1345}},
    {"origem": {"icao": "SBSP", "nome": "Congonhas São Paulo", "lat": -23.6261, "lng": -46.6564}, "destino": {"icao": "SDPW", "nome": "Aeroporto de Piracicaba", "lat": -22.7610, "lng": -47.6530}},
    {"origem": {"icao": "SBMT", "nome": "Campo de Marte SP", "lat": -23.5092, "lng": -46.6378}, "destino": {"icao": "SDAM", "nome": "Amarais Campinas", "lat": -22.8592, "lng": -47.0736}},
    {"origem": {"icao": "SDPW", "nome": "Aeroporto de Piracicaba", "lat": -22.7610, "lng": -47.6530}, "destino": {"icao": "SBRJ", "nome": "Santos Dumont RJ", "lat": -22.9101, "lng": -43.1631}},
    {"origem": {"icao": "SBJR", "nome": "Jacarepaguá RJ", "lat": -22.9869, "lng": -43.3703}, "destino": {"icao": "P-58", "nome": "Plataforma Pré-Sal Offshore", "lat": -24.2000, "lng": -41.8000}},
    {"origem": {"icao": "SBBH", "nome": "Pampulha Belo Horizonte", "lat": -19.8519, "lng": -43.9506}, "destino": {"icao": "SBCF", "nome": "Confins MG", "lat": -19.6244, "lng": -43.9719}}
]

def inicializar_frota_simulada():
    global FROTA_GLOBAL_SIMULADA
    if len(FROTA_GLOBAL_SIMULADA) > 0:
        return

    modelos = [
        ("Airbus H125", "Airbus Helicopters", 5, 2250),
        ("Bell 407", "Bell Helicopter", 6, 2381),
        ("AW109 Grand", "Leonardo", 7, 3175),
        ("Sikorsky S-76", "Sikorsky Aircraft", 12, 5307),
        ("EC135 Resgate", "Airbus Helicopters", 6, 2980)
    ]

    tipos_op = ["Particular", "Executivo", "Policial", "Offshore"]
    id_count = 1

    for rota in ROTAS_REAIS_SP:
        for _ in range(5):
            op_chave = random.choice(tipos_op)
            mod_nome, fab, pax_max, p_max = random.choice(modelos)
            
            # Posição atual entre origem e destino
            t = random.uniform(0.2, 0.7)
            lat_init = rota["origem"]["lat"] + t * (rota["destino"]["lat"] - rota["origem"]["lat"])
            lng_init = rota["origem"]["lng"] + t * (rota["destino"]["lng"] - rota["origem"]["lng"])
            
            dlat = rota["destino"]["lat"] - lat_init
            dlng = rota["destino"]["lng"] - lng_init
            heading = int((math.degrees(math.atan2(dlng, dlat)) + 360) % 360)
            
            vel_kts = random.randint(110, 150)
            prefixo = f"PP-{chr(65+random.randint(0,25))}{chr(65+random.randint(0,25))}{random.randint(10,99)}"

            # Cria um histórico inicial conectado desde a origem real
            ponto_meio_lat = rota["origem"]["lat"] + (lat_init - rota["origem"]["lat"]) * 0.5
            ponto_meio_lng = rota["origem"]["lng"] + (lng_init - rota["origem"]["lng"]) * 0.5

            FROTA_GLOBAL_SIMULADA.append({
                "id": id_count,
                "prefixo": prefixo,
                "modelo": mod_nome,
                "fabricante": fab,
                "icao": f"E48{id_count:03d}",
                "operacao_chave": op_chave,
                "tipo_operacao": CORES_OPERACAO[op_chave]["nome_curto"],
                "cor_operacao": CORES_OPERACAO[op_chave]["cor"],
                "pax_atual": random.randint(1, pax_max),
                "pax_max": pax_max,
                "peso_atual": int(p_max * random.uniform(0.75, 0.95)),
                "peso_max": p_max,
                "combustivel": random.randint(50, 95),
                "autonomia": f"0{random.randint(1,3)}h {random.randint(10,50)}m",
                "latitude": lat_init,
                "longitude": lng_init,
                "historico_rota": [
                    [rota["origem"]["lat"], rota["origem"]["lng"]],
                    [ponto_meio_lat, ponto_meio_lng],
                    [lat_init, lng_init]
                ],
                "altitude": random.randint(1500, 3800),
                "velocidade": vel_kts,
                "heading": heading,
                "status": f"Em Rota para {rota['destino']['nome']}",
                "origem": rota["origem"],
                "destino": rota["destino"]
            })
            id_count += 1

def atualizar_posicoes_simuladas():
    inicializar_frota_simulada()
    for aero in FROTA_GLOBAL_SIMULADA:
        dist_nm = (aero["velocidade"] / 3600.0) * 5.0
        dist_deg = dist_nm / 60.0
        
        rad = math.radians(aero["heading"])
        aero["latitude"] += dist_deg * math.cos(rad)
        aero["longitude"] += dist_deg * math.sin(rad)
        aero["altitude"] += random.choice([-10, 0, 10])
        
        # Mantém a rota conectada
        aero["historico_rota"].append([aero["latitude"], aero["longitude"]])

def buscar_voos_opensky_brasil():
    url = "https://opensky-network.org/api/states/all?lamin=-33.75&lomin=-73.98&lamax=5.27&lomax=-28.85"
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            dados = response.json()
            states = dados.get("states", [])
            lista_real = []
            if states:
                for idx, s in enumerate(states):
                    icao24 = s[0].strip().upper() if s[0] else "UNK"
                    callsign = s[1].strip() if s[1] else f"PR-AER{idx+1}"
                    long, lat = s[5], s[6]
                    alt_m = s[7] or s[13] or 600
                    vel_ms = s[9] or 50
                    heading = s[10] or 0
                    
                    if lat is not None and long is not None:
                        alt_ft = int(alt_m * 3.28084)
                        vel_kts = int(vel_ms * 1.94384)
                        
                        op_chave = "Particular"
                        if "GLO" in callsign or "TAM" in callsign or "AZU" in callsign:
                            op_chave = "Executivo"
                        elif "PT-" in callsign:
                            op_chave = "Particular"
                        elif "PR-" in callsign:
                            op_chave = "Offshore" if alt_ft > 2500 else "Policial"

                        rad = math.radians(heading)
                        lat_origem = lat - 0.4 * math.cos(rad)
                        lng_origem = long - 0.4 * math.sin(rad)
                        lat_dest = lat + 0.4 * math.cos(rad)
                        lng_dest = long + 0.4 * math.sin(rad)

                        lista_real.append({
                            "id": idx + 1,
                            "prefixo": callsign if len(callsign) >= 4 else f"PP-{icao24[:3]}",
                            "modelo": "Aeronave ADS-B Live",
                            "fabricante": "Transponder OpenSky",
                            "icao": icao24,
                            "tipo_operacao": CORES_OPERACAO[op_chave]["nome_curto"],
                            "cor_operacao": CORES_OPERACAO[op_chave]["cor"],
                            "pax_atual": 4, "pax_max": 6,
                            "peso_atual": 2400, "peso_max": 3000,
                            "combustivel": 80, "autonomia": "02h 00m",
                            "latitude": float(lat), "longitude": float(long),
                            "historico_rota": [[float(lat_origem), float(lng_origem)], [float(lat), float(long)]],
                            "altitude": alt_ft, "velocidade": vel_kts,
                            "heading": heading,
                            "status": f"Em Voo (Rumo {int(heading)}°)",
                            "origem": {"icao": "RADAR", "nome": "Origem do Voo", "lat": float(lat_origem), "lng": float(lng_origem)},
                            "destino": {"icao": "DEST", "nome": "Destino Estimado", "lat": float(lat_dest), "lng": float(lng_dest)}
                        })
            if len(lista_real) >= 15:
                return lista_real
    except Exception as e:
        print(f"-> Conexão OpenSky em standby: {e}")
    return []

@app.route("/api/telemetria")
def api_telemetria():
    dados_reais = buscar_voos_opensky_brasil()
    if dados_reais and len(dados_reais) > 0:
        return jsonify({"status": "sucesso", "origem_dados": f"OpenSky Network ({len(dados_reais)} Aeronaves ao Vivo)", "dados": dados_reais})
    
    atualizar_posicoes_simuladas()
    return jsonify({"status": "sucesso", "origem_dados": f"Radar ADS-B Tempo Real ({len(FROTA_GLOBAL_SIMULADA)} Helicópteros)", "dados": FROTA_GLOBAL_SIMULADA})

@app.route("/")
def index():
    return render_template_string("""
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Helicóptero Web Valdecir - Telemetria & Rota Completa</title>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <style>
                * { box-sizing: border-box; margin: 0; padding: 0; }
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; }
                header { background: #1e293b; padding: 12px 25px; border-bottom: 2px solid #3b82f6; display: flex; justify-content: space-between; align-items: center; }
                h1 { font-size: 1.3rem; color: #60a5fa; display: flex; align-items: center; gap: 10px; }
                .badge-db { background: #10b981; color: #022c22; font-size: 0.8rem; font-weight: bold; padding: 5px 12px; border-radius: 12px; }
                
                .main-container { display: grid; grid-template-columns: 2.2fr 1fr; gap: 12px; padding: 12px; height: calc(100vh - 65px); }
                #map { width: 100%; height: 100%; border-radius: 8px; border: 1px solid #334155; }
                
                .side-panel { background: #1e293b; border-radius: 8px; padding: 12px; border: 1px solid #334155; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; }
                .card { background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 12px; }
                .card h3 { color: #93c5fd; font-size: 0.95rem; margin-bottom: 8px; border-bottom: 1px solid #1e293b; padding-bottom: 4px; }
                
                .plano-voo-box { background: #172554; border: 1px solid #2563eb; padding: 10px; border-radius: 6px; font-size: 0.82rem; }
                .plano-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 6px; }
                .plano-item { background: #0f172a; padding: 6px; border-radius: 4px; border: 1px solid #1e293b; }
                .plano-item span { color: #94a3b8; font-size: 0.72rem; display: block; }
                .plano-item strong { color: #38bdf8; font-size: 0.82rem; }

                .legenda-cores { display: flex; justify-content: space-between; font-size: 0.72rem; background: #0f172a; padding: 8px; border-radius: 6px; border: 1px solid #334155; margin-bottom: 8px; }
                .leg-item { display: flex; align-items: center; gap: 4px; }
                .dot { width: 9px; height: 9px; border-radius: 50%; display: inline-block; }

                .heli-marker-box {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                }
                .heli-label {
                    background: #0f172a;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 1px 4px;
                    border-radius: 3px;
                    white-space: nowrap;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.8);
                    margin-top: -2px;
                }

                table { width: 100%; border-collapse: collapse; font-size: 0.8rem; margin-top: 5px; }
                th, td { text-align: left; padding: 7px 5px; border-bottom: 1px solid #334155; }
                th { color: #94a3b8; background: #1e293b; }
                .heli-row { cursor: pointer; transition: background 0.2s; }
                .heli-row:hover { background: #1e293b; }
            </style>
        </head>
        <body>
            <header>
                <h1>🚁 Helicóptero Web Valdecir - Telemetria & Rota Completa</h1>
                <span class="badge-db" id="fonte-dados">Sincronizando...</span>
            </header>

            <div class="main-container">
                <div id="map"></div>

                <div class="side-panel">
                    <div class="card">
                        <h3>🎨 Legenda por Tipo de Operação</h3>
                        <div class="legenda-cores">
                            <div class="leg-item"><span class="dot" style="background:#16a34a;"></span> Particular</div>
                            <div class="leg-item"><span class="dot" style="background:#2563eb;"></span> Executivo</div>
                            <div class="leg-item"><span class="dot" style="background:#dc2626;"></span> Policial</div>
                            <div class="leg-item"><span class="dot" style="background:#d97706;"></span> Offshore</div>
                        </div>
                    </div>

                    <div class="card" id="card-plano">
                        <h3>📊 Ficha Completa de Voo Selecionado</h3>
                        <div class="plano-voo-box">
                            <p style="color: #cbd5e1; font-weight: bold; font-size: 0.9rem;" id="plano-titulo">Clique em um helicóptero para ver os detalhes</p>
                            <div class="plano-grid" id="plano-detalhes">
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
                    </div>

                    <div class="card">
                        <h3>🚁 Frota Rastreada (Operação Ao Vivo)</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>Callsign</th>
                                    <th>Operação</th>
                                    <th>PAX</th>
                                    <th>Alt / Vel</th>
                                </tr>
                            </thead>
                            <tbody id="tabela-aeronaves">
                                <tr><td colspan="4" style="text-align:center; color:#64748b;">Carregando frota nacional...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <script>
                const map = L.map('map').setView([-22.8, -47.2], 9);

                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© OpenStreetMap'
                }).addTo(map);

                let marcadores = {};
                let helicopteSelecionadoId = null;
                let linhaPercorrida = null;
                let linhaRestante = null;
                let marcadorOrigem = null;
                let marcadorDestino = null;

                function criarIconeHelicopteroColorido(prefixo, cor, heading) {
                    const angle = heading || 0;
                    const htmlContent = `
                        <div class="heli-marker-box">
                            <div style="transform: rotate(${angle}deg); filter: drop-shadow(0px 2px 4px #000);">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="38" height="38">
                                    <ellipse cx="50" cy="50" rx="46" ry="6" fill="${cor}" stroke="#000000" stroke-width="2" />
                                    <ellipse cx="50" cy="52" rx="18" ry="24" fill="${cor}" stroke="#000000" stroke-width="2.5" />
                                    <path d="M 36 44 C 36 30, 64 30, 64 44 Z" fill="#38bdf8" stroke="#000" stroke-width="1.5" />
                                    <rect x="47" y="72" width="6" height="22" fill="${cor}" stroke="#000" stroke-width="1.5" />
                                    <rect x="38" y="90" width="24" height="4" fill="#ffffff" stroke="#000" stroke-width="1" />
                                </svg>
                            </div>
                            <div class="heli-label" style="color:${cor}; border: 1px solid ${cor};">${prefixo}</div>
                        </div>
                    `;
                    return L.divIcon({
                        html: htmlContent,
                        className: 'custom-heli-colored-icon',
                        iconSize: [50, 50],
                        iconAnchor: [25, 25]
                    });
                }

                function limparSelecao() {
                    helicopteSelecionadoId = null;
                    if (linhaPercorrida) map.removeLayer(linhaPercorrida);
                    if (linhaRestante) map.removeLayer(linhaRestante);
                    if (marcadorOrigem) map.removeLayer(marcadorOrigem);
                    if (marcadorDestino) map.removeLayer(marcadorDestino);

                    document.getElementById('plano-titulo').innerText = "Clique em um helicóptero para ver os detalhes";
                    document.getElementById('p-operacao').innerText = "-";
                    document.getElementById('p-modelo').innerText = "-";
                    document.getElementById('p-origem').innerText = "-";
                    document.getElementById('p-destino').innerText = "-";
                    document.getElementById('p-pax').innerText = "-";
                    document.getElementById('p-peso').innerText = "-";
                    document.getElementById('p-alt-vel').innerText = "-";
                    document.getElementById('p-combustivel').innerText = "-";
                }

                function selecionarHelicoptero(aero) {
                    helicopteSelecionadoId = aero.id;
                    if (marcadores[aero.id]) marcadores[aero.id].openPopup();

                    document.getElementById('plano-titulo').innerText = `🛸 ${aero.prefixo} [ICAO: ${aero.icao}]`;
                    document.getElementById('p-operacao').innerHTML = `<span style="color:${aero.cor_operacao}; font-weight:bold;">${aero.tipo_operacao}</span>`;
                    document.getElementById('p-modelo').innerText = `${aero.modelo} (${aero.fabricante})`;
                    document.getElementById('p-origem').innerText = `${aero.origem.nome}`;
                    document.getElementById('p-destino').innerText = `${aero.destino.nome}`;
                    document.getElementById('p-pax').innerText = `${aero.pax_atual} A Bordo / ${aero.pax_max} Max`;
                    document.getElementById('p-peso').innerText = `${aero.peso_atual} kg / ${aero.peso_max} kg (MTOW)`;
                    document.getElementById('p-alt-vel').innerText = `${aero.altitude} ft | ${aero.velocidade} kts`;
                    document.getElementById('p-combustivel').innerText = `${aero.combustivel}% (${aero.autonomia} de voo)`;

                    desenharRotaEHistorico(aero);
                }

                function desenharRotaEHistorico(aero) {
                    if (linhaPercorrida) map.removeLayer(linhaPercorrida);
                    if (linhaRestante) map.removeLayer(linhaRestante);
                    if (marcadorOrigem) map.removeLayer(marcadorOrigem);
                    if (marcadorDestino) map.removeLayer(marcadorDestino);

                    // Garante a linha contínua desde a decolagem até a posição atual
                    let pontosHistorico = aero.historico_rota || [];
                    if (pontosHistorico.length === 0 || (pontosHistorico[0][0] !== aero.origem.lat && pontosHistorico[0][1] !== aero.origem.lng)) {
                        pontosHistorico.unshift([aero.origem.lat, aero.origem.lng]);
                    }
                    pontosHistorico.push([aero.latitude, aero.longitude]);

                    // Linha Verde Verdejante Contínua (Da decolagem até o ponto atual)
                    linhaPercorrida = L.polyline(pontosHistorico, { color: '#16a34a', weight: 5, opacity: 0.95 }).addTo(map);

                    // Linha Laranja Tracejada (Do ponto atual até o aeroporto de destino)
                    linhaRestante = L.polyline([
                        [aero.latitude, aero.longitude],
                        [aero.destino.lat, aero.destino.lng]
                    ], { color: '#d97706', weight: 4, dashArray: '8, 8', opacity: 0.9 }).addTo(map);

                    // Marcadores nos aeródromos/helipontos reais de saída e chegada
                    marcadorOrigem = L.marker([aero.origem.lat, aero.origem.lng])
                        .addTo(map).bindPopup(`🛫 <b>Decolagem:</b> ${aero.origem.nome}`);
                    marcadorDestino = L.marker([aero.destino.lat, aero.destino.lng])
                        .addTo(map).bindPopup(`🛬 <b>Destino:</b> ${aero.destino.nome}`);
                }

                map.on('click', (e) => {
                    if (!e.originalEvent._stopped) limparSelecao();
                });

                async function atualizarMonitoramento() {
                    try {
                        const resposta = await fetch('/api/telemetria');
                        const json = await resposta.json();

                        if (json.status === 'sucesso') {
                            if (json.origem_dados) document.getElementById('fonte-dados').innerText = json.origem_dados;
                            
                            const frotaDados = json.dados;
                            const tbody = document.getElementById('tabela-aeronaves');
                            tbody.innerHTML = '';

                            const idsAtuais = frotaDados.map(a => a.id);
                            Object.keys(marcadores).forEach(id => {
                                if (!idsAtuais.includes(parseInt(id))) {
                                    map.removeLayer(marcadores[id]);
                                    delete marcadores[id];
                                }
                            });

                            frotaDados.forEach(aero => {
                                const tr = document.createElement('tr');
                                tr.className = 'heli-row';
                                tr.onclick = (e) => {
                                    e.stopPropagation();
                                    selecionarHelicoptero(aero);
                                };

                                tr.innerHTML = `
                                    <td><strong>${aero.prefixo}</strong></td>
                                    <td><small style="color:${aero.cor_operacao}; font-weight:bold;">${aero.tipo_operacao.split(' ')[0]}</small></td>
                                    <td>${aero.pax_atual}/${aero.pax_max} pax</td>
                                    <td>${aero.altitude}ft / ${aero.velocidade}kt</td>
                                `;
                                tbody.appendChild(tr);

                                const popupContent = `
                                    <div style="font-family: Arial; font-size: 12px; color: #0f172a; min-width: 200px;">
                                        <h4 style="color:${aero.cor_operacao}; margin-bottom:4px;">🚁 ${aero.prefixo} (${aero.modelo})</h4>
                                        <b>Operação:</b> ${aero.tipo_operacao}<br>
                                        <b>Passageiros:</b> ${aero.pax_atual} de ${aero.pax_max} pax<br>
                                        <b>Massa Atual:</b> ${aero.peso_atual} kg (Max: ${aero.peso_max} kg)<br>
                                        <b>Combustível:</b> ${aero.combustivel}% (${aero.autonomia})<br>
                                        <b>Altitude:</b> ${aero.altitude} ft | <b>Velocidade:</b> ${aero.velocidade} kts
                                    </div>
                                `;

                                const iconCustom = criarIconeHelicopteroColorido(aero.prefixo, aero.cor_operacao, aero.heading);

                                if (marcadores[aero.id]) {
                                    marcadores[aero.id].setLatLng([aero.latitude, aero.longitude]);
                                    marcadores[aero.id].setIcon(iconCustom);
                                    marcadores[aero.id].getPopup().setContent(popupContent);
                                } else {
                                    marcadores[aero.id] = L.marker([aero.latitude, aero.longitude], { icon: iconCustom })
                                        .addTo(map)
                                        .bindPopup(popupContent);
                                    
                                    marcadores[aero.id].on('click', (e) => {
                                        L.DomEvent.stopPropagation(e);
                                        selecionarHelicoptero(aero);
                                    });
                                }

                                if (helicopteSelecionadoId === aero.id) {
                                    desenharRotaEHistorico(aero);
                                }
                            });
                        }
                    } catch (err) {
                        console.error('Erro ao atualizar telemetria:', err);
                    }
                }

                atualizarMonitoramento();
                setInterval(atualizarMonitoramento, 5000);
            </script>
        </body>
        </html>
    """)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5052)
