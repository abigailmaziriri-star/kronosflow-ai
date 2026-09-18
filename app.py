import os
import json
import time
import random
import threading
import asyncio
from flask import Flask, render_template_string, jsonify
import websockets

app = Flask(__name__)

# --- GLOBAL THREAD-SAFE MULTI-MARKET MEMORY BUFFERS ---
ALL_MARKETS = {
    "1HZ10V": "Volatility 10 (1s)",
    "1HZ25V": "Volatility 25 (1s)",
    "1HZ50V": "Volatility 50 (1s)",
    "1HZ75V": "Volatility 75 (1s)",
    "1HZ100V": "Volatility 100 (1s)",
    "1HZ150V": "Volatility 150 (1s)",
    "1HZ250V": "Volatility 250 (1s)",
    "R_10": "Volatility 10",
    "R_25": "Volatility 25",
    "R_50": "Volatility 50",
    "R_75": "Volatility 75",
    "R_100": "Volatility 100"
}

SYSTEM_TELEMETRY = {
    "status": "INITIALIZING HANDSHAKE...",
    "balance": "0.00",
    "active_market": "1HZ100V",
    "risk_index": 0,
    "risk_label": "0% Stable",
    "target_profit": "20.00",
    "stop_loss": "-50.00",
    "max_ticks": 15,
    "last_signal": "SWEEPING ALL MARKETS FOR OPPORTUNITIES...",
    "signal_color": "#7c7c99",
    "digits": [],
    "ticks_analyzed": 0,
    "market_data": {}
}

for code, name in ALL_MARKETS.items():
    SYSTEM_TELEMETRY["market_data"][code] = {
        "name": name,
        "risk_index": 0,
        "risk_label": "0% Stable",
        "last_signal": "Awaiting Stream...",
        "signal_color": "#7c7c99",
        "digits": [],
        "ticks_analyzed": 0,
        "history": []
    }

APP_ID = "1089" 
API_TOKEN = "pat_2835a32815fff743180964079b2d7d66c61fbdb11dfabef674fadeb004f3f523"
async def live_deriv_quantum_engine():
    global SYSTEM_TELEMETRY
    url = f"wss://://derivws.com{APP_ID}"
    while True:
        try:
            SYSTEM_TELEMETRY["status"] = "📡 SCANNING ALL..."
            async with websockets.connect(url) as ws:
                await ws.send(json.dumps({"authorize": API_TOKEN}))
                auth_resp = json.loads(await ws.recv())
                if "error" in auth_resp:
                    SYSTEM_TELEMETRY["status"] = "🔴 AUTH FAILURE"
                    SYSTEM_TELEMETRY["last_signal"] = f"Token Denied: {auth_resp['error']['message']}"
                    return
                SYSTEM_TELEMETRY["balance"] = f"{float(auth_resp['authorize']['balance']):,.2f}"
                SYSTEM_TELEMETRY["status"] = "🟢 MATRIX ACTIVE"
                for market_code in ALL_MARKETS.keys():
                    await ws.send(json.dumps({"ticks": market_code, "subscribe": 1}))
                async for raw_message in ws:
                    message = json.loads(raw_message)
                    if "tick" not in message: continue
                    tick_data = message["tick"]
                    code = tick_data["symbol"]
                    quote = float(tick_data["quote"])
                    if code not in SYSTEM_TELEMETRY["market_data"]: continue
                    m_state = SYSTEM_TELEMETRY["market_data"][code]
                    m_state["history"].append(quote)
                    if len(m_state["history"]) > 200: m_state["history"].pop(0)
                    m_state["ticks_analyzed"] = len(m_state["history"])
                    digits_list = [int(str(p).split('.')[-1][-1]) for p in m_state["history"] if '.' in str(p)]
                    if digits_list:
                        freq_map = {d: digits_list.count(d) for d in range(6)}
                        m_state["digits"] = [round((freq_map[d] / len(digits_list)) * 100) for d in range(6)]
                    if len(m_state["history"]) >= 10:
                        diffs = [m_state["history"][i] - m_state["history"][i-1] for i in range(1, len(m_state["history"]))]
                        velocity = sum(diffs) / len(diffs)
                        variance = max(abs(d) for d in diffs)
                        risk_score = min(int(variance * 10000), 100)
                        m_state["risk_index"] = risk_score
                        if risk_score < 40 and abs(velocity) < 0.005:
                            m_state["risk_label"] = f"{risk_score}% - Safe Matrix"
                            m_state["last_signal"] = f"🟢 ACCUMULATOR ENTRY SIGNAL: Low volatility on {ALL_MARKETS[code]}."
                            m_state["signal_color"] = "#4caf50"
                        elif risk_score < 75:
                            m_state["risk_label"] = f"{risk_score}% - Minor Range Expansion"
                            m_state["last_signal"] = f"🟡 STANDBY: Momentum shifting on {ALL_MARKETS[code]}."
                            m_state["signal_color"] = "#ff9800"
                        else:
                            m_state["risk_label"] = f"{risk_score}% - CRITICAL COLLAPSE"
                            m_state["last_signal"] = f"🔴 ALERT: Knockout crash danger on {ALL_MARKETS[code]}! Sell contract."
                            m_state["signal_color"] = "#ff4a5a"
                    if code == SYSTEM_TELEMETRY["active_market"]:
                        SYSTEM_TELEMETRY["risk_index"] = m_state["risk_index"]
                        SYSTEM_TELEMETRY["risk_label"] = m_state["risk_label"]
                        SYSTEM_TELEMETRY["last_signal"] = m_state["last_signal"]
                        SYSTEM_TELEMETRY["signal_color"] = m_state["signal_color"]
                        SYSTEM_TELEMETRY["digits"] = m_state["digits"]
                        SYSTEM_TELEMETRY["ticks_analyzed"] = m_state["ticks_analyzed"]
        except Exception:
            SYSTEM_TELEMETRY["status"] = "🔴 RECONNECTING..."
            await asyncio.sleep(5)

