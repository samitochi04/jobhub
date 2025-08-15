from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from app.models import db
from config import config
import os

migrate = Migrate()

def create_app(config_name=None):
    """Factory pour créer l'application Flask"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialiser les extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Enregistrer les blueprints (routes)
    from app.routes import search_bp, jobs_bp, status_bp
    app.register_blueprint(search_bp, url_prefix='/api')
    app.register_blueprint(jobs_bp, url_prefix='/api')
    app.register_blueprint(status_bp, url_prefix='/api')
    
    # Route de santé
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'JobHub API is running'}, 200
    
    # Créer les tables si elles n'existent pas
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"❌ Error creating database tables: {e}")
    
    return app
