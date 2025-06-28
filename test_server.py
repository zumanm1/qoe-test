#!/usr/bin/env python3
import os
import sys
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Simple test Flask app without SocketIO complexity
app = Flask(__name__)
app.secret_key = 'test-secret-key'

# Mock user for testing
TEST_USER = {'username': 'admin', 'password': 'Admin123!'}

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == TEST_USER['username'] and password == TEST_USER['password']:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/dashboard/')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template_string(DASHBOARD_TEMPLATE)

@app.route('/simulation/')
def simulation():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template_string(SIMULATION_TEMPLATE)

@app.route('/reports/')
def reports():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template_string(REPORTS_TEMPLATE)

@app.route('/api/kpi/latest')
def api_kpi_latest():
    return jsonify({
        'kpis': [
            {'name': 'Download Speed', 'value': 85.5, 'unit': 'Mbps'},
            {'name': 'Upload Speed', 'value': 42.3, 'unit': 'Mbps'},
            {'name': 'Latency', 'value': 23, 'unit': 'ms'},
            {'name': 'Packet Loss', 'value': 0.1, 'unit': '%'}
        ]
    })

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

# Template strings (simplified versions)
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>QoE Tool - Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h4>Login to QoE Tool</h4>
                    </div>
                    <div class="card-body">
                        {% with messages = get_flashed_messages() %}
                            {% if messages %}
                                <div class="alert alert-danger">
                                    {% for message in messages %}
                                        {{ message }}
                                    {% endfor %}
                                </div>
                            {% endif %}
                        {% endwith %}
                        <form method="POST">
                            <div class="mb-3">
                                <label for="username" class="form-label">Username</label>
                                <input type="text" class="form-control" id="username" name="username" required>
                            </div>
                            <div class="mb-3">
                                <label for="password" class="form-label">Password</label>
                                <input type="password" class="form-control" id="password" name="password" required>
                            </div>
                            <button type="submit" class="btn btn-primary">Login</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>QoE Tool - Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="#">QoE Tool</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/dashboard/">Dashboard</a>
                <a class="nav-link" href="/simulation/">Simulation</a>
                <a class="nav-link" href="/reports/">Reports</a>
                <a class="nav-link" href="/logout">Logout</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        <h1>Dashboard</h1>
        <div class="row">
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Download Speed</h5>
                        <p class="card-text"><span id="download-speed">85.5</span> Mbps</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Upload Speed</h5>
                        <p class="card-text"><span id="upload-speed">42.3</span> Mbps</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Latency</h5>
                        <p class="card-text"><span id="latency">23</span> ms</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Packet Loss</h5>
                        <p class="card-text"><span id="packet-loss">0.1</span> %</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-12">
                <button id="refresh-btn" class="btn btn-primary">Refresh KPI Data</button>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-6">
                <canvas id="speedChart"></canvas>
            </div>
            <div class="col-md-6">
                <canvas id="latencyChart"></canvas>
            </div>
        </div>
    </div>
    
    <script>
        // Initialize charts
        const speedCtx = document.getElementById('speedChart').getContext('2d');
        const speedChart = new Chart(speedCtx, {
            type: 'line',
            data: {
                labels: ['1h ago', '45m ago', '30m ago', '15m ago', 'Now'],
                datasets: [{
                    label: 'Download Speed (Mbps)',
                    data: [82.1, 84.5, 83.2, 86.1, 85.5],
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            }
        });
        
        const latencyCtx = document.getElementById('latencyChart').getContext('2d');
        const latencyChart = new Chart(latencyCtx, {
            type: 'line',
            data: {
                labels: ['1h ago', '45m ago', '30m ago', '15m ago', 'Now'],
                datasets: [{
                    label: 'Latency (ms)',
                    data: [25, 22, 24, 21, 23],
                    borderColor: 'rgb(255, 99, 132)',
                    tension: 0.1
                }]
            }
        });
        
        // Refresh button functionality
        document.getElementById('refresh-btn').addEventListener('click', function() {
            fetch('/api/kpi/latest')
                .then(response => response.json())
                .then(data => {
                    console.log('KPI data refreshed:', data);
                    // Update KPI values
                    data.kpis.forEach(kpi => {
                        const element = document.getElementById(kpi.name.toLowerCase().replace(' ', '-'));
                        if (element) {
                            element.textContent = kpi.value;
                        }
                    });
                })
                .catch(error => console.error('Error:', error));
        });
    </script>
</body>
</html>
'''

SIMULATION_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>QoE Tool - Simulation</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="#">QoE Tool</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/dashboard/">Dashboard</a>
                <a class="nav-link" href="/simulation/">Simulation</a>
                <a class="nav-link" href="/reports/">Reports</a>
                <a class="nav-link" href="/logout">Logout</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        <h1>QoE Simulation</h1>
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Simulation Parameters</h5>
                    </div>
                    <div class="card-body">
                        <form id="simulation-form">
                            <div class="mb-3">
                                <label for="ran-factor" class="form-label">RAN Factor</label>
                                <input type="range" class="form-range" id="ran-factor" min="0" max="100" value="50">
                                <span id="ran-value">50</span>
                            </div>
                            <div class="mb-3">
                                <label for="transport-factor" class="form-label">Transport Factor</label>
                                <input type="range" class="form-range" id="transport-factor" min="0" max="100" value="50">
                                <span id="transport-value">50</span>
                            </div>
                            <div class="mb-3">
                                <label for="core-factor" class="form-label">Core Factor</label>
                                <input type="range" class="form-range" id="core-factor" min="0" max="100" value="50">
                                <span id="core-value">50</span>
                            </div>
                            <button type="button" id="run-simulation" class="btn btn-success">Run Simulation</button>
                        </form>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Simulation Results</h5>
                    </div>
                    <div class="card-body">
                        <div id="simulation-results">
                            <p>Click "Run Simulation" to see results</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Update range values
        document.getElementById('ran-factor').addEventListener('input', function() {
            document.getElementById('ran-value').textContent = this.value;
        });
        document.getElementById('transport-factor').addEventListener('input', function() {
            document.getElementById('transport-value').textContent = this.value;
        });
        document.getElementById('core-factor').addEventListener('input', function() {
            document.getElementById('core-value').textContent = this.value;
        });
        
        // Run simulation
        document.getElementById('run-simulation').addEventListener('click', function() {
            const ranFactor = document.getElementById('ran-factor').value;
            const transportFactor = document.getElementById('transport-factor').value;
            const coreFactor = document.getElementById('core-factor').value;
            
            // Mock simulation results
            const qoeScore = Math.max(0, Math.min(100, 
                (parseInt(ranFactor) + parseInt(transportFactor) + parseInt(coreFactor)) / 3 + Math.random() * 20 - 10
            )).toFixed(1);
            
            document.getElementById('simulation-results').innerHTML = `
                <h6>QoE Score: ${qoeScore}/100</h6>
                <ul>
                    <li>RAN Impact: ${ranFactor}%</li>
                    <li>Transport Impact: ${transportFactor}%</li>
                    <li>Core Impact: ${coreFactor}%</li>
                </ul>
                <p class="text-${qoeScore > 70 ? 'success' : qoeScore > 50 ? 'warning' : 'danger'}">
                    Quality Level: ${qoeScore > 70 ? 'Good' : qoeScore > 50 ? 'Fair' : 'Poor'}
                </p>
            `;
        });
    </script>
</body>
</html>
'''

REPORTS_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>QoE Tool - Reports</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="#">QoE Tool</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/dashboard/">Dashboard</a>
                <a class="nav-link" href="/simulation/">Simulation</a>
                <a class="nav-link" href="/reports/">Reports</a>
                <a class="nav-link" href="/logout">Logout</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        <h1>Reports</h1>
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h5>Recent Reports</h5>
                    </div>
                    <div class="card-body">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Report Name</th>
                                    <th>Date</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>Daily QoE Summary</td>
                                    <td>2025-06-28</td>
                                    <td><span class="badge bg-success">Ready</span></td>
                                    <td><button class="btn btn-sm btn-primary">Download</button></td>
                                </tr>
                                <tr>
                                    <td>Weekly Network Analysis</td>
                                    <td>2025-06-27</td>
                                    <td><span class="badge bg-success">Ready</span></td>
                                    <td><button class="btn btn-sm btn-primary">Download</button></td>
                                </tr>
                                <tr>
                                    <td>Monthly Trends Report</td>
                                    <td>2025-06-01</td>
                                    <td><span class="badge bg-warning">Processing</span></td>
                                    <td><button class="btn btn-sm btn-secondary" disabled>Processing...</button></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    from flask import render_template_string
    app.run(host='127.0.0.1', port=3000, debug=True, threaded=True)
