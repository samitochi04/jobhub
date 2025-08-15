from app.models import db, Search, Job, ExecutionLog, JobMetrics
from datetime import datetime, timedelta
from sqlalchemy import func, and_

class DatabaseUtils:
    """Utilitaires pour les opérations de base de données"""
    
    @staticmethod
    def create_search(keywords, job_types, platforms, duration_minutes=15):
        """Crée une nouvelle recherche"""
        try:
            search = Search(
                keywords=keywords,
                job_types=job_types,
                platforms=platforms,
                duration_minutes=duration_minutes
            )
            db.session.add(search)
            db.session.commit()
            return search
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_active_searches():
        """Récupère toutes les recherches actives"""
        return Search.query.filter_by(is_active=True).all()
    
    @staticmethod
    def get_search_by_id(search_id):
        """Récupère une recherche par son ID"""
        return Search.query.get(search_id)
    
    @staticmethod
    def deactivate_search(search_id):
        """Désactive une recherche"""
        try:
            search = Search.query.get(search_id)
            if search:
                search.is_active = False
                search.updated_at = datetime.utcnow()
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def add_job(search_id, title, company, url, platform, **kwargs):
        """Ajoute une nouvelle offre d'emploi"""
        try:
            # Vérifier si l'offre existe déjà
            existing_job = Job.query.filter_by(url=url).first()
            if existing_job:
                return None, False  # Offre déjà existante
            
            job = Job(
                search_id=search_id,
                title=title,
                company=company,
                url=url,
                platform=platform,
                location=kwargs.get('location'),
                description_snippet=kwargs.get('description_snippet'),
                salary_info=kwargs.get('salary_info'),
                job_type=kwargs.get('job_type'),
                date_posted=kwargs.get('date_posted')
            )
            db.session.add(job)
            db.session.commit()
            return job, True  # Nouvelle offre ajoutée
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_jobs_for_search(search_id, limit=50, new_only=False):
        """Récupère les offres pour une recherche donnée"""
        query = Job.query.filter_by(search_id=search_id)
        
        if new_only:
            query = query.filter_by(is_new=True)
        
        return query.order_by(Job.date_found.desc()).limit(limit).all()
    
    @staticmethod
    def get_recent_jobs(hours=24, limit=100):
        """Récupère les offres récentes (dernières X heures)"""
        since = datetime.utcnow() - timedelta(hours=hours)
        return Job.query.filter(Job.date_found >= since)\
                      .order_by(Job.date_found.desc())\
                      .limit(limit).all()
    
    @staticmethod
    def mark_jobs_as_seen(search_id):
        """Marque toutes les offres d'une recherche comme vues (is_new=False)"""
        try:
            Job.query.filter_by(search_id=search_id, is_new=True)\
                    .update({Job.is_new: False})
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def log_execution(search_id, platform, jobs_found=0, new_jobs_found=0, 
                     execution_time=None, status='success', error_message=None):
        """Enregistre un log d'exécution"""
        try:
            log = ExecutionLog(
                search_id=search_id,
                platform=platform,
                jobs_found=jobs_found,
                new_jobs_found=new_jobs_found,
                execution_time=execution_time,
                status=status,
                error_message=error_message
            )
            db.session.add(log)
            db.session.commit()
            return log
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_search_stats(search_id):
        """Récupère les statistiques pour une recherche"""
        search = Search.query.get(search_id)
        if not search:
            return None
        
        total_jobs = Job.query.filter_by(search_id=search_id).count()
        new_jobs = Job.query.filter_by(search_id=search_id, is_new=True).count()
        
        # Statistiques par plateforme
        platform_stats = db.session.query(
            Job.platform,
            func.count(Job.id).label('count')
        ).filter_by(search_id=search_id)\
         .group_by(Job.platform).all()
        
        # Dernière exécution
        last_execution = ExecutionLog.query.filter_by(search_id=search_id)\
                                         .order_by(ExecutionLog.executed_at.desc())\
                                         .first()
        
        return {
            'search_id': search_id,
            'total_jobs': total_jobs,
            'new_jobs': new_jobs,
            'platform_stats': [{'platform': stat[0], 'count': stat[1]} 
                             for stat in platform_stats],
            'last_execution': last_execution.to_dict() if last_execution else None,
            'is_active': search.is_active
        }
    
    @staticmethod
    def get_dashboard_stats():
        """Récupère les statistiques globales pour le dashboard"""
        total_searches = Search.query.count()
        active_searches = Search.query.filter_by(is_active=True).count()
        total_jobs = Job.query.count()
        new_jobs = Job.query.filter_by(is_new=True).count()
        
        # Jobs des dernières 24h
        since_24h = datetime.utcnow() - timedelta(hours=24)
        jobs_24h = Job.query.filter(Job.date_found >= since_24h).count()
        
        # Statistiques par plateforme
        platform_stats = db.session.query(
            Job.platform,
            func.count(Job.id).label('total'),
            func.sum(func.cast(Job.is_new, db.Integer)).label('new')
        ).group_by(Job.platform).all()
        
        return {
            'total_searches': total_searches,
            'active_searches': active_searches,
            'total_jobs': total_jobs,
            'new_jobs': new_jobs,
            'jobs_24h': jobs_24h,
            'platform_stats': [
                {
                    'platform': stat[0], 
                    'total': stat[1], 
                    'new': stat[2] or 0
                } 
                for stat in platform_stats
            ]
        }
    
    @staticmethod
    def cleanup_old_logs(days=30):
        """Nettoie les anciens logs d'exécution"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            deleted = ExecutionLog.query.filter(ExecutionLog.executed_at < cutoff_date).delete()
            db.session.commit()
            return deleted
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_job_trends(days=7):
        """Récupère les tendances des offres sur les derniers jours"""
        since = datetime.utcnow() - timedelta(days=days)
        
        # Grouper par jour
        trends = db.session.query(
            func.date(Job.date_found).label('date'),
            func.count(Job.id).label('count'),
            Job.platform
        ).filter(Job.date_found >= since)\
         .group_by(func.date(Job.date_found), Job.platform)\
         .order_by(func.date(Job.date_found).desc()).all()
        
        return [
            {
                'date': trend[0].strftime('%Y-%m-%d') if trend[0] else None,
                'count': trend[1],
                'platform': trend[2]
            }
            for trend in trends
        ]
