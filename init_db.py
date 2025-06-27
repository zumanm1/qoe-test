"""
Database initialization script for Mobile QoE Tool
Creates the database tables and adds an admin user
"""
from app import create_app, db
from app.models.user import User
from datetime import datetime
from werkzeug.security import generate_password_hash

# Create Flask application context
app = create_app('development')

with app.app_context():
    # Create all database tables
    db.create_all()
    print("Database tables created.")
    
    # Check if admin user exists
    admin = User.query.filter_by(username='admin').first()
    if admin is None:
        # Create admin user
        admin = User(
            username='admin',
            email='admin@Mobile.com',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            created_at=datetime.utcnow()
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created with username: 'admin' and password: 'admin123'")
    else:
        print("Admin user already exists.")
    
    print("Database initialization complete.")
