"""
This script will update the NetworkElement model to match the database schema
and ensure SQLAlchemy properly recognizes the subdomain column.
"""
from app import create_app, db
import inspect
import os

def main():
    """Main function to update the model"""
    # Force reload all modules to clear any cached metadata
    print("Forcing reload of app models...")
    
    # Create the application context
    app = create_app('development')
    
    with app.app_context():
        from app.models.network import NetworkElement
        
        # Check current model definition
        print(f"Current NetworkElement class definition: {inspect.getsource(NetworkElement)}")
        
        # Display model attributes
        print("\nCurrent model attributes:")
        for attr in dir(NetworkElement):
            if not attr.startswith('_'):
                try:
                    value = getattr(NetworkElement, attr)
                    print(f"  {attr}: {value}")
                except Exception as e:
                    print(f"  {attr}: [Error: {e}]")
        
        # Check database columns
        print("\nChecking database columns for NetworkElement...")
        inspector = db.inspect(db.engine)
        columns = inspector.get_columns('network_elements')
        print("Database columns:")
        for column in columns:
            print(f"  {column['name']}: {column['type']}")
            
        # Directly query the database
        try:
            print("\nAttempting direct raw SQL query...")
            result = db.engine.execute("SELECT * FROM network_elements LIMIT 1").fetchone()
            print(f"Raw SQL result: {result}")
            
            # Extra check for subdomain column
            result = db.engine.execute("SELECT subdomain FROM network_elements LIMIT 1").fetchone()
            print(f"Raw subdomain query result: {result}")
        except Exception as e:
            print(f"Error with raw SQL: {e}")
        
        # Try direct ORM query with text()
        try:
            from sqlalchemy import text
            print("\nAttempting SQLAlchemy text() query...")
            result = db.session.execute(text("SELECT * FROM network_elements LIMIT 1")).fetchone()
            print(f"Text query result: {result}")
        except Exception as e:
            print(f"Error with text query: {e}")

    print("\nCompleted model inspection")
    
if __name__ == "__main__":
    main()
