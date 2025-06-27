"""
Comprehensive database synchronization script for Mobile QoE Tool
This script will:
1. Ensure the network_elements table has the subdomain column
2. Set up TX_D and CDN_D subdomains for TRANSPORT domain
3. Create sample network elements for both subdomains
"""
import os
import sqlite3
import sys
from datetime import datetime

# Database path
DB_PATH = 'mtn_qoe.db'

def main():
    print(f"Starting database synchronization for Mobile QoE Tool...")
    
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"Database file not found at: {DB_PATH}")
        return False
    
    # Step 1: Connect to database and check structure
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if network_elements table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='network_elements'")
        if not cursor.fetchone():
            print("Network elements table doesn't exist, creating it...")
            cursor.execute('''
            CREATE TABLE network_elements (
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
        else:
            # Check if subdomain column exists
            cursor.execute("PRAGMA table_info(network_elements)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'subdomain' not in columns:
                print("Adding subdomain column to network_elements table...")
                cursor.execute("ALTER TABLE network_elements ADD COLUMN subdomain TEXT")
                print("Added subdomain column to network_elements table")
            else:
                print("Subdomain column already exists in network_elements table")
        
        # Step 2: Create network_subdomains table if it doesn't exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='network_subdomains'")
        if not cursor.fetchone():
            cursor.execute('''
            CREATE TABLE network_subdomains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subdomain_name TEXT NOT NULL UNIQUE,
                parent_domain TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            print("Created network_subdomains table")
        
        # Step 3: Add TX_D and CDN_D subdomains
        cursor.execute("SELECT subdomain_name FROM network_subdomains WHERE subdomain_name='TX_D'")
        if not cursor.fetchone():
            cursor.execute('''
            INSERT INTO network_subdomains (subdomain_name, parent_domain, description)
            VALUES (?, ?, ?)
            ''', ('TX_D', 'transport', 'Transmission Domain - Connects 2G, 3G, 4G and 5G VRF on PE edge routers towards core networks.'))
            print("Added TX_D subdomain")
        
        cursor.execute("SELECT subdomain_name FROM network_subdomains WHERE subdomain_name='CDN_D'")
        if not cursor.fetchone():
            cursor.execute('''
            INSERT INTO network_subdomains (subdomain_name, parent_domain, description)
            VALUES (?, ?, ?)
            ''', ('CDN_D', 'transport', 'Core Data Network Domain - Provides L3VPN services to connect EPC, CS and PS core (4G, LTE and 5G CORE and all related services provisioning).'))
            print("Added CDN_D subdomain")
        
        # Step 4: Add example network elements for TX_D and CDN_D
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
            else:
                # Update existing element with subdomain
                cursor.execute('''
                UPDATE network_elements 
                SET subdomain=?, protocol_layer=?, location=?, status=?
                WHERE element_name=?
                ''', (element[3], element[4], element[5], element[6], element[0]))
                print(f"Updated existing element: {element[0]}")
        
        # Add CDN_D elements
        for element in cdn_elements:
            cursor.execute("SELECT element_name FROM network_elements WHERE element_name=?", (element[0],))
            if not cursor.fetchone():
                cursor.execute('''
                INSERT INTO network_elements (element_name, element_type, domain, subdomain, protocol_layer, location, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', element)
                print(f"Added CDN_D element: {element[0]}")
            else:
                # Update existing element with subdomain
                cursor.execute('''
                UPDATE network_elements 
                SET subdomain=?, protocol_layer=?, location=?, status=?
                WHERE element_name=?
                ''', (element[3], element[4], element[5], element[6], element[0]))
                print(f"Updated existing element: {element[0]}")
        
        # Step 5: Export SQL to help with SQLAlchemy synchronization
        print("\nGenerating SQL for manual inspection...")
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='network_elements'")
        network_elements_sql = cursor.fetchone()[0]
        print(f"Network Elements Table SQL:\n{network_elements_sql}\n")
        
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='network_subdomains'")
        network_subdomains_sql = cursor.fetchone()[0]
        print(f"Network Subdomains Table SQL:\n{network_subdomains_sql}\n")
        
        # Commit all changes and close connection
        conn.commit()
        conn.close()
        print("Database synchronization completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during database synchronization: {e}")
        return False

if __name__ == "__main__":
    main()
