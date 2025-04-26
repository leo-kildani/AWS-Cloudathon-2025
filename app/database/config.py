# config.py
import os

# Basic configuration
SECRET_KEY = os.urandom(24) # Used for session management, etc.

# Database configuration (Local PostgreSQL)
# Replace with your local database details
DB_USERNAME = 'your_local_db_user'
DB_PASSWORD = 'your_local_db_password'
DB_HOST = 'localhost' # Or '127.0.0.1'
DB_PORT = '5432' # Default PostgreSQL port
DB_NAME = 'flight_mvp_db' # The database you created

# Construct the SQLAlchemy Database URI
SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Optional: Disable modification tracking if not needed (improves performance)
SQLALCHEMY_TRACK_MODIFICATIONS = False