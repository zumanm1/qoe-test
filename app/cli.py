import click
from werkzeug.security import generate_password_hash
from app import db
from app.models.user import User
from datetime import datetime

def register_commands(app):
    """Register Click commands for the application."""
    
    @app.cli.command('create-admin')
    @click.argument('username')
    @click.argument('email')
    @click.argument('password')
    def create_admin(username, email, password):
        """Create an admin user for manual use."""
        if User.query.filter_by(username=username).first():
            click.echo(f'Error: Admin user {username} already exists.')
            return
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role='admin',
            created_at=datetime.utcnow()
        )
        db.session.add(user)
        db.session.commit()
        click.echo(f'Admin user {username} created successfully.')
        
    @app.cli.command('init-db')
    def init_db():
        """Initialize the database with required tables."""
        db.create_all()
        click.echo('Database initialized.')
        
    @app.cli.command('clean-db')
    @click.confirmation_option(prompt='Are you sure you want to drop all tables? This will delete ALL data!')
    def clean_db():
        """Drop all tables and remove all data from the database."""
        db.drop_all()
        click.echo('Database cleared - all tables dropped.')
