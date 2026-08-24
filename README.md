# 🚁 Helicóptero Web Valdecir - Radar ADS-B & Telemetria em Tempo Real

Aplicações Web em Python Flask para monitoramento aéreo de aeronaves e helicópteros em tempo real sobre o território nacional, com classificação por tipo de operação, cálculo de rotas e telemetria completa.

## 📌 Funcionalidades Principais

- **Telemetria de Voo Completa:** Exibição de Altitude, Velocidade (kts), Porcentagem de Combustível, Autonomia, Ocupação de Cabine (PAX) e Peso Atual vs. MTOW (kg).
- **Classificação Visual por Operação:**
  - 🟢 **Particular (TPX):** Verde
  - 🔵 **Executivo (TPV):** Azul
  - 🔴 **Policial / Resgate (SAE/GOV):** Vermelho
  - 🟡 **Offshore / Plataforma (SAE):** Laranja
- **Mapeamento Interativo com Leaflet.js:**
  - Silhueta HD de helicóptero com orientação dinâmica pelo *heading* (direção do voo).
  - Traçado completo e contínuo de rota (Rastro Percorrido desde a Decolagem + Projeção de Destino).
  - Câmera fixa ao selecionar aeronaves (sem alterar o zoom ou navegação do usuário).
- **Consumo Inteligente de Dados (ADS-B / Standby):** Integração com API OpenSky Network e simulação de vetores de deslocamento contínuo em tempo real.

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3, Flask, Requests, Psycopg2.
- **Frontend:** HTML5, CSS3 Grid/Flexbox, JavaScript ES6, Leaflet.js.
- **Banco de Dados:** PostgreSQL (Render / Supabase).
- **Deploy & Infraestrutura:** Render, GitHub, Gunicorn.

## 🚀 Como Executar Localmente

1. **Ativar o ambiente virtual e instalar dependências:**
   ```bash
   source venv/bin/activate
   pip install flask requests psycopg2-binary gunicorn

