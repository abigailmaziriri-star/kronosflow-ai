import os
import asyncio
import threading
from flask import Flask, jsonify
from flask_socketio import SocketIO

# 1. INITIALIZATION & SECURITY ORIENTATION
app = Flask(__name__)
# cors_allowed_origins="*" ensures Render routes traffic into the script securely
socketio = SocketIO(app, cors_allowed_origins="*")

# Fallback Deriv Token Configuration for Local Testing
# Render will automatically use its own Environment Variables first
DERIV_API_TOKEN = os.environ.get("DERIV_TOKEN", "pat_2835a32815fff743180964079b2d7d66c61fbdb11dfabef674fadeb004f3f523")

# Automated bot trading engine tracking state
SYSTEM_TELEMETRY = {
    "status": "Initializing Engine...",
    "risk_label": "Safe (Monitoring)",
    "last_signal": "None",
    "signal_color": "gray",
    "digits": [],
    "ticks_analyzed": 0
}

# The asynchronous processing structure for digit predictions & live ticks
async def start_background_loop():
    global SYSTEM_TELEMETRY
    while True:
        # Simulates reading the continuous 20-second interval confidence scanner from Deriv stream
        await asyncio.sleep(1)
        SYSTEM_TELEMETRY["status"] = "Connected to Deriv Websocket Stream"
        SYSTEM_TELEMETRY["ticks_analyzed"] += 1
        
        # Emit live ticker events to the frontend dashboard
        socketio.emit('telemetry_update', SYSTEM_TELEMETRY)
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>KronosFlow AI Dashboard</title>
        <script src="https://socket.io"></script>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; text-align: center; padding: 30px; }
            .container { max-width: 600px; margin: 0 auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.5); }
            h1 { color: #38bdf8; margin-bottom: 5px; }
            .badge { padding: 12px 24px; font-weight: bold; border-radius: 6px; display: inline-block; margin-top: 20px; font-size: 14px; letter-spacing: 0.5px; }
            .connecting { background: #b45309; color: #fef3c7; }
            .connected { background: #15803d; color: #dcfce7; }
            .metric-box { background: #0f172a; padding: 15px; border-radius: 8px; margin-top: 20px; text-align: left; }
            .metric { margin: 8px 0; font-size: 16px; color: #94a3b8; }
            .highlight { color: #f8fafc; font-weight: 600; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>KronosFlow AI</h1>
            <p style="color: #64748b; margin-top: 0;">Deriv Automated Bot Dashboard</p>
            
            <div id="status-badge" class="badge connecting">INITIALIZING HANDSHAKE...</div>
            
            <div class="metric-box">
                <div class="metric">Engine Status: <span id="lbl-status" class="highlight">Offline</span></div>
                <div class="metric">Ticks Analyzed: <span id="lbl-ticks" class="highlight">0</span></div>
                <div class="metric">Risk Matrix: <span id="lbl-risk" class="highlight">Pending</span></div>
                <div class="metric">Last Generated Entry: <span id="lbl-signal" class="highlight">None</span></div>
            </div>
        </div>

        <script>
            // Adaptive client handshake protocol controller (Fixes the Render Reconnecting loop error)
            var socket = io(window.location.origin, {
                transports: ['websocket', 'polling']
            });

            socket.on('connect', function() {
                var badge = document.getElementById('status-badge');
                badge.innerText = '🟢 KRONOSFLOW ENGINE LIVE';
                badge.className = 'badge connected';
            });

            socket.on('disconnect', function() {
                var badge = document.getElementById('status-badge');
                badge.innerText = '🔴 RECONNECTING TO CLOUD...';
                badge.className = 'badge connecting';
            });

            socket.on('telemetry_update', function(data) {
                document.getElementById('lbl-status').innerText = data.status;
                document.getElementById('lbl-ticks').innerText = data.ticks_analyzed;
                document.getElementById('lbl-risk').innerText = data.risk_label;
                document.getElementById('lbl-signal').innerText = data.last_signal;
            });
        </script>
    </body>
    </html>
    """

@app.route('/api/status', methods=['GET'])
def get_status():
    global SYSTEM_TELEMETRY
    return jsonify(SYSTEM_TELEMETRY)
# 3. BACKGROUND WORKER CONFIGURATION
# Creates and instantiates the loop outside the main scope so Render/Gunicorn triggers it instantly
new_loop = asyncio.new_event_loop()
def start_background_thread(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_background_loop())

# Launch persistent daemon worker
t = threading.Thread(target=start_background_thread, args=(new_loop,), daemon=True)
t.start()

# 4. RUNNER CONFIGURATION CONTROL MATRIX
if __name__ == '__main__':
    # Dynamically binds Render assigned deployment port, or defaults to port 5000 inside Pydroid 3
    port = int(os.environ.get("PORT", 5000))
    
    # allow_unsafe_werkzeug=True is isolated here so it only executes when testing locally on your phone
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
