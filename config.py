import os
from datetime import timedelta

class Config:
    # Basic Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'Mobile_qoe.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Flask-Login
    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # WebSocket
    SOCKETIO_ASYNC_MODE = 'threading'
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"
    
    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Performance Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year cache for static files
    
    # Application Settings
    ITEMS_PER_PAGE = 20
    MAX_SEARCH_RESULTS = 100
    KPI_UPDATE_INTERVAL = 1  # seconds
    ALERT_CHECK_INTERVAL = 60  # seconds
    
class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False  # For development without HTTPS
    REMEMBER_COOKIE_SECURE = False  # For development without HTTPS
    
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
