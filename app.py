import math
import random
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

CORES_OPERACAO = {
    "particular": {"nome": "Particular", "nome_curto": "Particular", "cor": "#10b981"},
    "executivo": {"nome": "Executivo (TPV)", "nome_curto": "Executivo", "cor": "#3b82f6"},
    "policial": {"nome": "Policial / Resgate (CGPA)", "nome_curto": "Policial", "cor": "#ef4444"},
    "offshore": {"nome": "Offshore (Plataforma)", "nome_curto": "Offshore", "cor": "#f59e0b"}
}

HELICOPTEROS_MODELOS = {
    "particular": [
        ("Robinson R44 Raven II", "Robinson", 3, 1134),
        ("Robinson R66 Turbine", "Robinson", 4, 1225),
        ("Bell 505 Jet Ranger X", "Bell", 4, 1660),
        ("Airbus H125 Esquilo", "Airbus Helicopters", 5, 2250)
    ],
    "executivo": [
        ("AW109 Grand", "Leonardo", 7, 3175),
        ("Airbus H145", "Airbus Helicopters", 8, 3800),
        ("Bell 429 GlobalRanger", "Bell", 7, 3175),
        ("Sikorsky S-76C++", "Sikorsky", 12, 5306)
    ],
    "policial": [
        ("Airbus H125 Águia/Ás", "Airbus Helicopters", 5, 2250),
        ("AW119 Koala", "Leonardo", 7, 2850),
        ("EC135 T3", "Airbus Helicopters", 6, 2980)
    ],
    "offshore": [
        ("Sikorsky S-92A", "Sikorsky", 19, 12020),
        ("AW139 Offshore", "Leonardo", 15, 6800),
        ("Airbus H175", "Airbus Helicopters", 16, 7500)
    ]
}

FROTA_GLOBAL_SIMULADA = []

BASES_E_ROTAS = [
    {"origem": {"icao": "SDPW", "nome": "Aeroporto de Piracicaba", "lat": -22.7610, "lng": -47.6530}, "destino": {"icao": "SBKP", "nome": "Intl Viracopos Campinas", "lat": -23.0074, "lng": -47.1345}},
    {"origem": {"icao": "SBSP", "nome": "Congonhas São Paulo", "lat": -23.6261, "lng": -46.6564}, "destino": {"icao": "SDPW", "nome": "Aeroporto de Piracicaba", "lat": -22.7610, "lng": -47.6530}},
    {"origem": {"icao": "SBMT", "nome": "Campo de Marte SP", "lat": -23.5092, "lng": -46.6378}, "destino": {"icao": "SDAM", "nome": "Amarais Campinas", "lat": -22.8592, "lng": -47.0736}},
    {"origem": {"icao": "SDPW", "nome": "Aeroporto de Piracicaba", "lat": -22.7610, "lng": -47.6530}, "destino": {"icao": "SBRJ", "nome": "Santos Dumont RJ", "lat": -22.9101, "lng": -43.1631}},
    {"origem": {"icao": "SBJR", "nome": "Jacarepaguá RJ", "lat": -22.9869, "lng": -43.3703}, "destino": {"icao": "P-58", "nome": "Plataforma Pré-Sal Offshore", "lat": -24.2000, "lng": -41.8000}},
    {"origem": {"icao": "SBBH", "nome": "Pampulha Belo Horizonte", "lat": -19.8519, "lng": -43.9506}, "destino": {"icao": "SBCF", "nome": "Confins MG", "lat": -19.6244, "lng": -43.9719}},
    {"origem": {"icao": "SBBR", "nome": "Brasília DF", "lat": -15.8697, "lng": -47.9208}, "destino": {"icao": "SBGO", "nome": "Goiânia GO", "lat": -16.6322, "lng": -49.2212}},
    {"origem": {"icao": "SBCT", "nome": "Afonso Pena Curitiba", "lat": -25.5317, "lng": -49.1761}, "destino": {"icao": "SBFL", "nome": "Hercílio Luz Florianópolis", "lat": -27.6703, "lng": -48.5525}},
    {"origem": {"icao": "SBSV", "nome": "Deputado Luís Eduardo Magalhães Salvador", "lat": -12.9086, "lng": -38.3225}, "destino": {"icao": "SBRF", "nome": "Guararapes Recife", "lat": -8.1268, "lng": -34.9229}}
]

