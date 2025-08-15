from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Search(db.Model):
    """Modèle pour les recherches d'emploi configurées par l'utilisateur"""
    __tablename__ = 'searches'
    
    id = db.Column(db.Integer, primary_key=True)
    keywords = db.Column(db.String(200), nullable=False, index=True)
    job_types = db.Column(db.Text, nullable=False)  # JSON array: ["alternance", "stage"]
    duration_minutes = db.Column(db.Integer, default=15, nullable=False)
    platforms = db.Column(db.Text, nullable=False)  # JSON array: ["indeed", "linkedin"]
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relation vers les jobs trouvés
    jobs = db.relationship('Job', backref='search', lazy=True, cascade='all, delete-orphan')
    execution_logs = db.relationship('ExecutionLog', backref='search', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, keywords, job_types, platforms, duration_minutes=15):
        self.keywords = keywords
        self.job_types = json.dumps(job_types) if isinstance(job_types, list) else job_types
        self.platforms = json.dumps(platforms) if isinstance(platforms, list) else platforms
        self.duration_minutes = duration_minutes
    
    @property
    def job_types_list(self):
        """Retourne la liste des types d'emploi"""
        try:
            return json.loads(self.job_types)
        except (json.JSONDecodeError, TypeError):
            return []
    
    @property
    def platforms_list(self):
        """Retourne la liste des plateformes"""
        try:
            return json.loads(self.platforms)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            'id': self.id,
            'keywords': self.keywords,
            'job_types': self.job_types_list,
            'duration_minutes': self.duration_minutes,
            'platforms': self.platforms_list,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'total_jobs': len(self.jobs)
        }
    
    def __repr__(self):
        return f'<Search {self.id}: {self.keywords}>'


class Job(db.Model):
    """Modèle pour les offres d'emploi trouvées"""
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    search_id = db.Column(db.Integer, db.ForeignKey('searches.id'), nullable=False, index=True)
    title = db.Column(db.String(300), nullable=False, index=True)
    company = db.Column(db.String(200), index=True)
    url = db.Column(db.Text, nullable=False, unique=True)
    platform = db.Column(db.String(50), nullable=False, index=True)
    location = db.Column(db.String(200))
    description_snippet = db.Column(db.Text)  # Extrait de la description
    salary_info = db.Column(db.String(200))  # Information sur le salaire si disponible
    job_type = db.Column(db.String(100))  # CDI, CDD, Alternance, Stage, etc.
    date_posted = db.Column(db.DateTime, index=True)  # Date de publication sur la plateforme
    date_found = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    is_new = db.Column(db.Boolean, default=True, nullable=False, index=True)
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            'id': self.id,
            'search_id': self.search_id,
            'title': self.title,
            'company': self.company,
            'url': self.url,
            'platform': self.platform,
            'location': self.location,
            'description_snippet': self.description_snippet,
            'salary_info': self.salary_info,
            'job_type': self.job_type,
            'date_posted': self.date_posted.isoformat() if self.date_posted else None,
            'date_found': self.date_found.isoformat() if self.date_found else None,
            'is_new': self.is_new
        }
    
    def __repr__(self):
        return f'<Job {self.id}: {self.title} at {self.company}>'


class ExecutionLog(db.Model):
    """Modèle pour les logs d'exécution des scrapers"""
    __tablename__ = 'execution_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    search_id = db.Column(db.Integer, db.ForeignKey('searches.id'), nullable=False, index=True)
    platform = db.Column(db.String(50), nullable=False, index=True)
    jobs_found = db.Column(db.Integer, default=0, nullable=False)
    new_jobs_found = db.Column(db.Integer, default=0, nullable=False)
    execution_time = db.Column(db.Float)  # Temps d'exécution en secondes
    status = db.Column(db.String(20), nullable=False, index=True)  # 'success', 'error', 'partial'
    error_message = db.Column(db.Text)
    executed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            'id': self.id,
            'search_id': self.search_id,
            'platform': self.platform,
            'jobs_found': self.jobs_found,
            'new_jobs_found': self.new_jobs_found,
            'execution_time': self.execution_time,
            'status': self.status,
            'error_message': self.error_message,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None
        }
    
    def __repr__(self):
        return f'<ExecutionLog {self.id}: {self.platform} - {self.status}>'


class JobMetrics(db.Model):
    """Modèle pour stocker des métriques agrégées (optionnel, pour optimisation)"""
    __tablename__ = 'job_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    platform = db.Column(db.String(50), nullable=False, index=True)
    total_jobs_scraped = db.Column(db.Integer, default=0)
    total_new_jobs = db.Column(db.Integer, default=0)
    total_searches = db.Column(db.Integer, default=0)
    avg_execution_time = db.Column(db.Float)
    success_rate = db.Column(db.Float)  # Pourcentage de succès
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'platform': self.platform,
            'total_jobs_scraped': self.total_jobs_scraped,
            'total_new_jobs': self.total_new_jobs,
            'total_searches': self.total_searches,
            'avg_execution_time': self.avg_execution_time,
            'success_rate': self.success_rate,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<JobMetrics {self.date} - {self.platform}>'
