"""
Complete setup script for Mobile QoE Tool Transport domain configuration
- Initializes database tables including the subdomain column
- Creates TX_D and CDN_D subdomains for TRANSPORT domain
- Adds sample network elements for each subdomain
"""
import sys
import os
from app import create_app, db
from app.models.network import NetworkElement
from datetime import datetime

# Define the subdomain model directly in this script to avoid circular imports
class NetworkSubdomain(db.Model):
    """Model for network subdomains within main domains"""
    __tablename__ = 'network_subdomains'
    
    id = db.Column(db.Integer, primary_key=True)
    subdomain_name = db.Column(db.String(100), nullable=False, unique=True)
    parent_domain = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<NetworkSubdomain {self.subdomain_name}>'
        
    def to_dict(self):
        return {
            'id': self.id,
            'subdomain_name': self.subdomain_name,
            'parent_domain': self.parent_domain,
            'description': self.description
        }

def setup_transport_domains():
    app = create_app('development')
    
    with app.app_context():
        # 1. Create all tables including our new subdomain table
        print("Creating/updating database schema...")
        db.create_all()
        
        # 2. Create TX_D and CDN_D subdomains
        print("Setting up TRANSPORT subdomains...")
        
        # Check if subdomains already exist
        tx_d = NetworkSubdomain.query.filter_by(subdomain_name='TX_D').first()
        cdn_d = NetworkSubdomain.query.filter_by(subdomain_name='CDN_D').first()
        
        if not tx_d:
            tx_d = NetworkSubdomain(
                subdomain_name='TX_D',
                parent_domain='transport',
                description='Transmission Domain - Connects 2G, 3G, 4G and 5G VRF on PE edge routers towards core networks.'
            )
            db.session.add(tx_d)
            print("Added TX_D subdomain")
        
        if not cdn_d:
            cdn_d = NetworkSubdomain(
                subdomain_name='CDN_D',
                parent_domain='transport',
                description='Core Data Network Domain (Note: Not Content Delivery Network) - Provides L3VPN services to connect EPC, CS and PS core (4G, LTE and 5G CORE and all related services provisioning).'
            )
            db.session.add(cdn_d)
            print("Added CDN_D subdomain")
            
        db.session.commit()
        
        # 3. Add example network elements for each subdomain
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
        
        print("Adding network elements for subdomains...")
        
        # Add TX_D elements
        for element_data in tx_elements:
            # Check if element exists
            element = NetworkElement.query.filter_by(element_name=element_data['element_name']).first()
            if not element:
                element = NetworkElement(**element_data)
                db.session.add(element)
                print(f"Added TX_D element: {element_data['element_name']}")
            else:
                # Update existing element
                for key, value in element_data.items():
                    setattr(element, key, value)
                print(f"Updated existing element: {element_data['element_name']}")
        
        # Add CDN_D elements
        for element_data in cdn_elements:
            # Check if element exists
            element = NetworkElement.query.filter_by(element_name=element_data['element_name']).first()
            if not element:
                element = NetworkElement(**element_data)
                db.session.add(element)
                print(f"Added CDN_D element: {element_data['element_name']}")
            else:
                # Update existing element
                for key, value in element_data.items():
                    setattr(element, key, value)
                print(f"Updated existing element: {element_data['element_name']}")
        
        db.session.commit()
        print("Transport domain setup completed successfully")

if __name__ == '__main__':
    setup_transport_domains()
