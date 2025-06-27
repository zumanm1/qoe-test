from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_cors import CORS
from config import config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
socketio = SocketIO()
cors = CORS()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins="*")
    cors.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.views.auth import auth_bp
    from app.views.dashboard import dashboard_bp
    from app.views.troubleshooting import troubleshooting_bp
    from app.views.qoe_impact import qoe_impact_bp
    app.register_blueprint(qoe_impact_bp, url_prefix='/feature04')

    from app.views.technical_deep_dive import technical_deep_dive_bp
    app.register_blueprint(technical_deep_dive_bp, url_prefix='/feature04')
    from app.views.simulation import simulation_bp
    from app.views.reports import reports_bp
    from app.views.main import main_bp
    from app.views.docs import docs_bp
    from app.views.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(simulation_bp, url_prefix='/simulation')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(troubleshooting_bp, url_prefix='/troubleshooting')
    app.register_blueprint(docs_bp, url_prefix='/docs')
    
    # Register error handlers
    from app.errors import register_error_handlers
    register_error_handlers(app)
    
    # Register context processors
    from app.context_processors import inject_current_year
    app.context_processor(inject_current_year)

    # Register CLI commands
    from app.cli import register_commands
    register_commands(app)
    
    return app
