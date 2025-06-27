"""
Migration script to add subdomain column to network_elements table
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app, db
from flask_migrate import Migrate, upgrade
import sqlite3

def run_migration():
    app = create_app('development')
    
    with app.app_context():
        try:
            # Connect to the database directly to add the column
            conn = sqlite3.connect(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
            cursor = conn.cursor()
            
            # Check if the column exists
            cursor.execute("PRAGMA table_info(network_elements)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'subdomain' not in column_names:
                print("Adding subdomain column to network_elements table...")
                cursor.execute("ALTER TABLE network_elements ADD COLUMN subdomain VARCHAR(50)")
                conn.commit()
                print("Column added successfully")
            else:
                print("Subdomain column already exists")
                
            conn.close()
            return True
        except Exception as e:
            print(f"Error during migration: {e}")
            return False

if __name__ == '__main__':
    run_migration()
