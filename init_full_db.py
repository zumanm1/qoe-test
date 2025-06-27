"""
Complete database initialization script for Mobile QoE Tool
- Creates ALL database tables including network_elements with subdomain support
- Adds an admin user
- Sets up TX_D and CDN_D subdomains in the TRANSPORT domain
"""
from app import create_app, db
from app.models.user import User
from app.models.network import NetworkElement
from datetime import datetime
from werkzeug.security import generate_password_hash
import sqlite3

# Define the NetworkSubdomain model here to avoid import issues
class NetworkSubdomain(db.Model):
    """Model for network subdomains within main domains"""
    __tablename__ = 'network_subdomains'
    
    id = db.Column(db.Integer, primary_key=True)
    subdomain_name = db.Column(db.String(100), nullable=False, unique=True)
    parent_domain = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create Flask application context
app = create_app('development')

with app.app_context():
    # Create all database tables - this will include the new NetworkSubdomain model
    print("Creating all database tables...")
    db.create_all()
    
    # Check if admin user exists
    admin = User.query.filter_by(username='admin').first()
    if admin is None:
        # Create admin user
        admin = User(
            username='admin',
            email='admin@Mobile.com',
            password_hash=generate_password_hash('Admin123!'),
            role='admin',
            created_at=datetime.utcnow()
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created with username: 'admin' and password: 'Admin123!'")
    else:
        print("Admin user already exists.")
    
    # Set up the TX_D and CDN_D subdomains
    tx_d = NetworkSubdomain.query.filter_by(subdomain_name='TX_D').first()
    if not tx_d:
        tx_d = NetworkSubdomain(
            subdomain_name='TX_D',
            parent_domain='transport',
            description='Transmission Domain - Connects 2G, 3G, 4G and 5G VRF on PE edge routers towards core networks.'
        )
        db.session.add(tx_d)
        print("Added TX_D subdomain")
    
    cdn_d = NetworkSubdomain.query.filter_by(subdomain_name='CDN_D').first()
    if not cdn_d:
        cdn_d = NetworkSubdomain(
            subdomain_name='CDN_D',
            parent_domain='transport',
            description='Core Data Network Domain (Note: Not Content Delivery Network) - Provides L3VPN services to connect EPC, CS and PS core (4G, LTE and 5G CORE and all related services provisioning).'
        )
        db.session.add(cdn_d)
        print("Added CDN_D subdomain")
    
    db.session.commit()
    
    # Add example network elements for each subdomain
    # TX_D (Transmission Domain) Elements
    tx_elements = [
        {
            'element_name': 'TX_PE_RTR_01',
            'element_type': 'PE Router',
            'domain': 'transport',
            'subdomain': 'TX_D',
            'protocol_layer': 'L3',
            'location': 'Data Center East',
            'status': 'active'
        },
        {
            'element_name': 'TX_PE_RTR_02',
            'element_type': 'PE Router',
            'domain': 'transport',
            'subdomain': 'TX_D',
            'protocol_layer': 'L3',
            'location': 'Data Center West',
            'status': 'active'
        },
        {
            'element_name': 'TX_AGG_SW_01',
            'element_type': 'Aggregation Switch',
            'domain': 'transport',
            'subdomain': 'TX_D',
            'protocol_layer': 'L2/L3',
            'location': 'Regional Office North',
            'status': 'active'
        },
    ]
    
    # CDN_D (Core Data Network Domain) Elements
    cdn_elements = [
        {
            'element_name': 'CDN_CORE_RTR_01',
            'element_type': 'Core Router',
            'domain': 'transport',
            'subdomain': 'CDN_D',
            'protocol_layer': 'L3',
            'location': 'Main Data Center',
            'status': 'active'
        },
        {
            'element_name': 'CDN_L3VPN_01',
            'element_type': 'L3VPN Service',
            'domain': 'transport',
            'subdomain': 'CDN_D',
            'protocol_layer': 'L3',
            'location': 'EPC Connection',
            'status': 'active'
        },
        {
            'element_name': 'CDN_L3VPN_02',
            'element_type': 'L3VPN Service',
            'domain': 'transport',
            'subdomain': 'CDN_D',
            'protocol_layer': 'L3',
            'location': '5G Core Connection',
            'status': 'active'
        },
    ]
    
    print("Adding example network elements...")
    
    # Add TX_D elements
    for element_data in tx_elements:
        element = NetworkElement.query.filter_by(element_name=element_data['element_name']).first()
        if not element:
            element = NetworkElement(**element_data)
            db.session.add(element)
            print(f"Added TX_D element: {element_data['element_name']}")
    
    # Add CDN_D elements
    for element_data in cdn_elements:
        element = NetworkElement.query.filter_by(element_name=element_data['element_name']).first()
        if not element:
            element = NetworkElement(**element_data)
            db.session.add(element)
            print(f"Added CDN_D element: {element_data['element_name']}")
    
    db.session.commit()
    print("Full database initialization complete with TRANSPORT subdomains and example elements.")
