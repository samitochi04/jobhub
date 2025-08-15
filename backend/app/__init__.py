from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from app.models import db
from config import config
import os
import logging
import atexit

migrate = Migrate()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_name=None):
    """Factory pour créer l'application Flask"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialiser les extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, 
         origins=["http://localhost:5173"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization"])
    
    # Initialiser le service de scraping
    try:
        from app.services.scraping_service import ScrapingService
        from app.routes.scraping_routes import init_scraping_service
        
        scraping_service = ScrapingService(app)
        init_scraping_service(scraping_service)
        
        # Arrêter le service proprement à la fermeture
        def shutdown_scraping():
            try:
                scraping_service.stop()
                logger.info("⏹️ Scraping service stopped")
            except:
                pass
        
        atexit.register(shutdown_scraping)
        
    except ImportError as e:
        logger.warning(f"⚠️ Scraping service not available: {e}")
        scraping_service = None
    
    # Enregistrer les blueprints (routes)
    from app.routes import search_bp, jobs_bp, status_bp
    app.register_blueprint(search_bp, url_prefix='/api')
    app.register_blueprint(jobs_bp, url_prefix='/api')
    app.register_blueprint(status_bp, url_prefix='/api')
    
    # Injecter le service de scraping dans les routes de recherche
    if scraping_service:
        from app.routes.search import set_scraping_service
        set_scraping_service(scraping_service)
    
    # Enregistrer les routes de scraping si disponibles
    if scraping_service:
        try:
            from app.routes.scraping_routes import scraping_bp
            app.register_blueprint(scraping_bp, url_prefix='/api/scraping')
            logger.info("✅ Scraping routes registered")
        except ImportError:
            logger.warning("⚠️ Scraping routes not available")
    
    # Route de santé
    @app.route('/health')
    def health_check():
        scraping_status = None
        if scraping_service:
            try:
                scraping_status = scraping_service.get_status()
            except:
                scraping_status = {'error': 'Service unavailable'}
        
        return {
            'status': 'healthy', 
            'message': 'JobHub API is running',
            'scraping': scraping_status
        }, 200
    
    # Créer les tables si elles n'existent pas
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Démarrer le scraping service après l'initialisation
            if scraping_service:
                try:
                    scraping_service.start()
                    logger.info("✅ Scraping service started automatically")
                except Exception as e:
                    logger.error(f"❌ Failed to start scraping service: {e}")
                    
        except Exception as e:
            print(f"❌ Error creating database tables: {e}")
    
    return app
