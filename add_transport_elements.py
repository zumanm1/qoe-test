"""
Add example network elements for the TX_D and CDN_D subdomains in TRANSPORT domain
"""
from app import create_app, db
from app.models.network import NetworkElement
from datetime import datetime

def add_transport_elements():
    app = create_app('development')
    
    with app.app_context():
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
        
        # Add TX_D elements
        for element_data in tx_elements:
            # Check if element exists
            element = NetworkElement.query.filter_by(element_name=element_data['element_name']).first()
            if not element:
                element = NetworkElement(**element_data)
                db.session.add(element)
                print(f"Added TX_D element: {element_data['element_name']}")
            else:
                # Update subdomain if not set
                if not element.subdomain:
                    element.subdomain = 'TX_D'
                    print(f"Updated existing element with TX_D subdomain: {element_data['element_name']}")
        
        # Add CDN_D elements
        for element_data in cdn_elements:
            # Check if element exists
            element = NetworkElement.query.filter_by(element_name=element_data['element_name']).first()
            if not element:
                element = NetworkElement(**element_data)
                db.session.add(element)
                print(f"Added CDN_D element: {element_data['element_name']}")
            else:
                # Update subdomain if not set
                if not element.subdomain:
                    element.subdomain = 'CDN_D'
                    print(f"Updated existing element with CDN_D subdomain: {element_data['element_name']}")
        
        db.session.commit()
        print("Transport domain elements added successfully")

if __name__ == '__main__':
    add_transport_elements()
