"""
Complete reset and setup script for Mobile QoE Tool
- Removes existing database
- Creates new database with proper schema including subdomain support
- Sets up admin user
- Creates TX_D and CDN_D subdomains in TRANSPORT domain
- Adds example network elements for each subdomain
"""
import os
import sys
import sqlite3
from app import create_app, db
from app.models.user import User
from app.models.subdomain import NetworkSubdomain
from werkzeug.security import generate_password_hash
from datetime import datetime

# Create Flask application context
app = create_app('development')

def reset_database():
    """Remove the existing database file"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Mobile_qoe.db')
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Removed existing database: {db_path}")
        except Exception as e:
            print(f"Error removing database: {e}")
            return False
    return True

def create_tables():
    """Create all database tables"""
    with app.app_context():
        db.create_all()
        print("All database tables created successfully")
        return True

def create_admin_user():
    """Create admin user"""
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if admin is None:
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
            print("Admin user already exists")
        return True

def setup_transport_subdomains():
    """Setup TX_D and CDN_D subdomains"""
    with app.app_context():
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
        return True

def add_sample_network_elements():
    """Add sample network elements for TX_D and CDN_D subdomains"""
    with app.app_context():
        # Direct database access to avoid ORM issues
        conn = sqlite3.connect('Mobile_qoe.db')
        cursor = conn.cursor()
        
        # TX_D elements
        tx_elements = [
            ('TX_PE_RTR_01', 'PE Router', 'transport', 'TX_D', 'L3', 'Data Center East', 'active'),
            ('TX_PE_RTR_02', 'PE Router', 'transport', 'TX_D', 'L3', 'Data Center West', 'active'),
            ('TX_AGG_SW_01', 'Aggregation Switch', 'transport', 'TX_D', 'L2/L3', 'Regional Office North', 'active')
        ]
        
        # CDN_D elements
        cdn_elements = [
            ('CDN_CORE_RTR_01', 'Core Router', 'transport', 'CDN_D', 'L3', 'Main Data Center', 'active'),
            ('CDN_L3VPN_01', 'L3VPN Service', 'transport', 'CDN_D', 'L3', 'EPC Connection', 'active'),
            ('CDN_L3VPN_02', 'L3VPN Service', 'transport', 'CDN_D', 'L3', '5G Core Connection', 'active')
        ]
        
        # Add TX_D elements
        for element in tx_elements:
            cursor.execute("""
            INSERT INTO network_elements (element_name, element_type, domain, subdomain, protocol_layer, location, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, element)
            print(f"Added TX_D element: {element[0]}")
        
        # Add CDN_D elements
        for element in cdn_elements:
            cursor.execute("""
            INSERT INTO network_elements (element_name, element_type, domain, subdomain, protocol_layer, location, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, element)
            print(f"Added CDN_D element: {element[0]}")
        
        conn.commit()
        conn.close()
        return True

def main():
    """Main function to run all setup steps"""
    print("Starting Mobile QoE Tool complete setup...")
    
    if not reset_database():
        print("Failed to reset database. Exiting.")
        return False
    
    if not create_tables():
        print("Failed to create tables. Exiting.")
        return False
    
    if not create_admin_user():
        print("Failed to create admin user. Exiting.")
        return False
    
    if not setup_transport_subdomains():
        print("Failed to setup transport subdomains. Exiting.")
        return False
    
    if not add_sample_network_elements():
        print("Failed to add sample network elements. Exiting.")
        return False
    
    print("Mobile QoE Tool setup completed successfully!")
    return True

if __name__ == "__main__":
    main()