def inicializar_frota_simulada_500():
    global FROTA_GLOBAL_SIMULADA
    if len(FROTA_GLOBAL_SIMULADA) >= 500:
        return
    
    FROTA_GLOBAL_SIMULADA = []
    chaves_operacao = list(CORES_OPERACAO.keys())
    
    for id_count in range(1, 501):
        op_chave = random.choice(chaves_operacao)
        modelos = HELICOPTEROS_MODELOS[op_chave]
        rota = random.choice(BASES_E_ROTAS)
        
        mod_nome, fab, pax_max, p_max = random.choice(modelos)
        
        lat_base = rota["origem"]["lat"]
        lng_base = rota["origem"]["lng"]
        
        # Coordenadas exatas do destino para bater com o nome correto
        lat_dest = rota["destino"]["lat"]
        lng_dest = rota["destino"]["lng"]

        t = random.uniform(0.1, 0.9)
        lat_init = lat_base + t * (lat_dest - lat_base)
        lng_init = lng_base + t * (lng_dest - lng_base)

        dlat = lat_dest - lat_init
        dlng = lng_dest - lng_init
        heading = int((math.degrees(math.atan2(dlng, dlat)) + 360) % 360)

        vel_kts = random.randint(100, 160)
        prefixo = f"PP-{chr(65+random.randint(0,25))}{chr(65+random.randint(0,25))}{random.randint(10,99)}"

        ponto_meio_lat = lat_base + (lat_init - lat_base) * 0.5
        ponto_meio_lng = lng_base + (lng_init - lng_base) * 0.5

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
            "combustivel": random.randint(40, 98),
            "autonomia": f"0{random.randint(1,3)}h {random.randint(10,50)}m",
            "latitude": lat_init,
            "longitude": lng_init,
            "historico_rota": [
                [lat_base, lng_base],
                [ponto_meio_lat, ponto_meio_lng],
                [lat_init, lng_init]
            ],
            "altitude": random.randint(1200, 4200),
            "velocidade": vel_kts,
            "heading": heading,
            "status": f"Em Rota Operacional",
            "origem": {"icao": rota["origem"]["icao"], "nome": rota["origem"]["nome"], "lat": lat_base, "lng": lng_base},
            "destino": {"icao": rota["destino"]["icao"], "nome": rota["destino"]["nome"], "lat": lat_dest, "lng": lng_dest}
        })

def atualizar_posicoes_simuladas():
    inicializar_frota_simulada_500()
    for aero in FROTA_GLOBAL_SIMULADA:
        rad = math.radians(aero["heading"])
        passo = 0.003
        
        nova_lat = aero["latitude"] + passo * math.cos(rad)
        nova_lng = aero["longitude"] + passo * math.sin(rad)
        
        aero["latitude"] = nova_lat
        aero["longitude"] = nova_lng
        
        aero["historico_rota"].append([nova_lat, nova_lng])
        if len(aero["historico_rota"]) > 30:
            aero["historico_rota"].pop(0)

@app.route('/api/telemetria')
def api_telemetria():
    atualizar_posicoes_simuladas()
    return jsonify(FROTA_GLOBAL_SIMULADA)

