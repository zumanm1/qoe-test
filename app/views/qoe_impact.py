from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
import math

qoe_impact_bp = Blueprint('qoe_impact', __name__)

@qoe_impact_bp.route('/qoe_impact_dashboard')
@login_required
def qoe_impact_dashboard():
    return render_template('feature04/qoe_impact.html', title='QoE Impact Dashboard')

@qoe_impact_bp.route('/api/qoe_impact/update', methods=['POST'])
@login_required
def update_qoe_impact():
    params = request.get_json()

    # --- 1. Get all parameters from frontend ---
    # Radio Access
    tx_power = int(params.get('txPowerSlider', 40))
    interference = params.get('interferenceLevelSwitch', False)
    # Transport
    link_capacity = int(params.get('linkCapacitySlider', 1000))
    high_jitter = params.get('latencyJitterSwitch', False)
    # Core
    mme_capacity = int(params.get('mmeCapacitySlider', 50000))
    congestion = params.get('congestionControlSwitch', False)
    # Packet Core
    qci = params.get('qciClassSelect', 'QCI 9')
    strict_pcc = params.get('policyControlSwitch', False)

    # --- 2. Calculate Domain-Specific Scores (0-100) ---
    # Radio Score
    radio_score = ((tx_power - 30) / (50 - 30)) * 100  # Normalize 30-50 dBm to 0-100
    if interference:
        radio_score *= 0.6  # 40% penalty for high interference

    # Transport Score
    transport_score = (math.log(link_capacity / 100) / math.log(10000 / 100)) * 100 # Log scale for capacity
    if high_jitter:
        transport_score *= 0.7 # 30% penalty for high jitter/latency

    # Core Score
    core_score = (mme_capacity / 100000) * 100
    if congestion:
        core_score *= 0.5 # 50% penalty for congestion

    # Packet Core Score
    qci_multipliers = {'QCI 1': 1.2, 'QCI 5': 1.1, 'QCI 9': 1.0}
    packet_core_score = 80 * qci_multipliers.get(qci.split(' ')[0], 1.0)
    if strict_pcc:
        packet_core_score += 10 # Bonus for strict policy control
    
    domain_scores = {
        'radio': max(0, min(100, radio_score)),
        'transport': max(0, min(100, transport_score)),
        'core': max(0, min(100, core_score)),
        'packet_core': max(0, min(100, packet_core_score)),
    }

    # --- 3. Calculate Overall QoE Score (weighted average) ---
    weights = {'radio': 0.4, 'transport': 0.3, 'core': 0.2, 'packet_core': 0.1}
    qoe_score = sum(domain_scores[d] * weights[d] for d in domain_scores)

    # --- 4. Derive KPIs from Domain Scores ---
    kpis = {
        'download_speed': (domain_scores['radio'] * 0.6 + domain_scores['transport'] * 0.4) * 1.5,
        'upload_speed': (domain_scores['radio'] * 0.7 + domain_scores['transport'] * 0.3) * 0.5,
        'latency': 150 - (domain_scores['transport'] * 0.5 + domain_scores['core'] * 0.5),
        'jitter': 80 - (domain_scores['transport'] * 0.8 + domain_scores['radio'] * 0.2),
        'packet_loss': 5 - (domain_scores['radio'] * 0.5 + domain_scores['core'] * 0.5) / 20
    }
    # Ensure KPIs are within realistic bounds
    kpis['download_speed'] = max(1, min(150, kpis['download_speed']))
    kpis['upload_speed'] = max(1, min(50, kpis['upload_speed']))
    kpis['latency'] = max(10, min(500, kpis['latency']))
    kpis['jitter'] = max(5, min(100, kpis['jitter']))
    kpis['packet_loss'] = max(0, min(10, kpis['packet_loss']))

    # --- 5. Format Data for Charts ---
    # Radar: Throughput, Reliability, Latency, Jitter, Integrity (all 0-100, higher is better)
    radar_data = [
        (kpis['download_speed'] / 150) * 100, # Throughput
        100 - (kpis['packet_loss'] * 10), # Reliability
        100 - (kpis['latency'] / 500) * 100, # Latency
        100 - (kpis['jitter'] / 100) * 100, # Jitter
        domain_scores['core'] # Integrity
    ]

    # Domain Impact: Use the calculated domain scores
    domain_impact_data = list(domain_scores.values()) + [75] # Add static 75 for 'Application'

    # --- 6. Build JSON Response ---
    response_data = {
        'qoe_score': round(qoe_score, 1),
        'kpis': {key: round(value, 2) for key, value in kpis.items()},
        'radar_data': [round(d, 2) for d in radar_data],
        'domain_impact_data': [round(d, 2) for d in domain_impact_data]
    }

    return jsonify(response_data)
