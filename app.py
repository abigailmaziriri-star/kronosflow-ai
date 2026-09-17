import os
import json
import time
import random
import threading
import asyncio
from flask import Flask, jsonify

app = Flask(__name__)

# --- GLOBAL THREAD-SAFE STORAGE ENGINE ---
SYSTEM_TELEMETRY = {
    "status": "CONNECTING...",
    "balance": "1,245.50",
    "risk_index": 0,
    "risk_label": "0% Stable",
    "target_profit": "20.00",
    "stop_loss": "-50.00",
    "max_ticks": 15,
    "last_signal": "STANDBY - WAITING FOR PACKET STREAM...",
    "signal_color": "#7c7c99",
    "digits": [0, 0, 0, 0, 0, 0]
}

# --- BACKEND CORE QUANTUM DATA PUMP ---
async def deriv_websocket_mock_loop():
    global SYSTEM_TELEMETRY
    SYSTEM_TELEMETRY["status"] = "🟢 LIVE PIPELINE"
    while True:
        try:
            await asyncio.sleep(2)
            calculated_risk = random.randint(15, 92)
            mock_digits = [random.randint(10, 95) for _ in range(6)]
            if calculated_risk < 40:
                label = f"{calculated_risk}% - Low Volatility"
                signal = "🟢 OPEN ACCUMULATOR POSITION // Stable compression matrix detected."
                color = "#4caf50"
            elif calculated_risk < 72:
                label = f"{calculated_risk}% - Unstable Micro-Trend"
                signal = "🟡 HOLD POSITION // High frequency velocity shifts occurring."
                color = "#ff9800"
            else:
                label = f"{calculated_risk}% - CRITICAL COLLAPSE THREAT"
                signal = "🔴 EMERGENCY EXIT NOW // KronosFlow AI flags maximum risk."
                color = "#ff4a5a"
            SYSTEM_TELEMETRY["risk_index"] = calculated_risk
            SYSTEM_TELEMETRY["risk_label"] = label
            SYSTEM_TELEMETRY["last_signal"] = signal
            SYSTEM_TELEMETRY["signal_color"] = color
            SYSTEM_TELEMETRY["digits"] = mock_digits
        except Exception as e:
            SYSTEM_TELEMETRY["status"] = "🔴 API STALL"
            SYSTEM_TELEMETRY["last_signal"] = str(e)
            await asyncio.sleep(5)

def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(deriv_websocket_mock_loop())
# --- PERFECTED CLEAN WEB INTERFACE LAYOUT ---
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KronosFlow AI Dashboard</title>
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
        .progress-fill { background: linear-gradient(90deg, #4caf50, #ff9800, #ff4a5a); height: 100%; width: 0%; transition: width 0.5s ease-in-out; }
        .digit-bar { background-color: #ff4a5a; height: 100%; width: 0%; transition: width 0.4s ease; }
        .input-group { display: flex; justify-content: space-between; margin-top: 8px; font-size: 13px; align-items: center; }
        .input-group input { background-color: #111116; border: 1px solid #2d2d3d; color: #fff; padding: 6px; width: 80px; border-radius: 4px; text-align: center; }
        .form-input { background-color: #111116; border: 1px solid #2d2d3d; color: #fff; padding: 8px; width: 100%; border-radius: 4px; box-sizing: border-box; margin-bottom: 10px; font-size: 12px; }
        textarea.form-input { height: 60px; resize: none; }
        .signal-box { border-left: 4px solid #7c7c99; padding-left: 10px; margin: 10px 0; }
        .signal-title { font-weight: bold; font-size: 13px; }
        .btn { background-color: #ff4a5a; color: #fff; border: none; padding: 14px; width: 100%; border-radius: 6px; font-weight: bold; font-size: 14px; }
    </style>
    <script>
        async function updateTelemetry() {
            try {
                const response = await fetch('/api/telemetry');
                const data = await response.json();
                document.getElementById('status-indicator').innerText = data.status;
                document.getElementById('risk-value').innerText = data.risk_label;
                document.getElementById('signal-text').innerText = data.last_signal;
                document.getElementById('gauge-fill').style.width = data.risk_index + '%';
                for (let i = 0; i <= 5; i++) {
                    document.getElementById('digit-val-' + i).innerText = data.digits[i] + '%';
                    document.getElementById('digit-bar-' + i).style.width = data.digits[i] + '%';
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
            <div class="subtitle">⚡ MULTI-MATRIX ENGINE // UNRESTRICTED CORE PLATFORM</div>
            <div class="status-badge" id="status-indicator">CONNECTING...</div>
        </div>
        <div class="card">
            <h2>🔐 DERIV CORE SYNC LINK</h2>
            <div class="input-group">
                <span>Deriv API Account Token:</span>
                <input type="password" value="secret_token" style="width: 160px;">
            </div>
            <div class="input-group">
                <span>Account Operational Balance:</span>
                <span style="font-weight: bold; color: #4caf50;">$1,245.50 USD</span>
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
            <h2>⚡ LIVE STRATEGY FEED</h2>
            <div class="signal-box" id="signal-container">
                <div class="signal-title" id="signal-header">SYSTEM ENGINE STATE</div>
                <p id="signal-text" style="font-size: 12px; margin: 4px 0 0 0; color: #b7b7cc;">Awaiting connection...</p>
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
def dashboard():
    return HTML_LAYOUT

@app.route('/api/telemetry')
def get_telemetry():
    return jsonify(SYSTEM_TELEMETRY)

if __name__ == '__main__':
    new_loop = asyncio.new_event_loop()
    t = threading.Thread(target=start_background_loop, args=(new_loop,), daemon=True)
    t.start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