INDEX_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Helicóptero Web Valdecir - Telemetria ADS-B</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { display: flex; flex-direction: column; height: 100vh; background-color: #0f172a; color: #f8fafc; }
        header { background-color: #1e293b; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #334155; }
        h1 { font-size: 1.2rem; font-weight: 600; color: #38bdf8; display: flex; align-items: center; gap: 10px; }
        .badge-live { background-color: #059669; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; }
        .main-container { display: flex; flex: 1; overflow: hidden; }
        #map { flex: 1; height: 100%; background-color: #1e293b; }
        .sidebar { width: 380px; background-color: #0f172a; border-left: 2px solid #334155; display: flex; flex-direction: column; padding: 15px; gap: 15px; overflow-y: auto; }
        .panel { background-color: #1e293b; border-radius: 8px; padding: 15px; border: 1px solid #334155; }
        .panel-title { font-size: 0.95rem; font-weight: bold; color: #94a3b8; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #334155; padding-bottom: 6px; }
        .legenda-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.8rem; }
        .legenda-item { display: flex; align-items: center; gap: 6px; }
        .dot { width: 10px; height: 10px; border-radius: 50%; }
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
        <span class="badge-live">Radar ADS-B Alta Densidade (500 Helicópteros)</span>
    </header>

    <div class="main-container">
        <div id="map"></div>
        <aside class="sidebar">
            <div class="panel">
                <div class="panel-title">🎨 Legenda por Tipo de Operação</div>
                <div class="legenda-grid">
                    <div class="legenda-item"><div class="dot" style="background-color:#10b981;"></div>Particular</div>
                    <div class="legenda-item"><div class="dot" style="background-color:#3b82f6;"></div>Executivo</div>
                    <div class="legenda-item"><div class="dot" style="background-color:#ef4444;"></div>Policial</div>
                    <div class="legenda-item"><div class="dot" style="background-color:#f59e0b;"></div>Offshore</div>
                </div>
            </div>

            <div class="panel">
                <div class="panel-title">📊 Ficha Completa de Voo Selecionado</div>
                <div class="plano-voo" id="detalhes-voo">
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
                            <tr>
                                <th>CallSign</th>
                                <th>Operação</th>
                                <th>PAX</th>
                                <th>Alt / Vel</th>
                            </tr>
                        </thead>
                        <tbody id="tabela-frota"></tbody>
                    </table>
                </div>
            </div>
        </aside>
    </div>

    <script>
        const map = L.map('map').setView([-23.0000, -46.8000], 8);
        map.on('click', function(e) {
            // Evita limpar se o clique for em um elemento interativo
            if (e.originalEvent && e.originalEvent.defaultPrevented) return;
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
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap'
        }).addTo(map);

        let marcadores = {};
        let selecaoAtualId = null;
        let rotaPolyline = null;
        let marcadorOrigem = null;
        let marcadorDestino = null;

        function criarIconeHelicopteroColorido(prefixo, corHex, heading) {
            const svgIcon = `
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="32" height="32" style="transform: rotate(${heading}deg);">
                    <line x1="2" y1="12" x2="22" y2="12" stroke="${corHex}" stroke-width="2.5" stroke-linecap="round"/>
                    <path fill="${corHex}" stroke="#ffffff" stroke-width="1.2" d="M12,4 C10,4 9,6 9,10 L9,14 C9,16 10,17 11,18 L11,21 L13,21 L13,18 C14,17 15,16 15,14 L15,10 C15,6 14,4 12,4 Z"/>
                    <line x1="10" y1="21" x2="14" y2="21" stroke="${corHex}" stroke-width="2"/>
                </svg>`;
            return L.divIcon({
                html: `<div style="text-align:center;">
                        ${svgIcon}
                        <div style="background-color:rgba(15,23,42,0.85); color:${corHex}; font-size:9px; font-weight:bold; border-radius:3px; padding:1px 3px; margin-top:-4px; white-space:nowrap; border:1px solid ${corHex};">${prefixo}</div>
                       </div>`,
                className: '',
                iconSize: [40, 40],
                iconAnchor: [20, 20]
            });
        }

        function selecionarAeronave(id, aeronaves) {
            const aero = aeronaves.find(a => a.id === id);
            if (!aero) return;
            selecaoAtualId = id;

            const speedKmh = Math.round(aero.velocidade * 1.852);
            const velTexto = `${speedKmh} km/h (${aero.velocidade} kts)`;

            document.getElementById('plano-titulo').innerText = `🛸 ${aero.prefixo} [ICAO: ${aero.icao}]`;
            document.getElementById('p-operacao').innerHTML = `<span style="color:${aero.cor_operacao}; font-weight:bold;">${aero.tipo_operacao}</span>`;
            document.getElementById('p-modelo').innerText = `${aero.modelo} (${aero.fabricante})`;
            document.getElementById('p-origem').innerText = `${aero.origem.nome}`;
            document.getElementById('p-destino').innerText = `${aero.destino.nome}`;
            document.getElementById('p-pax').innerText = `${aero.pax_atual} A Bordo / ${aero.pax_max} Max`;
            document.getElementById('p-peso').innerText = `${aero.peso_atual} kg / ${aero.peso_max} kg (MTOW)`;
            document.getElementById('p-alt-vel').innerText = `${aero.altitude} ft | ${velTexto}`;
            document.getElementById('p-combustivel').innerText = `${aero.combustivel}% (${aero.autonomia} de voo)`;

            desenharRotaEHistorico(aero);
        }

        
        function limparRota() {
            if (rotaPolyline) { map.removeLayer(rotaPolyline); rotaPolyline = null; }
            if (marcadorOrigem) { map.removeLayer(marcadorOrigem); marcadorOrigem = null; }
            if (marcadorDestino) { map.removeLayer(marcadorDestino); marcadorDestino = null; }
            selecaoAtualId = null;
        }

        function desenharRotaEHistorico(aero) {
            if (rotaPolyline) map.removeLayer(rotaPolyline);
            if (marcadorOrigem) map.removeLayer(marcadorOrigem);
            if (marcadorDestino) map.removeLayer(marcadorDestino);

            if (aero.origem && aero.destino) {
                const pontos = [
                    [aero.origem.lat, aero.origem.lng],
                    [aero.latitude, aero.longitude],
                    [aero.destino.lat, aero.destino.lng]
                ];
                
                rotaPolyline = L.polyline(pontos, { color: aero.cor_operacao, weight: 3, dashArray: '6, 6' }).addTo(map);
                
                marcadorOrigem = L.circleMarker([aero.origem.lat, aero.origem.lng], { radius: 6, color: '#38bdf8', fillColor: '#38bdf8', fillOpacity: 0.8 }).addTo(map).bindPopup(`🛫 <b>Origem:</b> ${aero.origem.nome}`);
                marcadorDestino = L.marker([aero.destino.lat, aero.destino.lng]).addTo(map).bindPopup(`🛬 <b>Destino:</b> ${aero.destino.nome}`);
            }
        }

        async function carregarTelemetria() {
            try {
                const response = await fetch('/api/telemetria');
                const aeronaves = await response.json();

                const tbody = document.getElementById('tabela-frota');
                tbody.innerHTML = '';

                aeronaves.forEach(aero => {
                    const speedKmh = Math.round(aero.velocidade * 1.852);
                    const velTexto = `${speedKmh}km/h (${aero.velocidade}kt)`;

                    const tr = document.createElement('tr');
                    tr.onclick = () => {
                        map.setView([aero.latitude, aero.longitude], 10);
                        selecionarAeronave(aero.id, aeronaves);
                    };
                    tr.innerHTML = `
                        <td style="font-weight:bold; color:${aero.cor_operacao};">${aero.prefixo}</td>
                        <td>${aero.tipo_operacao}</td>
                        <td>${aero.pax_atual}/${aero.pax_max} pax</td>
                        <td>${aero.altitude}ft / ${speedKmh}km/h</td>
                    `;
                    tbody.appendChild(tr);

                    const popupContent = `
                        <div style="font-size:12px; font-family:sans-serif;">
                            <h4 style="color:${aero.cor_operacao}; margin-bottom:4px;">🚁 ${aero.prefixo} (${aero.modelo})</h4>
                            <b>Operação:</b> ${aero.tipo_operacao}<br>
                            <b>Passageiros:</b> ${aero.pax_atual} de ${aero.pax_max} pax<br>
                            <b>Massa Atual:</b> ${aero.peso_atual} kg (Max: ${aero.peso_max} kg)<br>
                            <b>Combustível:</b> ${aero.combustivel}% (${aero.autonomia})<br>
                            <b>Altitude:</b> ${aero.altitude} ft | <b>Velocidade:</b> ${speedKmh} km/h (${aero.velocidade} kts)
                        </div>
                    `;

                    const iconCustom = criarIconeHelicopteroColorido(aero.prefixo, aero.cor_operacao, aero.heading);

                    if (marcadores[aero.id]) {
                        marcadores[aero.id].setLatLng([aero.latitude, aero.longitude]);
                        marcadores[aero.id].setIcon(iconCustom);
                        marcadores[aero.id].getPopup().setContent(popupContent);
                    } else {
                        const m = L.marker([aero.latitude, aero.longitude], { icon: iconCustom })
                            .addTo(map)
                            .bindPopup(popupContent);
                        
                        m.on('click', () => selecionarAeronave(aero.id, aeronaves));
                        marcadores[aero.id] = m;
                    }
                });

                if (selecaoAtualId) {
                    selecionarAeronave(selecaoAtualId, aeronaves);
                }

            } catch (err) {
                console.error("Erro ao carregar telemetria ADS-B:", err);
            }
        }

        carregarTelemetria();
        setInterval(carregarTelemetria, 3000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
