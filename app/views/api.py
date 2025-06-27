from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.network import NetworkElement, KPIMeasurement, KPIDefinition, Alert
from app.models.simulation import SimulationScenario, PerformanceTest
from app.services.simulation import SimulationEngine
from datetime import datetime, timedelta
from functools import wraps
import json

# Create API blueprint
api_bp = Blueprint('api', __name__)

def api_login_required(f):
    """Custom decorator for API authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Custom decorator for admin-only API endpoints"""
    @wraps(f)
    @api_login_required
    def decorated_function(*args, **kwargs):
        if not current_user.has_role('admin'):
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function


def engineer_required(f):
    """Custom decorator for engineer-level API endpoints"""
    @wraps(f)
    @api_login_required
    def decorated_function(*args, **kwargs):
        if not current_user.can_edit():
            return jsonify({'error': 'Engineer privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function


@api_bp.route('/network/elements', methods=['GET'])
@api_login_required
def get_network_elements():
    """Get all network elements"""
    domain = request.args.get('domain')
    status = request.args.get('status')
    
    query = NetworkElement.query
    
    if domain:
        query = query.filter_by(domain=domain)
    if status:
        query = query.filter_by(status=status)
    
    elements = query.all()
    
    result = [{
        'id': e.id,
        'name': e.element_name,
        'type': e.element_type,
        'domain': e.domain,
        'status': e.status,
        'location': e.location
    } for e in elements]
    
    return jsonify(result)


@api_bp.route('/network/elements/<int:element_id>', methods=['GET'])
@api_login_required
def get_network_element(element_id):
    """Get details for a specific network element"""
    element = NetworkElement.query.get_or_404(element_id)
    
    # Get latest KPI values
    latest_kpis = element.get_latest_kpis()
    
    # Get recent alerts (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(hours=24)
    recent_alerts = Alert.query.filter_by(element_id=element_id).filter(
        Alert.created_at >= yesterday
    ).order_by(Alert.created_at.desc()).limit(5).all()
    
    result = {
        'id': element.id,
        'name': element.element_name,
        'type': element.element_type,
        'domain': element.domain,
        'protocol_layer': element.protocol_layer,
        'location': element.location,
        'status': element.status,
        'created_at': element.created_at.isoformat(),
        'kpis': latest_kpis,
        'alerts': [a.to_dict() for a in recent_alerts]
    }
    
    return jsonify(result)


@api_bp.route('/network/elements/<int:element_id>/kpis', methods=['GET'])
@api_login_required
def get_element_kpis(element_id):
    """Get KPI measurements for a specific network element"""
    element = NetworkElement.query.get_or_404(element_id)
    
    kpi_code = request.args.get('kpi_code')
    hours = request.args.get('hours', type=int, default=24)
    
    # Get KPI definition if kpi_code is specified
    kpi_def = None
    if kpi_code:
        kpi_def = KPIDefinition.query.filter_by(kpi_code=kpi_code).first()
        if not kpi_def:
            return jsonify({'error': 'Invalid KPI code'}), 400
    
    # Get KPI measurements
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    query = KPIMeasurement.query.filter(
        KPIMeasurement.element_id == element_id,
        KPIMeasurement.timestamp >= cutoff
    )
    
    if kpi_def:
        query = query.filter(KPIMeasurement.kpi_id == kpi_def.id)
    
    measurements = query.order_by(KPIMeasurement.timestamp).all()
    
    result = [m.to_dict() for m in measurements]
    
    return jsonify(result)


@api_bp.route('/network/elements', methods=['POST'])
@engineer_required
def create_network_element():
    """Create a new network element"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate required fields
    required_fields = ['element_name', 'element_type', 'domain']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if element already exists
    existing = NetworkElement.query.filter_by(element_name=data['element_name']).first()
    if existing:
        return jsonify({'error': 'Element with this name already exists'}), 400
    
    # Create new element
    element = NetworkElement(
        element_name=data['element_name'],
        element_type=data['element_type'],
        domain=data['domain'],
        protocol_layer=data.get('protocol_layer'),
        location=data.get('location'),
        status=data.get('status', 'active'),
        created_at=datetime.utcnow()
    )
    
    db.session.add(element)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'id': element.id,
        'message': f'Element {data["element_name"]} created successfully'
    }), 201


@api_bp.route('/network/elements/<int:element_id>', methods=['PUT'])
@engineer_required
def update_network_element(element_id):
    """Update an existing network element"""
    element = NetworkElement.query.get_or_404(element_id)
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update fields
    if 'element_name' in data:
        element.element_name = data['element_name']
    if 'element_type' in data:
        element.element_type = data['element_type']
    if 'domain' in data:
        element.domain = data['domain']
    if 'protocol_layer' in data:
        element.protocol_layer = data['protocol_layer']
    if 'location' in data:
        element.location = data['location']
    if 'status' in data:
        element.status = data['status']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Element {element.element_name} updated successfully'
    })


@api_bp.route('/kpi/measurements', methods=['POST'])
@engineer_required
def create_kpi_measurement():
    """Create a new KPI measurement"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate required fields
    required_fields = ['element_name', 'kpi_code', 'value']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Get element and KPI definition
    element = NetworkElement.query.filter_by(element_name=data['element_name']).first()
    if not element:
        return jsonify({'error': 'Invalid element name'}), 400
    
    kpi_def = KPIDefinition.query.filter_by(kpi_code=data['kpi_code']).first()
    if not kpi_def:
        return jsonify({'error': 'Invalid KPI code'}), 400
    
    # Calculate quality score based on KPI definition
    quality_score = None
    if kpi_def.optimal_value is not None and kpi_def.min_value is not None and kpi_def.max_value is not None:
        # Calculate based on distance from optimal value
        value = float(data['value'])
        range_size = kpi_def.max_value - kpi_def.min_value
        if range_size > 0:
            distance = abs(value - kpi_def.optimal_value) / range_size
            quality_score = max(0, min(100, 100 * (1 - distance)))
    
    # Create measurement
    measurement = KPIMeasurement(
        element_id=element.id,
        kpi_id=kpi_def.id,
        value=float(data['value']),
        timestamp=datetime.utcnow(),
        quality_score=quality_score
    )
    
    db.session.add(measurement)
    
    # Check if this measurement should trigger an alert
    if kpi_def.is_critical(float(data['value'])):
        alert = Alert(
            element_id=element.id,
            kpi_id=kpi_def.id,
            alert_type='kpi_threshold',
            severity='high',
            message=f'Critical {kpi_def.kpi_name} value: {data["value"]} {kpi_def.unit or ""}',
            created_at=datetime.utcnow()
        )
        db.session.add(alert)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'id': measurement.id,
        'message': f'KPI measurement created successfully'
    }), 201


