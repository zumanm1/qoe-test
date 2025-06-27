from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from flask_login import login_required, current_user
from app.models.network import NetworkElement, KPIMeasurement, KPIDefinition, Alert
from app.models.subdomain import NetworkSubdomain
from app.models.simulation import PerformanceTest
from datetime import datetime, timedelta
import json

# Create dashboard blueprint
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard view"""
    # Get summary statistics
    total_elements = NetworkElement.query.count()
    active_elements = NetworkElement.query.filter_by(status='active').count()
    
    # Get elements by domain for domain health calculation
    elements_by_domain = {}
    for domain in ['ran', 'transport', 'core', 'internet']:
        elements_by_domain[domain] = {
            'total': NetworkElement.query.filter_by(domain=domain).count(),
            'active': NetworkElement.query.filter_by(domain=domain, status='active').count()
        }
    
    # Get recent alerts (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(hours=24)
    recent_alerts = Alert.query.filter(
        Alert.created_at >= yesterday
    ).order_by(Alert.created_at.desc()).limit(10).all()
    
    # Get recent performance tests
    recent_tests = PerformanceTest.query.order_by(
        PerformanceTest.timestamp.desc()
    ).limit(5).all()
    
    return render_template(
        'dashboard/index.html',
        title='Network QoE Dashboard',
        total_elements=total_elements,
        active_elements=active_elements,
        elements_by_domain=elements_by_domain,
        recent_alerts=recent_alerts,
        recent_tests=recent_tests
    )


@dashboard_bp.route('/domain/<domain>')
@login_required
def domain_view(domain):
    """View details for a specific network domain"""
    valid_domains = ['ran', 'transport', 'core', 'internet', 'e2e']
    if domain not in valid_domains:
        return redirect(url_for('dashboard.index'))
    
    # Get all elements in this domain
    elements = NetworkElement.query.filter_by(domain=domain).all()
    
    # Get subdomains for this domain (especially for Transport domain)
    subdomains = []
    if domain == 'transport':
        subdomains = NetworkSubdomain.query.filter_by(parent_domain=domain).all()
    
    # Get KPI definitions for this domain
    kpi_defs = KPIDefinition.query.filter_by(domain=domain).all()
    
    # Get domain health percentage
    active_count = NetworkElement.query.filter_by(domain=domain, status='active').count()
    total_count = NetworkElement.query.filter_by(domain=domain).count()
    domain_health = int((active_count / total_count * 100) if total_count > 0 else 0)
    
    return render_template(
        'dashboard/domain.html',
        title=f'{domain.upper()} Domain',
        subdomains=subdomains,
        domain=domain,
        elements=elements,
        kpi_defs=kpi_defs,
        domain_health=domain_health
    )

@dashboard_bp.route('/network_topology')
@login_required
def network_topology():
    """Network topology visualization view"""
    return render_template(
        'dashboard/network_topology.html',
        title='Network Topology Visualization'
    )


@dashboard_bp.route('/alerts')
@login_required
def alerts():
    """View all system alerts"""
    # Get filter parameters
    severity = request.args.get('severity')
    domain = request.args.get('domain')
    acknowledged = request.args.get('acknowledged')
    
    # Base query
    query = Alert.query
    
    # Apply filters
    if severity:
        query = query.filter(Alert.severity == severity)
    if domain:
        query = query.join(NetworkElement).filter(NetworkElement.domain == domain)
    if acknowledged:
        acknowledged = acknowledged.lower() == 'true'
        query = query.filter(Alert.acknowledged == acknowledged)
    
    # Get alerts ordered by creation time (newest first)
    alerts = query.order_by(Alert.created_at.desc()).all()
    
    return render_template(
        'dashboard/alerts.html',
        title='System Alerts',
        alerts=alerts
    )


@dashboard_bp.route('/api/kpi-data')
@login_required
def kpi_data():
    """API endpoint to get KPI data for charts"""
    element_id = request.args.get('element_id', type=int)
    kpi_code = request.args.get('kpi_code', '')
    hours = request.args.get('hours', 24, type=int)
    
    if not element_id or not kpi_code:
        return jsonify({'error': 'Missing parameters'}), 400
    
    # Get the KPI definition
    kpi_def = KPIDefinition.query.filter_by(kpi_code=kpi_code).first()
    if not kpi_def:
        return jsonify({'error': 'Invalid KPI code'}), 400
    
    # Get the network element
    element = NetworkElement.query.get(element_id)
    if not element:
        return jsonify({'error': 'Invalid element ID'}), 400
    
    # Get KPI measurements
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    measurements = KPIMeasurement.query.join(KPIDefinition).filter(
        KPIMeasurement.element_id == element_id,
        KPIDefinition.kpi_code == kpi_code,
        KPIMeasurement.timestamp >= cutoff
    ).order_by(KPIMeasurement.timestamp).all()
    
    # Format data for charts
    data = {
        'labels': [m.timestamp.strftime('%H:%M') for m in measurements],
        'datasets': [{
            'label': f'{kpi_def.kpi_name} ({kpi_def.unit})',
            'data': [m.value for m in measurements],
            'borderColor': '#3498db',
            'backgroundColor': 'rgba(52, 152, 219, 0.2)',
            'fill': True,
            'tension': 0.4
        }]
    }
    
    return jsonify(data)


@dashboard_bp.route('/api/domain-health')
@login_required
def domain_health():
    """API endpoint to get domain health data for charts"""
    # Calculate health percentage for each domain
    domains = ['ran', 'transport', 'core', 'internet']
    data = []
    
    for domain in domains:
        active_count = NetworkElement.query.filter_by(domain=domain, status='active').count()
        total_count = NetworkElement.query.filter_by(domain=domain).count()
        health = int((active_count / total_count * 100) if total_count > 0 else 0)
        
        data.append({
            'domain': domain.upper(),
            'health': health,
            'color': get_health_color(health)
        })
    
    return jsonify(data)


def get_health_color(health):
    """Get color code based on health percentage"""
    if health >= 90:
        return '#2ecc71'  # Green
    elif health >= 75:
        return '#f1c40f'  # Yellow
    elif health >= 60:
        return '#e67e22'  # Orange
    else:
        return '#e74c3c'  # Red
