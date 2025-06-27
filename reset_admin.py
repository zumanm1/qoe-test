"""
Reset admin password script for Mobile QoE Tool
"""
from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

# Create Flask application context
app = create_app('development')

with app.app_context():
    # Find admin user
    admin = User.query.filter_by(username='admin').first()
    
    if admin:
        # Reset admin password
        admin.password_hash = generate_password_hash('Admin123!')
        db.session.commit()
        print("Admin password reset to 'Admin123!'")
    else:
        # Create admin if it doesn't exist
        admin = User(
            username='admin',
            email='admin@Mobile.com',
            password_hash=generate_password_hash('Admin123!'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created with username: 'admin' and password: 'Admin123!'")
