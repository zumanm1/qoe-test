"""
Complete database reset and setup for MTN QoE Tool
- Creates fresh database
- Sets up all tables with proper schema
- Creates admin user
- Sets up TX_D and CDN_D subdomains
- Creates sample network elements
"""
import os
import sqlite3
from werkzeug.security import generate_password_hash

# --- Configuration ---
DB_FILE = os.path.join(os.path.dirname(__file__), 'mtn_qoe.db')
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'Admin123!'
ADMIN_EMAIL = 'admin@example.com'

def reset_and_setup_database():
    """Deletes the existing database and sets up a new one with a full schema and initial data."""
    print(f"Database path: {DB_FILE}")

    # Delete the old database file if it exists
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print("Deleted existing database file.")

    # Connect to the new database (which will be created)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    print("Connected to database")

    # --- Schema Creation ---
    try:
        # Create users table
        cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        ''')
        print("Created users table")

        # Create network_subdomains table
        cursor.execute('''
        CREATE TABLE network_subdomains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subdomain_name TEXT UNIQUE NOT NULL,
            parent_domain TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        print("Created network_subdomains table")

        # Create network_elements table
        cursor.execute('''
        CREATE TABLE network_elements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            element_name TEXT UNIQUE NOT NULL,
            element_type TEXT NOT NULL,
            domain TEXT NOT NULL,
            subdomain TEXT,
            protocol_layer TEXT,
            location TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        print("Created network_elements table")

        # Create kpi_definitions table
        cursor.execute('''
        CREATE TABLE kpi_definitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kpi_name TEXT NOT NULL,
            kpi_code TEXT UNIQUE NOT NULL,
            unit TEXT,
            domain TEXT,
            impact_level TEXT,
            min_value REAL,
            max_value REAL,
            optimal_value REAL,
            description TEXT
        )
        ''')
        print("Created kpi_definitions table")

        # Create kpi_measurements table
        cursor.execute('''
        CREATE TABLE kpi_measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            element_id INTEGER NOT NULL,
            kpi_id INTEGER NOT NULL,
            value REAL NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            quality_score REAL,
            FOREIGN KEY (element_id) REFERENCES network_elements (id),
            FOREIGN KEY (kpi_id) REFERENCES kpi_definitions (id)
        )
        ''')
        print("Created kpi_measurements table")

        # Create alerts table
        cursor.execute('''
        CREATE TABLE alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            element_id INTEGER,
            kpi_id INTEGER,
            alert_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            acknowledged BOOLEAN DEFAULT 0,
            acknowledged_by INTEGER,
            acknowledged_at TIMESTAMP,
            FOREIGN KEY (element_id) REFERENCES network_elements (id),
            FOREIGN KEY (kpi_id) REFERENCES kpi_definitions (id),
            FOREIGN KEY (acknowledged_by) REFERENCES users (id)
        )
        ''')
        print("Created alerts table")

        # Create simulation_scenarios table
        cursor.execute('''
        CREATE TABLE simulation_scenarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario_name TEXT NOT NULL,
            description TEXT,
            created_by_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_baseline BOOLEAN DEFAULT 0,
            parameters TEXT,
            FOREIGN KEY (created_by_id) REFERENCES users (id)
        )
        ''')
        print("Created simulation_scenarios table")

        # Create performance_tests table
        cursor.execute('''
        CREATE TABLE performance_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_type TEXT,
            scenario_id INTEGER,
            download_speed REAL,
            upload_speed REAL,
            latency REAL,
            jitter REAL,
            packet_loss REAL,
            qoe_score REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            test_duration INTEGER,
            server_location TEXT,
            FOREIGN KEY (scenario_id) REFERENCES simulation_scenarios (id)
        )
        ''')
        print("Created performance_tests table")

        # Create optimization_recommendations table
        cursor.execute('''
        CREATE TABLE optimization_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario_id INTEGER,
            domain TEXT,
            severity TEXT,
            recommendation TEXT NOT NULL,
            impact_estimate REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            implemented BOOLEAN DEFAULT 0,
            implemented_by INTEGER,
            implemented_at TIMESTAMP,
            FOREIGN KEY (scenario_id) REFERENCES simulation_scenarios (id),
            FOREIGN KEY (implemented_by) REFERENCES users (id)
        )
        ''')
        print("Created optimization_recommendations table")

        # Create audit_logs table
        cursor.execute('''
        CREATE TABLE audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            resource_type TEXT,
            resource_id INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            details TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        print("Created audit_logs table")

        # --- Initial Data Insertion ---

        # Create admin user
        admin_password_hash = generate_password_hash(ADMIN_PASSWORD)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (ADMIN_USERNAME, ADMIN_EMAIL, admin_password_hash, 'admin')
        )
        print(f"Created admin user with username: {ADMIN_USERNAME} and password: {ADMIN_PASSWORD}")

        # Add Subdomains
        cursor.execute("INSERT INTO network_subdomains (subdomain_name, parent_domain, description) VALUES (?, ?, ?)", 
                       ('TX_D', 'TRANSPORT', 'Transmission Domain'))
        print("Added TX_D subdomain")
        cursor.execute("INSERT INTO network_subdomains (subdomain_name, parent_domain, description) VALUES (?, ?, ?)", 
                       ('CDN_D', 'TRANSPORT', 'Core Data Network Domain'))
        print("Added CDN_D subdomain")

        # Add KPI Definitions
        kpis = [
            ('LTE Accessibility', 'LTE_ACC', '%', 'RAN', 'high', 98, 100, 99.5, 'LTE network accessibility rate'),
            ('LTE Dropped Calls', 'LTE_DROP', '%', 'RAN', 'high', 0, 2, 0.5, 'LTE dropped call rate'),
            ('Data Throughput', 'DATA_THR', 'Mbps', 'CORE', 'medium', 5, 100, 50, 'Average data throughput')
        ]
        cursor.executemany("INSERT INTO kpi_definitions (kpi_name, kpi_code, unit, domain, impact_level, min_value, max_value, optimal_value, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", kpis)
        print(f"Added {len(kpis)} KPI definitions")

        # Add Network Elements with Subdomains
        elements = [
            ('TX_PE_RTR_01', 'Router', 'TRANSPORT', 'TX_D', 'IP/MPLS', 'New York'),
            ('TX_PE_RTR_02', 'Router', 'TRANSPORT', 'TX_D', 'IP/MPLS', 'London'),
            ('TX_AGG_SW_01', 'Switch', 'TRANSPORT', 'TX_D', 'Ethernet', 'New York'),
            ('CDN_CORE_RTR_01', 'Router', 'TRANSPORT', 'CDN_D', 'BGP', 'Frankfurt'),
            ('CDN_L3VPN_01', 'VPN', 'TRANSPORT', 'CDN_D', 'MPLS', 'Frankfurt'),
            ('CDN_L3VPN_02', 'VPN', 'TRANSPORT', 'CDN_D', 'MPLS', 'Ashburn'),
            ('RAN_BS_01', 'Base Station', 'RAN', None, 'LTE', 'Lagos'),
            ('RAN_BS_02', 'Base Station', 'RAN', None, '5G', 'Abuja'),
            ('CORE_SRV_01', 'Server', 'CORE', None, 'Application', 'Johannesburg'),
            ('INET_GW_01', 'Gateway', 'CORE', None, 'IP', 'Cape Town')
        ]
        for elem in elements:
            cursor.execute("INSERT INTO network_elements (element_name, element_type, domain, subdomain, protocol_layer, location) VALUES (?, ?, ?, ?, ?, ?)", elem)
            print(f"Added {elem[3] or 'other domain'} element: {elem[0]}")

        conn.commit()
        print("All changes committed to database")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
    finally:
        conn.close()

    print("Database setup completed successfully!")

if __name__ == '__main__':
    reset_and_setup_database()
