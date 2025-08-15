import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

class Config:
    """Configuration de base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration APScheduler
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = 'Europe/Paris'
    
    # Configuration scraping
    SCRAPING_INTERVAL_MINUTES = int(os.environ.get('SCRAPING_INTERVAL_MINUTES', 15))
    MAX_CONCURRENT_SCRAPERS = int(os.environ.get('MAX_CONCURRENT_SCRAPERS', 3))
    REQUEST_DELAY_SECONDS = float(os.environ.get('REQUEST_DELAY_SECONDS', 1.5))
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')

class DevelopmentConfig(Config):
    """Configuration pour développement"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///jobhub_dev.db'
    
class TestingConfig(Config):
    """Configuration pour tests"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Configuration pour production"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///jobhub.db'
    
    # En production, utiliser une clé secrète forte
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for production environment")

# Dictionnaire des configurations
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
