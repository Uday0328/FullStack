import os


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-fallback-secret-key-change-me'
    
    # Fallback SQLite DB path for serverless platforms (e.g. Vercel)
    if os.environ.get('VERCEL'):
        DATABASE_PATH = '/tmp/portfolio.db'
    else:
        DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'portfolio.db')

    SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'schema.sql')
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'Admin@2026'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    WTF_CSRF_ENABLED = True


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
