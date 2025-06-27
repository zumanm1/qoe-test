"""
This script will directly add the subdomain column using SQLite commands,
then restore the data to ensure everything matches the model definition.
"""
import sqlite3
import os
from datetime import datetime

# Get the absolute path to the database file
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mtn_qoe.db')

def main():
    print(f"Fixing subdomain column in database: {DB_PATH}")
    
    # Create a backup of the database
    backup_path = f"{DB_PATH}.backup_{int(datetime.now().timestamp())}"
    try:
        with open(DB_PATH, 'rb') as src, open(backup_path, 'wb') as dst:
            dst.write(src.read())
        print(f"Created backup at: {backup_path}")
    except Exception as e:
        print(f"Warning: Could not create backup: {e}")
    
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Step 1: Check if the table already has the subdomain column
    cursor.execute("PRAGMA table_info(network_elements)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'subdomain' not in columns:
        print("Subdomain column is missing. Adding it now...")
        try:
            # Create a new table with the correct structure
            cursor.execute('''
            CREATE TABLE network_elements_new (
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
            
            # Copy data from the old table
            cursor.execute('''
            INSERT INTO network_elements_new (
                id, element_name, element_type, domain, protocol_layer, 
                location, status, created_at
            )
            SELECT 
                id, element_name, element_type, domain, protocol_layer, 
                location, status, created_at 
            FROM network_elements
            ''')
            
            # Drop the old table
            cursor.execute("DROP TABLE network_elements")
            
            # Rename the new table to the original name
            cursor.execute("ALTER TABLE network_elements_new RENAME TO network_elements")
            
            print("Successfully recreated the network_elements table with subdomain column")
        except Exception as e:
            print(f"Error adding subdomain column: {e}")
            return False
    else:
        print("Subdomain column already exists in the schema")
    
    # Step 2: Make sure all Transport domain elements have the proper subdomain
    print("\nUpdating subdomain values for Transport domain elements...")
    
    # TX_D elements
    tx_elements = [
        'TX_PE_RTR_01', 'TX_PE_RTR_02', 'TX_AGG_SW_01'
    ]
    
    # CDN_D elements
    cdn_elements = [
        'CDN_CORE_RTR_01', 'CDN_L3VPN_01', 'CDN_L3VPN_02'
    ]
    
    # Update TX_D elements
    for element_name in tx_elements:
        cursor.execute('''
        UPDATE network_elements 
        SET subdomain = 'TX_D'
        WHERE element_name = ? AND domain = 'transport'
        ''', (element_name,))
        print(f"Set {element_name} subdomain to TX_D")
    
    # Update CDN_D elements
    for element_name in cdn_elements:
        cursor.execute('''
        UPDATE network_elements 
        SET subdomain = 'CDN_D'
        WHERE element_name = ? AND domain = 'transport'
        ''', (element_name,))
        print(f"Set {element_name} subdomain to CDN_D")
    
    # Commit changes
    conn.commit()
    
    # Verify the updates
    print("\nVerifying the network elements table structure...")
    cursor.execute("PRAGMA table_info(network_elements)")
    columns = cursor.fetchall()
    print("Current columns:")
    for col in columns:
        print(f"  {col[1]}: {col[2]}")
    
    print("\nVerifying transport elements with subdomains...")
    cursor.execute('''
    SELECT element_name, domain, subdomain 
    FROM network_elements 
    WHERE domain = 'transport'
    ''')
    elements = cursor.fetchall()
    for element in elements:
        print(f"  {element[0]}: {element[1]} -> {element[2]}")
    
    # Close connection
    conn.close()
    print("\nFix completed!")
    
if __name__ == "__main__":
    main()
