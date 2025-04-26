# config.py
import os
from datetime import timedelta

# Basic configuration
SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32)  # 32 bytes for better security
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or os.urandom(32)

# Security headers configuration
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',') or []
SECURITY_HEADERS = {
    'force_https': True,
    'strict_transport_security': True,
    'session_cookie_secure': True,
    'content_security_policy': {
        'default-src': "'self'",
        'script-src': "'self'",
        'style-src': "'self'",
    }
}

# Rate limiting configuration
RATE_LIMITS = {
    'default': "200 per day, 50 per hour",
    'auth': "10 per minute",
    'sensitive': "5 per minute"
}

# Database configuration (consider using environment variables for production)
DB_USERNAME = os.environ.get('DB_USERNAME', 'your_local_db_user')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'your_local_db_password')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'flight_mvp_db')

# Construct the SQLAlchemy Database URI
SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Disable modification tracking
SQLALCHEMY_TRACK_MODIFICATIONS = False

# JWT configuration
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
JWT_TOKEN_LOCATION = ['headers', 'cookies']
JWT_COOKIE_SECURE = True
JWT_COOKIE_CSRF_PROTECT = True