def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(live_deriv_quantum_engine())
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KronosFlow AI Suite</title>
    <style>
        body { background-color: #111116; color: #ffffff; font-family: sans-serif; margin: 0; padding: 15px; padding-bottom: 50px; }
        .container { max-width: 500px; margin: 0 auto; }
        .header { border-bottom: 2px solid #ff4a5a; padding-bottom: 12px; margin-bottom: 20px; position: relative; }
        .header h1 { font-size: 20px; margin: 0; color: #ffffff; font-weight: bold; }
        .header h1 span { color: #ff4a5a; }
        .subtitle { font-size: 10px; color: #7c7c99; margin-top: 4px; font-weight: bold; }
        .status-badge { position: absolute; right: 0; top: 5px; background-color: #ff9800; color: #fff; padding: 4px 8px; font-size: 10px; border-radius: 4px; font-weight: bold; }
        .card { background-color: #1c1c24; border-radius: 8px; padding: 15px; margin-bottom: 15px; border: 1px solid #252533; }
        .card h2 { font-size: 12px; margin-top: 0; color: #b7b7cc; border-bottom: 1px solid #2d2d3d; padding-bottom: 5px; text-transform: uppercase; }
        .progress-bar { background-color: #2d2d3d; border-radius: 4px; height: 12px; width: 100%; position: relative; margin-top: 5px; overflow: hidden; }
        .progress-fill { background: linear-gradient(90deg, #4caf50, #ff9800, #ff4a5a); height: 100%; width: 0%; transition: width 0.4s ease; }
        .digit-bar { background-color: #ff4a5a; height: 100%; width: 0%; transition: width 0.4s ease; }
        .input-group { display: flex; justify-content: space-between; margin-top: 8px; font-size: 13px; align-items: center; }
        .input-group select, .input-group input { background-color: #111116; border: 1px solid #2d2d3d; color: #fff; padding: 6px; width: 160px; border-radius: 4px; }
        .input-group input { width: 80px; text-align: center; }
        .signal-box { border-left: 4px solid #7c7c99; padding-left: 10px; margin: 10px 0; }
        .signal-title { font-weight: bold; font-size: 13px; }
        .btn { background-color: #ff4a5a; color: #fff; border: none; padding: 14px; width: 100%; border-radius: 6px; font-weight: bold; font-size: 14px; }
    </style>
    <script>
        async function switchMarketView(selectObject) {
            const marketCode = selectObject.value;
            await fetch('/api/switch_market/' + marketCode);
            updateTelemetry();
        }
        async function updateTelemetry() {
            try {
                const response = await fetch('/api/telemetry');
                const data = await response.json();
                document.getElementById('status-indicator').innerText = data.status;
                document.getElementById('balance-display').innerText = '$' + data.balance + ' USD';
                document.getElementById('risk-value').innerText = data.risk_label;
                document.getElementById('signal-text').innerText = data.last_signal;
                const selectedSelect = document.getElementById('market-selector');
                const selectedText = selectedSelect.options[selectedSelect.selectedIndex].text;
                document.getElementById('depth-counter').innerText = 'Asset: ' + selectedText + ' | Matrix Depth: ' + data.ticks_analyzed + ' Ticks';
                document.getElementById('gauge-fill').style.width = data.risk_index + '%';
                for (let i = 0; i <= 5; i++) {
                    document.getElementById('digit-val-' + i).innerText = (data.digits && data.digits[i] ? data.digits[i] : 0) + '%';
                    document.getElementById('digit-bar-' + i).style.width = (data.digits && data.digits[i] ? data.digits[i] : 0) + '%';
                }
                document.getElementById('signal-container').style.borderColor = data.signal_color;
                document.getElementById('signal-header').style.color = data.signal_color;
            } catch (err) { console.log(err); }
        }
        setInterval(updateTelemetry, 1000);
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>KRONOS<span>FLOW</span> AI</h1>
            <div class="subtitle">⚡ MULTI-MATRIX SIMULTANEOUS SCANNING // PRODUCTION UNIT</div>
            <div class="status-badge" id="status-indicator">CONNECTING...</div>
        </div>
        <div class="card">
            <h2>🌍 CHOOSE MONITORING STREAM VIEW</h2>
            <div class="input-group">
                <span>Select Target Index:</span>
                <select id="market-selector" onchange="switchMarketView(this)">
                    <option value="1HZ100V" selected>Volatility 100 (1s)</option>
                    <option value="1HZ10V">Volatility 10 (1s)</option>
                    <option value="1HZ25V">Volatility 25 (1s)</option>
                    <option value="1HZ50V">Volatility 50 (1s)</option>
                    <option value="1HZ75V">Volatility 75 (1s)</option>
                    <option value="1HZ150V">Volatility 150 (1s)</option>
                    <option value="1HZ250V">Volatility 250 (1s)</option>
                    <option value="R_10">Volatility 10</option>
                    <option value="R_25">Volatility 25</option>
                    <option value="R_50">Volatility 50</option>
                    <option value="R_75">Volatility 75</option>
                    <option value="R_100">Volatility 100</option>
                </select>
            </div>
        </div>
        <div class="card">
            <h2>🔐 DERIV CORE SYNC LINK</h2>
            <div class="input-group">
                <span>Account Operational Balance:</span>
                <span id="balance-display" style="font-weight: bold; color: #4caf50;">$0.00 USD</span>
            </div>
        </div>
        <div class="card">
            <h2>🛡️ RISK ASSURANCE CONTROLS</h2>
            <div class="input-group">
                <span>💥 CRASH INSURANCE RISK GAUGE:</span>
                <span id="risk-value" style="font-weight: bold; color: #ff9800;">Evaluating Matrix...</span>
            </div>
            <div class="progress-bar"><div class="progress-fill" id="gauge-fill"></div></div>
            <div class="input-group" style="margin-top: 15px;"><span>🎯 Session Target Profit:</span><input type="text" value="$20.00"></div>
            <div class="input-group"><span>🚨 Hard Maximum Stop Loss:</span><input type="text" value="-$50.00"></div>
            <div class="input-group"><span>🔢 Target Exit Ticks Limit:</span><input type="text" value="15"></div>
        </div>
        <div class="card">
            <h2>⚡ SELECTED MARKET LOGIC FEED</h2>
            <p id="depth-counter" style="font-size: 11px; color: #7c7c99; margin: 0;"></p>
            <div class="signal-box" id="signal-container">
                <div class="signal-title" id="signal-header">SYSTEM ENGINE STATE</div>
                <p id="signal-text" style="font-size: 12px; margin: 4px 0 0 0; color: #b7b7cc;">Processing matrix feeds...</p>
            </div>
        </div>
        <div class="card">
            <h2>📈 AI DIGIT PROBABILITY DISTRIBUTION MATRIX (0-5)</h2>
            <div class="input-group"><span>Digit 0:</span><span id="digit-val-0">0%</span></div>
            <div class="progress-bar" style="height:6px;"><div class="digit-bar" id="digit-bar-0"></div></div>
            <div class="input-group"><span>Digit 1:</span><span id="digit-val-1">0%</span></div>
            <div class="progress-bar" style="height:6px;"><div class="digit-bar" id="digit-bar-1"></div></div>
            <div class="input-group"><span>Digit 2:</span><span id="digit-val-2">0%</span></div>
            <div class="progress-bar" style="height:6px;"><div class="digit-bar" id="digit-bar-2"></div></div>
            <div class="input-group"><span>Digit 3:</span><span id="digit-val-3">0%</span></div>
            <div class="progress-bar" style="height:6px;"><div class="digit-bar" id="digit-bar-3"></div></div>
            <div class="input-group"><span>Digit 4:</span><span id="digit-val-4">0%</span></div>
            <div class="progress-bar" style="height:6px;"><div class="digit-bar" id="digit-bar-4"></div></div>
            <div class="input-group"><span>Digit 5:</span><span id="digit-val-5">0%</span></div>
            <div class="progress-bar" style="height:6px;"><div class="digit-bar" id="digit-bar-5"></div></div>
        </div>
        <button class="btn">INITIALIZE KRONOSFLOW RUN</button>
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard(): return HTML_LAYOUT

@app.route('/api/telemetry')
def get_telemetry(): return jsonify(SYSTEM_TELEMETRY)

@app.route('/api/switch_market/<market_code>')
def switch_market(market_code):
    global SYSTEM_TELEMETRY
    if market_code in ALL_MARKETS:
        SYSTEM_TELEMETRY["active_market"] = market_code
        m_state = SYSTEM_TELEMETRY["market_data"][market_code]
        SYSTEM_TELEMETRY["risk_index"] = m_state["risk_index"]
        SYSTEM_TELEMETRY["risk_label"] = m_state["risk_label"]
        SYSTEM_TELEMETRY["last_signal"] = m_state["last_signal"]
        SYSTEM_TELEMETRY["signal_color"] = m_state["signal_color"]
        SYSTEM_TELEMETRY["digits"] = m_state["digits"]
        SYSTEM_TELEMETRY["ticks_analyzed"] = m_state["ticks_analyzed"]
    return jsonify({"status": "Success"})

if __name__ == '__main__':
    new_loop = asyncio.new_event_loop()
    t = threading.Thread(target=start_background_loop, args=(new_loop,), daemon=True)
    t.start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
