import os
from werkzeug.security import generate_password_hash
from datetime import datetime
from app import create_app, db
from app.models.user import User
from app.models.network import NetworkElement, KPIDefinition

# ==============================================================================
# Programmatic Database Setup and Seeding
# ==============================================================================
# This script contains all logic for preparing the database. It is designed
# to be called directly from other scripts, avoiding the Flask CLI for setup.
# ==============================================================================

def seed_kpis():
    """Seed the database with KPI definitions if they don't exist."""
    if KPIDefinition.query.first():
        print("KPI definitions already exist.")
        return

    kpi_data = [
        {'kpi_name': 'Signal-to-Interference-plus-Noise Ratio', 'kpi_code': 'sinr', 'unit': 'dB', 'domain': 'ran', 'impact_level': 'high', 'min_value': -5, 'max_value': 30, 'optimal_value': 20, 'description': 'Measures the ratio of the received desired signal to the received undesired signals.'},
        {'kpi_name': 'Physical Resource Block Utilization', 'kpi_code': 'prb_util', 'unit': '%', 'domain': 'ran', 'impact_level': 'medium', 'min_value': 0, 'max_value': 100, 'optimal_value': 50, 'description': 'Percentage of allocated PRBs.'},
        {'kpi_name': 'MPLS Tunnel Utilization', 'kpi_code': 'mpls_util', 'unit': '%', 'domain': 'transport', 'impact_level': 'high', 'min_value': 0, 'max_value': 100, 'optimal_value': 60, 'description': 'Utilization of MPLS tunnels.'},
        {'kpi_name': 'Download Speed', 'kpi_code': 'dl_speed', 'unit': 'Mbps', 'domain': 'e2e', 'impact_level': 'high', 'min_value': 1, 'max_value': 1000, 'optimal_value': 50, 'description': 'Measured download speed.'},
        {'kpi_name': 'Latency', 'kpi_code': 'latency', 'unit': 'ms', 'domain': 'e2e', 'impact_level': 'high', 'min_value': 5, 'max_value': 500, 'optimal_value': 20, 'description': 'End-to-end round-trip time.'}
    ]

    for kpi_info in kpi_data:
        kpi = KPIDefinition(**kpi_info)
        db.session.add(kpi)
    db.session.commit()
    print("KPI definitions seeded successfully.")

def create_default_admin(username='admin', email='admin@Mobile.com', password='Admin123!'):
    """Create a default admin user if one does not exist."""
    if User.query.filter_by(username=username).first():
        print(f"Admin user '{username}' already exists.")
        return

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        role='admin',
        created_at=datetime.utcnow()
    )
    db.session.add(user)
    db.session.commit()
    print(f"Admin user '{username}' created successfully.")

def seed_network():
    """Seed the database with sample network elements if they don't exist."""
    if NetworkElement.query.first():
        print("Network elements already exist.")
        return

    network_elements = [
        {'element_name': 'UE_DEVICE', 'element_type': 'mobile', 'domain': 'ran', 'protocol_layer': 'l1', 'location': 'Client Side', 'status': 'active'},
        {'element_name': 'ENB_SITE_1', 'element_type': 'enb', 'domain': 'ran', 'protocol_layer': 'l1-l3', 'location': 'Cell Site Alpha', 'status': 'active'},
        {'element_name': 'ROUTER_EDGE_1', 'element_type': 'router', 'domain': 'transport', 'protocol_layer': 'l3', 'location': 'Edge POP 1', 'status': 'active'},
        {'element_name': 'S_GW_1', 'element_type': 'gateway', 'domain': 'core', 'protocol_layer': 'l3-l4', 'location': 'Core Data Center', 'status': 'active'},
        {'element_name': 'P_GW_1', 'element_type': 'gateway', 'domain': 'core', 'protocol_layer': 'l3-l4', 'location': 'Core Data Center', 'status': 'active'},
        {'element_name': 'INTERNET_GW', 'element_type': 'gateway', 'domain': 'internet', 'protocol_layer': 'l3', 'location': 'Internet Edge', 'status': 'active'},
        {'element_name': 'SPEEDTEST_SERVER', 'element_type': 'server', 'domain': 'internet', 'protocol_layer': 'l7', 'location': 'Data Center', 'status': 'active'}
    ]

    for element in network_elements:
        net_elem = NetworkElement(**element)
        db.session.add(net_elem)
    db.session.commit()
    print("Network elements seeded successfully.")

def run_setup():
    """Main function to run all setup tasks within the app context."""
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    with app.app_context():
        print("--- Running Database Setup ---")
        create_default_admin()
        seed_kpis()
        seed_network()
        print("--- Database Setup Complete ---")

if __name__ == '__main__':
    run_setup()
