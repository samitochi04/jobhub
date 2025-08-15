from flask import Blueprint

# Import des blueprints
from .search import search_bp
from .jobs import jobs_bp  
from .status import status_bp

# Exporter les blueprints
__all__ = ['search_bp', 'jobs_bp', 'status_bp']
