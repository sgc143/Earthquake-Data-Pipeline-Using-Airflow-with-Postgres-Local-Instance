import os

class Config:
    """Configuration class for the application."""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Build from individual components
        PGHOST = os.environ.get('PGHOST', 'localhost')
        PGPORT = os.environ.get('PGPORT', '5432')
        PGUSER = os.environ.get('PGUSER', 'postgres')
        PGPASSWORD = os.environ.get('PGPASSWORD', 'postgres')
        PGDATABASE = os.environ.get('PGDATABASE', 'earthquake_data')
        
        SQLALCHEMY_DATABASE_URI = f'postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}'
    
    # SQLAlchemy Configuration
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
