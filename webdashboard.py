"""
Web Dashboard for Ransomware Detection System
Real-time monitoring and visualization interface
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading
import time
import json
from datetime import datetime
from pathlib import Path
from ransomware_detector import RansomwareDetector, FileSystemMonitor
from watchdog.observers import Observer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ransomware-detection-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global detector instance
detector = None
observer = None
monitoring_active = False
watch_path = "./test_ransomware"


class WebDashboardMonitor(FileSystemMonitor):
    """Extended monitor that sends updates to web dashboard"""
    
    def _periodic_check(self):
        """Override to send real-time updates"""
        current_time = time.time()
        if current_time - self.last_check > self.check_interval:
            self.last_check = current_time
            
            # Analyze system behavior
            analysis = self.detector.analyze_system_behavior()
            
            # Send update to dashboard
            socketio.emit('system_update', {
                'risk_score': analysis['risk_score'],
                'is_attack': analysis['is_attack'],
                'indicators': analysis['indicators'],
                'timestamp': analysis['timestamp']
            })
            
            if analysis['is_attack']:
                self.detector.trigger_alert(analysis)
                socketio.emit('alert', analysis)
    
    def on_modified(self, event):
        super().on_modified(event)
        if not event.is_directory:
            # Analyze the file
            file_result = self.detector.analyze_file(event.src_path)
            time.sleep(0.1)
            system_result = self.detector.analyze_system_behavior()

            combined_risk = max(file_result['risk_score'], system_result['risk_score'])

            result = {
    **file_result,
    'risk_score': combined_risk,
    'is_suspicious': combined_risk > 25,
    'indicators': file_result.get('indicators', []) + system_result.get('indicators', [])
}
            
            socketio.emit('file_event', {
                'type': 'modified',
                'path': event.src_path,
                'entropy': result.get('entropy', 0),
                'risk_score': combined_risk,
                'is_suspicious': combined_risk > 25,
                'timestamp': datetime.now().isoformat()
            })
            
            # Send alert if suspicious
            if combined_risk >= 90:
                socketio.emit('alert', result)
    
    def on_created(self, event):
        super().on_created(event)
        if not event.is_directory:
            # Analyze the file
            file_result = self.detector.analyze_file(event.src_path)
            time.sleep(0.1)
            system_result = self.detector.analyze_system_behavior()

            combined_risk = max(file_result['risk_score'], system_result['risk_score'])
            

            result = {
    **file_result,
    'risk_score': combined_risk,
    'is_suspicious': combined_risk > 25,
    'indicators': file_result.get('indicators', []) + system_result.get('indicators', [])
}
            
            socketio.emit('file_event', {
                'type': 'created',
                'path': event.src_path,
                'entropy': result.get('entropy', 0),
                'risk_score': combined_risk,
                'is_suspicious': combined_risk > 25,
                'timestamp': datetime.now().isoformat()
            })
            
            # Send alert if suspicious
            if combined_risk >= 90:
             socketio.emit('alert', result)
            


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/status')
def get_status():
    """Get current system status"""
    global detector, monitoring_active
    
    if not detector:
        return jsonify({'error': 'Detector not initialized'}), 400
    
    analysis = detector.analyze_system_behavior()
    
    return jsonify({
        'monitoring_active': monitoring_active,
        'watch_path': watch_path,
        'risk_score': analysis['risk_score'],
        'is_attack': analysis['is_attack'],
        'indicators': analysis['indicators'],
        'alert_count': len(detector.alerts),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/analyze_file', methods=['POST'])
def analyze_file():
    """Analyze a specific file"""
    global detector
    
    file_path = request.json.get('file_path')
    if not file_path:
        return jsonify({'error': 'File path required'}), 400
    
    file_result = detector.analyze_file(file_path)
    system_result = detector.analyze_system_behavior()

# 🔥 COMBINE BOTH
    combined_risk = max(file_result['risk_score'], system_result['risk_score'])

    result = {
    **file_result,
    'risk_score': combined_risk,
    'system_risk': system_result['risk_score'],
    'indicators': file_result.get('indicators', []) + system_result.get('indicators', [])
    }
    return jsonify(result)


@app.route('/api/scan_directory', methods=['POST'])
def scan_directory():
    """Scan all files in a directory and analyze them"""
    global detector
    
    import os
    
    dir_path = request.json.get('directory', './test_ransomware')
    
    if not os.path.exists(dir_path):
        return jsonify({'error': f'Directory not found: {dir_path}'}), 400
    
    results = []
    suspicious_count = 0
    
    # Scan all files in directory
    for root, dirs, files in os.walk(dir_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            try:
                file_result = detector.analyze_file(file_path)
                system_result = detector.analyze_system_behavior()

# 🔥 COMBINE BOTH
                combined_risk = max(file_result['risk_score'], system_result['risk_score'])

                result = {
    **file_result,
    'risk_score': combined_risk,
    'system_risk': system_result['risk_score'],
    'is_suspicious': combined_risk > 25,
    'indicators': file_result.get('indicators', []) + system_result.get('indicators', [])
}
                results.append(result)
                
                # Emit to dashboard in real-time
                socketio.emit('file_event', {
                    'type': 'scanned',
                    'path': file_path,
                    'entropy': result.get('entropy', 0),
                    'risk_score': combined_risk,
                    'is_suspicious': combined_risk > 25,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Send alert if suspicious
                if combined_risk > 25:
                
                 suspicious_count += 1
                socketio.emit('alert', result)
                    
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
    
    return jsonify({
        'total_files': len(results),
        'suspicious_files': suspicious_count,
        'results': results
    })


@app.route('/api/alerts')
def get_alerts():
    """Get all alerts"""
    global detector
    
    return jsonify({
        'alerts': detector.alerts[-50:],  # Last 50 alerts
        'count': len(detector.alerts)
    })


@app.route('/api/start_monitoring', methods=['POST'])
def start_monitoring():
    """Start file system monitoring"""
    global detector, observer, monitoring_active, watch_path
    
    new_path = request.json.get('path', watch_path)
    
    # Stop existing monitoring
    if observer:
        observer.stop()
        observer.join()
    
    # Initialize detector if needed
    if not detector:
        detector = RansomwareDetector()
    
    # Setup new monitoring
    watch_path = new_path
    Path(watch_path).mkdir(parents=True, exist_ok=True)
    
    event_handler = WebDashboardMonitor(detector, watch_path)
    observer = Observer()
    observer.schedule(event_handler, watch_path, recursive=True)
    observer.start()
    
    monitoring_active = True
    
    return jsonify({
        'status': 'Monitoring started',
        'path': watch_path
    })


@app.route('/api/stop_monitoring', methods=['POST'])
def stop_monitoring():
    """Stop file system monitoring"""
    global observer, monitoring_active
    
    if observer:
        observer.stop()
        observer.join()
        monitoring_active = False
        
        return jsonify({'status': 'Monitoring stopped'})
    
    return jsonify({'error': 'No active monitoring'}), 400


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connection_response', {'status': 'Connected to ransomware detection system'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')


@socketio.on('request_update')
def handle_update_request():
    """Handle manual update request"""
    global detector
    
    if detector:
        analysis = detector.analyze_system_behavior()
        emit('system_update', analysis)


def create_html_template():
    """Create HTML template for dashboard"""
    template_dir = Path('templates')
    template_dir.mkdir(exist_ok=True)
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ransomware Detection Dashboard</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #fff;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .subtitle {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .card h2 {
            margin-bottom: 15px;
            font-size: 1.3em;
            border-bottom: 2px solid rgba(255,255,255,0.2);
            padding-bottom: 10px;
        }
        
        .risk-meter {
            position: relative;
            height: 150px;
            margin: 20px 0;
        }
        
        .risk-score {
            font-size: 4em;
            font-weight: bold;
            text-align: center;
            line-height: 150px;
        }
        
        .risk-low { color: #4ade80; }
        .risk-medium { color: #fbbf24; }
        .risk-high { color: #f87171; }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        .status-safe { background: #4ade80; }
        .status-warning { background: #fbbf24; }
        .status-danger { background: #f87171; }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .indicator-list {
            list-style: none;
            margin: 15px 0;
        }
        
        .indicator-list li {
            padding: 10px;
            margin: 8px 0;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            border-left: 3px solid #fbbf24;
        }
        
        .alert-item {
            padding: 15px;
            margin: 10px 0;
            background: rgba(248, 113, 113, 0.2);
            border-radius: 8px;
            border-left: 4px solid #f87171;
        }
        
        .alert-time {
            font-size: 0.85em;
            opacity: 0.8;
            margin-top: 5px;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        button {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 600;
        }
        
        .btn-primary {
            background: #3b82f6;
            color: white;
        }
        
        .btn-danger {
            background: #ef4444;
            color: white;
        }
        
        .btn-success {
            background: #10b981;
            color: white;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-top: 15px;
        }
        
        .stat-item {
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 0.9em;
            opacity: 0.8;
        }
        
        .event-log {
            max-height: 300px;
            overflow-y: auto;
            margin-top: 15px;
        }
        
        .event-item {
            padding: 8px;
            margin: 5px 0;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 5px;
            font-size: 0.9em;
        }
        
        .timestamp {
            color: #94a3b8;
            font-size: 0.85em;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🛡️ AI Ransomware Detection System</h1>
            <p class="subtitle">Real-time File Entropy & Access Pattern Intelligence</p>
        </header>
        
        <div class="dashboard">
            <!-- System Status Card -->
            <div class="card">
                <h2>System Status</h2>
                <div style="margin: 20px 0;">
                    <span class="status-indicator status-safe" id="statusIndicator"></span>
                    <span id="statusText">Initializing...</span>
                </div>
                
                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-value" id="alertCount">0</div>
                        <div class="stat-label">Alerts</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="fileEvents">0</div>
                        <div class="stat-label">File Events</div>
                    </div>
                </div>
                
                <div class="controls">
                    <button class="btn-success" onclick="startMonitoring()" id="startBtn">Start</button>
                    <button class="btn-danger" onclick="stopMonitoring()" id="stopBtn" disabled>Stop</button>
                </div>
                
                <div style="margin-top: 15px;">
                    <input type="text" id="scanPath" placeholder="./test_ransomware" 
                           style="padding: 10px; width: 60%; border-radius: 5px; border: none; margin-right: 5px;">
                    <button class="btn-success" onclick="scanDirectory()" style="width: 35%;">Scan Folder</button>
                </div>
            </div>
            
            <!-- Risk Score Card -->
            <div class="card">
                <h2>Risk Assessment</h2>
                <div class="risk-meter">
                    <div class="risk-score risk-low" id="riskScore">0</div>
                </div>
                <div style="text-align: center; margin-top: -10px;">
                    <strong id="riskLabel">System Safe</strong>
                </div>
            </div>
            
            <!-- Threat Indicators Card -->
            <div class="card">
                <h2>Threat Indicators</h2>
                <ul class="indicator-list" id="indicatorList">
                    <li>No threats detected</li>
                </ul>
            </div>
        </div>
        
        <!-- Alerts Section -->
        <div class="card">
            <h2>🚨 Recent Alerts</h2>
            <div id="alertsList">
                <p style="opacity: 0.7;">No alerts</p>
            </div>
        </div>
        
        <!-- Activity Log -->
        <div class="card">
            <h2>📊 Activity Log</h2>
            <div class="event-log" id="eventLog">
                <div class="event-item">System initialized</div>
            </div>
        </div>
    </div>
    
    <script>
        const socket = io();
        let fileEventCount = 0;
        let alertCount = 0;
        
        // Socket event handlers
        socket.on('connect', () => {
            console.log('Connected to server');
            addEventLog('Connected to detection system');
            updateStatus();
        });
        
        socket.on('system_update', (data) => {
            updateRiskScore(data.risk_score);
            updateIndicators(data.indicators);
            
            if (data.is_attack) {
                updateStatusIndicator('danger', 'RANSOMWARE DETECTED!');
            }
        });
        
        socket.on('alert', (data) => {
            addAlert(data);
            alertCount++;
            document.getElementById('alertCount').textContent = alertCount;
        });
        
        socket.on('file_event', (data) => {
            fileEventCount++;
            document.getElementById('fileEvents').textContent = fileEventCount;
            
            const fileName = data.path.split('/').pop();
            const entropy = data.entropy !== undefined ? data.entropy.toFixed(2) : 'N/A';
            const riskScore = data.risk_score !== undefined ? data.risk_score : 'N/A';
            const isSuspicious = data.is_suspicious ? '🚨' : '✅';
            
            addEventLog(`${isSuspicious} ${data.type.toUpperCase()}: ${fileName} (Entropy: ${entropy}, Risk: ${riskScore})`);
            
            // Update risk score if available
            if (data.risk_score !== undefined) {
                updateRiskScore(data.risk_score);
            }
        });
        
        // Update functions
        function updateRiskScore(score) {
            const scoreElement = document.getElementById('riskScore');
            const labelElement = document.getElementById('riskLabel');
            
            scoreElement.textContent = Math.round(score);
            
            // Update color and label
            scoreElement.className = 'risk-score';
            if (score < 30) {
                scoreElement.classList.add('risk-low');
                labelElement.textContent = 'System Safe';
                updateStatusIndicator('safe', 'Monitoring Active');
            } else if (score < 70) {
                scoreElement.classList.add('risk-medium');
                labelElement.textContent = 'Elevated Risk';
                updateStatusIndicator('warning', 'Suspicious Activity');
            } else {
                scoreElement.classList.add('risk-high');
                labelElement.textContent = 'Critical Threat';
                updateStatusIndicator('danger', 'RANSOMWARE DETECTED!');
            }
        }
        
        function updateIndicators(indicators) {
            const list = document.getElementById('indicatorList');
            
            if (indicators.length === 0) {
                list.innerHTML = '<li>No threats detected</li>';
            } else {
                list.innerHTML = indicators.map(ind => `<li>⚠️ ${ind}</li>`).join('');
            }
        }
        
        function updateStatusIndicator(status, text) {
            const indicator = document.getElementById('statusIndicator');
            const statusText = document.getElementById('statusText');
            
            indicator.className = 'status-indicator status-' + status;
            statusText.textContent = text;
        }
        
        function addAlert(alert) {
            const alertsList = document.getElementById('alertsList');
            
            const alertHtml = `
                <div class="alert-item">
                    <strong>🚨 Risk Score: ${alert.risk_score}</strong>
                    <ul style="margin: 10px 0 10px 20px;">
                        ${alert.indicators.map(ind => `<li>${ind}</li>`).join('')}
                    </ul>
                    <div class="alert-time">${new Date(alert.timestamp).toLocaleString()}</div>
                </div>
            `;
            
            if (alertsList.querySelector('p')) {
                alertsList.innerHTML = '';
            }
            
            alertsList.insertAdjacentHTML('afterbegin', alertHtml);
        }
        
        function addEventLog(message) {
            const log = document.getElementById('eventLog');
            const timestamp = new Date().toLocaleTimeString();
            
            const eventHtml = `
                <div class="event-item">
                    <span class="timestamp">[${timestamp}]</span> ${message}
                </div>
            `;
            
            log.insertAdjacentHTML('afterbegin', eventHtml);
            
            // Keep only last 50 events
            while (log.children.length > 50) {
                log.removeChild(log.lastChild);
            }
        }
        
        // Control functions
        async function startMonitoring() {
            try {
                const response = await fetch('/api/start_monitoring', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({path: './monitored_directory'})
                });
                
                const data = await response.json();
                
                document.getElementById('startBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
                
                addEventLog('Monitoring started: ' + data.path);
                updateStatusIndicator('safe', 'Monitoring Active');
            } catch (error) {
                console.error('Error starting monitoring:', error);
            }
        }
        
        async function stopMonitoring() {
            try {
                await fetch('/api/stop_monitoring', {method: 'POST'});
                
                document.getElementById('startBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
                
                addEventLog('Monitoring stopped');
                updateStatusIndicator('safe', 'Monitoring Inactive');
            } catch (error) {
                console.error('Error stopping monitoring:', error);
            }
        }
        
        async function scanDirectory() {
            const path = document.getElementById('scanPath').value || './test_ransomware';
            
            addEventLog(`Scanning directory: ${path}...`);
            
            try {
                const response = await fetch('/api/scan_directory', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({directory: path})
                });
                
                const data = await response.json();
                
                if (data.error) {
                    addEventLog(`❌ Error: ${data.error}`);
                } else {
                    addEventLog(`✓ Scan complete: ${data.total_files} files analyzed, ${data.suspicious_files} suspicious`);
                }
            } catch (error) {
                console.error('Error scanning directory:', error);
                addEventLog('❌ Error scanning directory');
            }
        }
        
        async function updateStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                if (data.monitoring_active) {
                    document.getElementById('startBtn').disabled = true;
                    document.getElementById('stopBtn').disabled = false;
                    updateStatusIndicator('safe', 'Monitoring Active');
                }
                
                alertCount = data.alert_count;
                document.getElementById('alertCount').textContent = alertCount;
            } catch (error) {
                console.error('Error fetching status:', error);
            }
        }
        
        // Auto-refresh every 5 seconds
        setInterval(() => {
            socket.emit('request_update');
        }, 5000);
    </script>
</body>
</html>"""
    
    with open(template_dir / 'dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✓ Dashboard template created")


def run_dashboard(host='127.0.0.1', port=5000):
    """Run the web dashboard"""
    global detector
    
    
    # create_html_template()
    
    # Initialize detector
    detector = RansomwareDetector()
    
    print(f"\n{'='*70}")
    print("Starting Ransomware Detection Web Dashboard")
    print(f"{'='*70}")
    print(f"\nDashboard URL: http://{host}:{port}")
    print("Press Ctrl+C to stop\n")
    
    socketio.run(app, host=host, port=port, debug=False)


if __name__ == "__main__":
    run_dashboard()             