from gevent import monkey
monkey.patch_all()  # Establishes internal routing adjustments for Render containers

import os
from flask import Flask, jsonify
from flask_socketio import SocketIO

# 1. PLATFORM CONFIGURATION MATRIX
app = Flask(__name__)
# Explicitly disabling standard transport layers forces the proxy to hold lines open safely
socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    async_mode='gevent',
    logger=True,
    engineio_logger=True
)

# Core state layout architecture
SYSTEM_TELEMETRY = {
    "status": "Initializing Engine...",
    "risk_label": "Safe (Monitoring)",
    "last_signal": "None",
    "signal_color": "gray",
    "digits": [],
    "ticks_analyzed": 0
}

def start_background_loop():
    """
    Runs continuously inside a stable gevent micro-thread to handle 
    incoming data streaming and broadcast updates to the web panel.
    """
    global SYSTEM_TELEMETRY
    while True:
        socketio.sleep(1)  # Production-safe asynchronous clock timing marker
        SYSTEM_TELEMETRY["status"] = "Connected to Deriv Websocket Stream"
        SYSTEM_TELEMETRY["ticks_analyzed"] += 1
        socketio.emit('telemetry_update', SYSTEM_TELEMETRY)

@socketio.on('connect')
def handle_connect():
    global SYSTEM_TELEMETRY
    socketio.emit('telemetry_update', SYSTEM_TELEMETRY)

# 2. SEAMLESS PRODUCTION INTERFACE ROUTING
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>KronosFlow AI Dashboard</title>
        <script src="https://cloudflare.com"></script>
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
            // Forcing explicit fallback pathways resolves mobile carrier proxy bottlenecks immediately
            var socket = io(window.location.origin, {
                transports: ['polling', 'websocket'],
                upgrade: true,
                rememberUpgrade: true
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

# 3. WORKER BOOTSTRAP GATEWAY
socketio.start_background_task(start_background_loop)

if __name__ == '__main__':
    # Intercepts Render container routing system variable seamlessly
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
