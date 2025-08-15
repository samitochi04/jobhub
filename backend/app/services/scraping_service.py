#!/usr/bin/env python3
"""
Service de scraping automatique avec APScheduler
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from app.models import db, Search, Job, ExecutionLog
from app.utils.database import DatabaseUtils
from app.scrapers import ScraperManager, ScrapingError

logger = logging.getLogger(__name__)

class ScrapingService:
    """Service principal de scraping automatique"""
    
    def __init__(self, app=None):
        self.app = app
        self.scheduler = None
        self.scraper_manager = ScraperManager()
        self.is_running = False
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialise le service avec l'application Flask"""
        self.app = app
        
        # Configuration du scheduler
        jobstores = {
            'default': SQLAlchemyJobStore(url=app.config['SQLALCHEMY_DATABASE_URI'])
        }
        
        job_defaults = {
            'coalesce': True,
            'max_instances': 3,
            'misfire_grace_time': 300  # 5 minutes
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            job_defaults=job_defaults,
            timezone=app.config.get('SCHEDULER_TIMEZONE', 'Europe/Paris')
        )
    
    def start(self):
        """Démarre le scheduler"""
        if not self.scheduler:
            raise RuntimeError("ScrapingService not initialized with app")
        
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("🚀 Scraping scheduler started")
            
            # Programmer les recherches existantes
            self._schedule_existing_searches()
        else:
            logger.warning("Scheduler is already running")
    
    def stop(self):
        """Arrête le scheduler"""
        if self.scheduler and self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("⏹️ Scraping scheduler stopped")
    
    def _schedule_existing_searches(self):
        """Programme toutes les recherches actives existantes"""
        with self.app.app_context():
            active_searches = Search.query.filter_by(is_active=True).all()
            
            for search in active_searches:
                self.schedule_search(search.id)
                logger.info(f"📅 Scheduled search {search.id}: '{search.keywords}'")
    
    def schedule_search(self, search_id: int) -> bool:
        """
        Programme une recherche pour exécution automatique
        
        Args:
            search_id: ID de la recherche à programmer
        
        Returns:
            True si programmée avec succès
        """
        try:
            with self.app.app_context():
                search = Search.query.get(search_id)
                if not search or not search.is_active:
                    logger.warning(f"Search {search_id} not found or inactive")
                    return False
                
                job_id = f"search_{search_id}"
                
                # Supprimer job existant s'il y en a un
                try:
                    self.scheduler.remove_job(job_id)
                except:
                    pass
                
                # Créer nouveau job
                trigger = IntervalTrigger(minutes=search.duration_minutes)
                self.scheduler.add_job(
                    func=self._execute_search,
                    trigger=trigger,
                    args=[search_id],
                    id=job_id,
                    name=f"Search: {search.keywords}",
                    replace_existing=True
                )
                
                logger.info(f"✅ Scheduled search {search_id} every {search.duration_minutes} minutes")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to schedule search {search_id}: {e}")
            return False
    
    def unschedule_search(self, search_id: int) -> bool:
        """Annule la programmation d'une recherche"""
        try:
            job_id = f"search_{search_id}"
            self.scheduler.remove_job(job_id)
            logger.info(f"🗑️ Unscheduled search {search_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to unschedule search {search_id}: {e}")
            return False
    
    def _execute_search(self, search_id: int):
        """
        Exécute une recherche de scraping
        
        Args:
            search_id: ID de la recherche à exécuter
        """
        execution_start = datetime.now()
        
        with self.app.app_context():
            try:
                search = Search.query.get(search_id)
                if not search or not search.is_active:
                    logger.warning(f"Search {search_id} no longer active, skipping")
                    return
                
                logger.info(f"🔍 Executing search {search_id}: '{search.keywords}'")
                
                # Obtenir la date de dernière exécution pour éviter les doublons
                last_execution = ExecutionLog.query.filter_by(
                    search_id=search_id
                ).order_by(ExecutionLog.executed_at.desc()).first()
                
                since_date = None
                if last_execution:
                    # Chercher uniquement les offres plus récentes que la dernière exécution
                    since_date = last_execution.executed_at - timedelta(hours=1)  # Marge de sécurité
                
                # Parser les types d'emploi et plateformes
                job_types = search.job_types_list
                platforms = search.platforms_list
                
                total_new_jobs = 0
                total_jobs_found = 0
                
                # Scraper chaque plateforme
                for platform in platforms:
                    try:
                        platform_jobs = self._scrape_platform(
                            platform, search.keywords, job_types, since_date
                        )
                        
                        if platform_jobs:
                            new_jobs = self._save_jobs(platform_jobs, search_id)
                            total_jobs_found += len(platform_jobs)
                            total_new_jobs += new_jobs
                            
                            # Log d'exécution par plateforme
                            self._log_execution(
                                search_id, platform, len(platform_jobs), new_jobs,
                                'success', execution_start
                            )
                            
                            logger.info(f"✅ {platform}: {len(platform_jobs)} found, {new_jobs} new")
                        else:
                            # Log même si aucun job trouvé
                            self._log_execution(
                                search_id, platform, 0, 0, 'success', execution_start
                            )
                            
                    except Exception as e:
                        logger.error(f"❌ Error scraping {platform}: {e}")
                        self._log_execution(
                            search_id, platform, 0, 0, 'error', execution_start, str(e)
                        )
                
                execution_time = (datetime.now() - execution_start).total_seconds()
                logger.info(f"🎯 Search {search_id} completed: {total_new_jobs} new jobs in {execution_time:.1f}s")
                
            except Exception as e:
                logger.error(f"💥 Critical error in search execution {search_id}: {e}")
                # Log d'erreur critique
                self._log_execution(
                    search_id, 'system', 0, 0, 'error', execution_start, str(e)
                )
    
    def _scrape_platform(self, platform: str, keywords: str, job_types: List[str], 
                        since_date: datetime = None) -> List[Dict]:
        """Scrape une plateforme spécifique"""
        try:
            scraper = self.scraper_manager.get_scraper(platform)
            
            jobs = scraper.scrape_jobs(
                keywords=keywords,
                job_types=job_types,
                limit=50,  # Configurable
                since_date=since_date
            )
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping {platform}: {e}")
            raise ScrapingError(f"Failed to scrape {platform}: {e}")
    
    def _save_jobs(self, jobs: List[Dict], search_id: int) -> int:
        """
        Sauvegarde les jobs en base et retourne le nombre de nouveaux jobs
        
        Returns:
            Nombre de nouveaux jobs ajoutés
        """
        new_jobs_count = 0
        
        for job_data in jobs:
            try:
                # Vérifier si le job existe déjà par URL
                existing_job = Job.query.filter_by(url=job_data.get('url')).first()
                
                if not existing_job:
                    # Créer nouveau job
                    job = Job(
                        search_id=search_id,
                        title=job_data.get('title', ''),
                        company=job_data.get('company', ''),
                        url=job_data.get('url', ''),
                        platform=job_data.get('platform', ''),
                        location=job_data.get('location'),
                        job_type=job_data.get('job_type'),
                        description_snippet=job_data.get('description_snippet'),
                        salary=job_data.get('salary'),
                        date_posted=job_data.get('date_posted', datetime.now()),
                        external_id=job_data.get('external_id'),
                        is_new=True
                    )
                    
                    db.session.add(job)
                    new_jobs_count += 1
                
            except Exception as e:
                logger.error(f"Error saving job: {e}")
                continue
        
        try:
            db.session.commit()
            logger.info(f"💾 Saved {new_jobs_count} new jobs to database")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Database error: {e}")
            new_jobs_count = 0
        
        return new_jobs_count
    
    def _log_execution(self, search_id: int, platform: str, jobs_found: int, 
                      new_jobs: int, status: str, start_time: datetime, 
                      error_message: str = None):
        """Enregistre un log d'exécution"""
        try:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            log = ExecutionLog(
                search_id=search_id,
                platform=platform,
                jobs_found=jobs_found,
                new_jobs_found=new_jobs,
                execution_time=execution_time,
                status=status,
                error_message=error_message
            )
            
            db.session.add(log)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to log execution: {e}")
            db.session.rollback()
    
    def execute_search_now(self, search_id: int) -> Dict:
        """
        Exécute immédiatement une recherche (pour test/debug)
        
        Returns:
            Résultats de l'exécution
        """
        start_time = datetime.now()
        
        try:
            self._execute_search(search_id)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'success': True,
                'execution_time': execution_time,
                'message': f'Search {search_id} executed successfully'
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Manual execution failed for search {search_id}: {e}")
            
            return {
                'success': False,
                'execution_time': execution_time,
                'error': str(e)
            }
    
    def get_status(self) -> Dict:
        """Retourne le statut du service"""
        return {
            'running': self.is_running,
            'scheduled_jobs': len(self.scheduler.get_jobs()) if self.scheduler else 0,
            'available_scrapers': list(self.scraper_manager.scrapers.keys()),
            'scraper_connections': self.scraper_manager.test_all_connections() if self.scraper_manager else {}
        }
    
    def get_scheduled_jobs(self) -> List[Dict]:
        """Retourne la liste des jobs programmés"""
        if not self.scheduler:
            return []
        
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        
        return jobs
