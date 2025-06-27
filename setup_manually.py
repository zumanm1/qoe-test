"""
Direct SQLite implementation of TX_D and CDN_D subdomains in the TRANSPORT domain
"""
import os
import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime

def main():
    # Connect to database (will create if doesn't exist)
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Mobile_qoe.db')
    print(f"Using database at: {db_path}")
    
    # Create database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create network_elements table with subdomain support
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS network_elements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        element_name TEXT NOT NULL UNIQUE,
        element_type TEXT NOT NULL,
        domain TEXT NOT NULL,
        subdomain TEXT,
        protocol_layer TEXT,
        location TEXT,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("Created network_elements table with subdomain support")
    
    # Create subdomains table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS network_subdomains (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subdomain_name TEXT NOT NULL UNIQUE,
        parent_domain TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("Created network_subdomains table")
    
    # Add TX_D subdomain
    cursor.execute("SELECT subdomain_name FROM network_subdomains WHERE subdomain_name=?", ('TX_D',))
    if not cursor.fetchone():
        cursor.execute('''
        INSERT INTO network_subdomains (subdomain_name, parent_domain, description)
        VALUES (?, ?, ?)
        ''', ('TX_D', 'transport', 'Transmission Domain - Connects 2G, 3G, 4G and 5G VRF on PE edge routers towards core networks.'))
        print("Added TX_D subdomain")
    
    # Add CDN_D subdomain
    cursor.execute("SELECT subdomain_name FROM network_subdomains WHERE subdomain_name=?", ('CDN_D',))
    if not cursor.fetchone():
        cursor.execute('''
        INSERT INTO network_subdomains (subdomain_name, parent_domain, description)
        VALUES (?, ?, ?)
        ''', ('CDN_D', 'transport', 'Core Data Network Domain - Provides L3VPN services to connect EPC, CS and PS core (4G, LTE and 5G CORE and all related services provisioning).'))
        print("Added CDN_D subdomain")
    
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
        cursor.execute("SELECT element_name FROM network_elements WHERE element_name=?", (element[0],))
        if not cursor.fetchone():
            cursor.execute('''
            INSERT INTO network_elements (element_name, element_type, domain, subdomain, protocol_layer, location, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', element)
            print(f"Added TX_D element: {element[0]}")
    
    # Add CDN_D elements
    for element in cdn_elements:
        cursor.execute("SELECT element_name FROM network_elements WHERE element_name=?", (element[0],))
        if not cursor.fetchone():
            cursor.execute('''
            INSERT INTO network_elements (element_name, element_type, domain, subdomain, protocol_layer, location, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', element)
            print(f"Added CDN_D element: {element[0]}")
    
    # Commit changes and close connection
    conn.commit()
    print("All changes committed to database")
    conn.close()
    print("Setup completed successfully")

if __name__ == "__main__":
    main()
