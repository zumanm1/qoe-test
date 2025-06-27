"""
Refresh SQLAlchemy models and database schema
"""
from app import create_app, db
from app.models.network import NetworkElement, KPIMeasurement, KPIDefinition, Alert
from app.models.subdomain import NetworkSubdomain
from app.models.user import User
import sqlite3
import os

def refresh_sqlalchemy_schema():
    """Force SQLAlchemy to refresh its understanding of the database schema"""
    app = create_app('development')
    with app.app_context():
        print("Refreshing SQLAlchemy metadata...")
        db.metadata.clear()
        db.reflect()
        print("SQLAlchemy metadata refreshed")
        
        # Verify schema
        try:
            elements = NetworkElement.query.all()
            print(f"Successfully queried {len(elements)} network elements")
            
            subdomains = NetworkSubdomain.query.all()
            print(f"Successfully queried {len(subdomains)} network subdomains")
            
            for subdomain in subdomains:
                print(f"  - {subdomain.subdomain_name} ({subdomain.parent_domain})")
                
            # Print a few elements with their subdomains
            transport_elements = NetworkElement.query.filter_by(domain='transport').limit(5).all()
            print("\nSample transport elements:")
            for element in transport_elements:
                print(f"  - {element.element_name} (Subdomain: {element.subdomain})")
                
            print("\nSchema refresh completed successfully!")
            return True
        except Exception as e:
            print(f"Error during schema refresh: {e}")
            return False

if __name__ == "__main__":
    refresh_sqlalchemy_schema()
