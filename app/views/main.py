from flask import Blueprint, render_template, redirect, url_for, jsonify
from app import db
import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Serve the index page."""
    return render_template('index.html')

@main_bp.route('/home')
def home():
    """Redirect to index."""
    return redirect(url_for('main.index'))

@main_bp.route('/health')
def health_check():
    """Health check endpoint for load balancers and monitoring."""
    try:
        # Check database connectivity
        db.session.execute('SELECT 1')
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
    
    health_data = {
        'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'database': db_status,
        'version': '1.0.0'  # Update this with your app version
    }
    
    status_code = 200 if health_data['status'] == 'healthy' else 503
    return jsonify(health_data), status_code
