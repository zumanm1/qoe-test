"""
Direct SQLite database modification script to add subdomain column
"""
import sqlite3
import os

def fix_database():
    # Database path
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mtn_qoe.db')
    
    if not os.path.exists(db_path):
        print(f"Database file not found at: {db_path}")
        return False
    
    try:
        # Connect to SQLite database
        print(f"Connecting to database at: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the network_elements table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='network_elements'")
        if not cursor.fetchone():
            print("The network_elements table doesn't exist yet")
            return False
        
        # Check if subdomain column already exists
        cursor.execute("PRAGMA table_info(network_elements)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'subdomain' not in column_names:
            print("Adding 'subdomain' column to network_elements table...")
            cursor.execute("ALTER TABLE network_elements ADD COLUMN subdomain TEXT")
            conn.commit()
            print("Column added successfully")
        else:
            print("The 'subdomain' column already exists")
        
        # Add network_subdomains table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS network_subdomains (
            id INTEGER PRIMARY KEY,
            subdomain_name TEXT NOT NULL UNIQUE,
            parent_domain TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()
        print("Ensured network_subdomains table exists")
        
        # Add TX_D and CDN_D subdomains
        cursor.execute("SELECT subdomain_name FROM network_subdomains WHERE subdomain_name='TX_D'")
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO network_subdomains (subdomain_name, parent_domain, description)
            VALUES ('TX_D', 'transport', 'Transmission Domain - Connects 2G, 3G, 4G and 5G VRF on PE edge routers towards core networks.')
            """)
            print("Added TX_D subdomain")
        
        cursor.execute("SELECT subdomain_name FROM network_subdomains WHERE subdomain_name='CDN_D'")
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO network_subdomains (subdomain_name, parent_domain, description)
            VALUES ('CDN_D', 'transport', 'Core Data Network Domain - Provides L3VPN services to connect EPC, CS and PS core (4G, LTE and 5G CORE and all related services provisioning).')
            """)
            print("Added CDN_D subdomain")
        
        conn.commit()
        
        # Now add example network elements for these subdomains
        # First, let's add a TX_D element
        cursor.execute("SELECT element_name FROM network_elements WHERE element_name='TX_PE_RTR_01'")
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO network_elements (element_name, element_type, domain, subdomain, protocol_layer, location, status)
            VALUES ('TX_PE_RTR_01', 'PE Router', 'transport', 'TX_D', 'L3', 'Data Center East', 'active')
            """)
            print("Added TX_PE_RTR_01 element")
            
        # And a CDN_D element
        cursor.execute("SELECT element_name FROM network_elements WHERE element_name='CDN_CORE_RTR_01'")
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO network_elements (element_name, element_type, domain, subdomain, protocol_layer, location, status)
            VALUES ('CDN_CORE_RTR_01', 'Core Router', 'transport', 'CDN_D', 'L3', 'Main Data Center', 'active')
            """)
            print("Added CDN_CORE_RTR_01 element")
        
        conn.commit()
        conn.close()
        print("Database update completed successfully")
        return True
    except Exception as e:
        print(f"Error updating database: {e}")
        return False

if __name__ == '__main__':
    fix_database()