@api_bp.route('/alerts', methods=['GET'])
@api_login_required
def get_alerts():
    """Get all alerts, with optional filtering"""
    severity = request.args.get('severity')
    domain = request.args.get('domain')
    acknowledged = request.args.get('acknowledged')
    hours = request.args.get('hours', type=int, default=24)
    
    # Start with base query
    query = Alert.query
    
    # Apply filters
    if severity:
        query = query.filter(Alert.severity == severity)
    
    if domain:
        query = query.join(NetworkElement).filter(NetworkElement.domain == domain)
    
    if acknowledged is not None:
        acknowledged = acknowledged.lower() == 'true'
        query = query.filter(Alert.acknowledged == acknowledged)
    
    # Time filter
    if hours:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        query = query.filter(Alert.created_at >= cutoff)
    
    # Get results
    alerts = query.order_by(Alert.created_at.desc()).all()
    
    result = [a.to_dict() for a in alerts]
    
    return jsonify(result)


@api_bp.route('/alerts/<int:alert_id>/acknowledge', methods=['POST'])
@engineer_required
def acknowledge_alert(alert_id):
    """Acknowledge an alert"""
    alert = Alert.query.get_or_404(alert_id)
    
    alert.acknowledged = True
    alert.acknowledged_by = current_user.id
    alert.acknowledged_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Alert acknowledged successfully'
    })


@api_bp.route('/topology', methods=['GET'])
@api_login_required
def get_topology():
    """Get network topology data for visualization"""
    # Get all elements
    elements = NetworkElement.query.all()
    
    # Structure for D3.js force-directed graph
    nodes = []
    links = []
    
    # Add nodes (elements)
    for e in elements:
        latest_kpis = e.get_latest_kpis()
        nodes.append({
            'id': e.id,
            'name': e.element_name,
            'type': e.element_type,
            'domain': e.domain,
            'status': e.status,
            'kpis': latest_kpis
        })
    
    # Define connections based on network architecture
    # In a real app, these would come from a connections table
    # For this prototype, we'll define a simple chain topology
    
    # Sort elements by domain in the expected order
    domain_order = {'ran': 1, 'transport': 2, 'core': 3, 'internet': 4}
    elements_by_domain = {}
    
    for e in elements:
        if e.domain not in elements_by_domain:
            elements_by_domain[e.domain] = []
        elements_by_domain[e.domain].append(e)
    
    # Connect elements within domains
    for domain, domain_elements in elements_by_domain.items():
        for i in range(len(domain_elements) - 1):
            links.append({
                'source': domain_elements[i].id,
                'target': domain_elements[i + 1].id,
                'type': f'intra-{domain}'
            })
    
    # Connect domains in sequence
    domains = sorted(elements_by_domain.keys(), key=lambda d: domain_order.get(d, 999))
    for i in range(len(domains) - 1):
        if domains[i] in elements_by_domain and domains[i + 1] in elements_by_domain:
            # Connect last element of current domain to first element of next domain
            source = elements_by_domain[domains[i]][-1].id
            target = elements_by_domain[domains[i + 1]][0].id
            links.append({
                'source': source,
                'target': target,
                'type': f'inter-domain'
            })
    
    return jsonify({
        'nodes': nodes,
        'links': links
    })
