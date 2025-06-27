"""
Initialize subdomains for Mobile QoE Tool
This script adds TX_D and CDN_D subdomains to the TRANSPORT domain
"""
from app import create_app, db
from app.models.subdomain import NetworkSubdomain

def init_subdomains():
    app = create_app('development')
    
    with app.app_context():
        # Create all tables including our new subdomain table
        db.create_all()
        print("Ensured all tables exist including network_subdomains")
        
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
        print("Transport subdomains initialized successfully")

if __name__ == '__main__':
    init_subdomains()
