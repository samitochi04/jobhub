#!/usr/bin/env python3
"""
Routes pour le contrôle du système de scraping
"""
from flask import Blueprint, jsonify, request
from app.services.scraping_service import ScrapingService
from app.models import Search, ExecutionLog, Job
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

scraping_bp = Blueprint('scraping', __name__)

# Instance globale du service (sera initialisée dans app.py)
scraping_service = None

def init_scraping_service(service):
    """Initialise le service de scraping"""
    global scraping_service
    scraping_service = service

@scraping_bp.route('/status', methods=['GET'])
def get_scraping_status():
    """Retourne le statut du système de scraping"""
    try:
        if not scraping_service:
            return jsonify({
                'error': 'Scraping service not initialized',
                'running': False
            }), 503
        
        status = scraping_service.get_status()
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting scraping status: {e}")
        return jsonify({'error': str(e)}), 500

@scraping_bp.route('/start', methods=['POST'])
def start_scraping():
    """Démarre le système de scraping"""
    try:
        if not scraping_service:
            return jsonify({'error': 'Scraping service not initialized'}), 503
        
        scraping_service.start()
        
        return jsonify({
            'message': 'Scraping service started successfully',
            'status': 'running'
        })
        
    except Exception as e:
        logger.error(f"Error starting scraping service: {e}")
        return jsonify({'error': str(e)}), 500

@scraping_bp.route('/stop', methods=['POST'])
def stop_scraping():
    """Arrête le système de scraping"""
    try:
        if not scraping_service:
            return jsonify({'error': 'Scraping service not initialized'}), 503
        
        scraping_service.stop()
        
        return jsonify({
            'message': 'Scraping service stopped successfully',
            'status': 'stopped'
        })
        
    except Exception as e:
        logger.error(f"Error stopping scraping service: {e}")
        return jsonify({'error': str(e)}), 500

@scraping_bp.route('/jobs', methods=['GET'])
def get_scheduled_jobs():
    """Retourne la liste des jobs programmés"""
    try:
        if not scraping_service:
            return jsonify({'error': 'Scraping service not initialized'}), 503
        
        jobs = scraping_service.get_scheduled_jobs()
        return jsonify({'jobs': jobs})
        
    except Exception as e:
        logger.error(f"Error getting scheduled jobs: {e}")
        return jsonify({'error': str(e)}), 500

@scraping_bp.route('/search/<int:search_id>/schedule', methods=['POST'])
def schedule_search(search_id):
    """Programme une recherche pour exécution automatique"""
    try:
        if not scraping_service:
            return jsonify({'error': 'Scraping service not initialized'}), 503
        
        search = Search.query.get_or_404(search_id)
        
        success = scraping_service.schedule_search(search_id)
        
        if success:
            return jsonify({
                'message': f'Search "{search.keywords}" scheduled successfully',
                'search_id': search_id
            })
        else:
            return jsonify({
                'error': 'Failed to schedule search'
            }), 500
            
    except Exception as e:
        logger.error(f"Error scheduling search {search_id}: {e}")
        return jsonify({'error': str(e)}), 500

@scraping_bp.route('/search/<int:search_id>/unschedule', methods=['POST'])
def unschedule_search(search_id):
    """Annule la programmation d'une recherche"""
    try:
        if not scraping_service:
            return jsonify({'error': 'Scraping service not initialized'}), 503
        
        search = Search.query.get_or_404(search_id)
        
        success = scraping_service.unschedule_search(search_id)
        
        if success:
            return jsonify({
                'message': f'Search "{search.keywords}" unscheduled successfully',
                'search_id': search_id
            })
        else:
            return jsonify({
                'error': 'Failed to unschedule search'
            }), 500
            
    except Exception as e:
        logger.error(f"Error unscheduling search {search_id}: {e}")
        return jsonify({'error': str(e)}), 500

@scraping_bp.route('/search/<int:search_id>/execute', methods=['POST'])
def execute_search_now(search_id):
    """Exécute immédiatement une recherche"""
    try:
        if not scraping_service:
            return jsonify({'error': 'Scraping service not initialized'}), 503
        
        search = Search.query.get_or_404(search_id)
        
        result = scraping_service.execute_search_now(search_id)
        
        if result['success']:
            return jsonify({
                'message': f'Search "{search.keywords}" executed successfully',
                'execution_time': result['execution_time'],
                'search_id': search_id
            })
        else:
            return jsonify({
                'error': result['error'],
                'execution_time': result['execution_time']
            }), 500
            
    except Exception as e:
        logger.error(f"Error executing search {search_id}: {e}")
        return jsonify({'error': str(e)}), 500

@scraping_bp.route('/search/<int:search_id>/logs', methods=['GET'])
def get_search_logs(search_id):
    """Retourne les logs d'exécution d'une recherche"""
    try:
        search = Search.query.get_or_404(search_id)
        
        # Paramètres de pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Filtre par date (optionnel)
        days = request.args.get('days', 7, type=int)
        since_date = datetime.now() - timedelta(days=days)
        
        # Query avec pagination
        logs_query = ExecutionLog.query.filter_by(search_id=search_id)\
            .filter(ExecutionLog.executed_at >= since_date)\
            .order_by(ExecutionLog.executed_at.desc())
        
        logs_pagination = logs_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        logs_data = []
        for log in logs_pagination.items:
            logs_data.append({
                'id': log.id,
                'platform': log.platform,
                'jobs_found': log.jobs_found,
                'new_jobs_found': log.new_jobs_found,
                'execution_time': log.execution_time,
                'status': log.status,
                'error_message': log.error_message,
                'executed_at': log.executed_at.isoformat()
            })
        
        return jsonify({
            'logs': logs_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': logs_pagination.total,
                'pages': logs_pagination.pages,
                'has_next': logs_pagination.has_next,
                'has_prev': logs_pagination.has_prev
            },
            'search': {
                'id': search.id,
                'keywords': search.keywords,
                'is_active': search.is_active
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting logs for search {search_id}: {e}")
        return jsonify({'error': str(e)}), 500

@scraping_bp.route('/stats', methods=['GET'])
def get_scraping_stats():
    """Retourne des statistiques de scraping"""
    try:
        # Paramètres de période
        days = request.args.get('days', 7, type=int)
        since_date = datetime.now() - timedelta(days=days)
        
        # Statistiques générales
        total_searches = Search.query.filter_by(is_active=True).count()
        total_jobs = Job.query.count()
        
        # Statistiques récentes
        recent_logs = ExecutionLog.query.filter(
            ExecutionLog.executed_at >= since_date
        ).all()
        
        recent_executions = len(recent_logs)
        recent_jobs_found = sum(log.jobs_found for log in recent_logs)
        recent_new_jobs = sum(log.new_jobs_found for log in recent_logs)
        
        # Statistiques par plateforme
        platform_stats = {}
        for log in recent_logs:
            if log.platform not in platform_stats:
                platform_stats[log.platform] = {
                    'executions': 0,
                    'jobs_found': 0,
                    'new_jobs': 0,
                    'success_rate': 0,
                    'avg_execution_time': 0
                }
            
            stats = platform_stats[log.platform]
            stats['executions'] += 1
            stats['jobs_found'] += log.jobs_found
            stats['new_jobs'] += log.new_jobs_found
            
            if log.status == 'success':
                stats['success_rate'] += 1
        
        # Calculer les moyennes
        for platform, stats in platform_stats.items():
            if stats['executions'] > 0:
                stats['success_rate'] = (stats['success_rate'] / stats['executions']) * 100
                
                # Moyenne du temps d'exécution
                platform_logs = [log for log in recent_logs if log.platform == platform]
                if platform_logs:
                    stats['avg_execution_time'] = sum(
                        log.execution_time for log in platform_logs
                    ) / len(platform_logs)
        
        # Jobs récents par recherche
        search_stats = []
        active_searches = Search.query.filter_by(is_active=True).all()
        
        for search in active_searches:
            search_logs = [log for log in recent_logs if log.search_id == search.id]
            search_jobs = Job.query.filter_by(search_id=search.id)\
                .filter(Job.created_at >= since_date).count()
            
            search_stats.append({
                'search_id': search.id,
                'keywords': search.keywords,
                'executions': len(search_logs),
                'new_jobs': search_jobs,
                'last_execution': max(
                    (log.executed_at.isoformat() for log in search_logs),
                    default=None
                )
            })
        
        return jsonify({
            'period_days': days,
            'general_stats': {
                'total_active_searches': total_searches,
                'total_jobs': total_jobs,
                'recent_executions': recent_executions,
                'recent_jobs_found': recent_jobs_found,
                'recent_new_jobs': recent_new_jobs
            },
            'platform_stats': platform_stats,
            'search_stats': search_stats,
            'service_status': scraping_service.get_status() if scraping_service else None
        })
        
    except Exception as e:
        logger.error(f"Error getting scraping stats: {e}")
        return jsonify({'error': str(e)}), 500

@scraping_bp.route('/test-connection', methods=['POST'])
def test_scrapers_connection():
    """Test la connexion aux différents scrapers"""
    try:
        if not scraping_service:
            return jsonify({'error': 'Scraping service not initialized'}), 503
        
        connections = scraping_service.scraper_manager.test_all_connections()
        
        return jsonify({
            'connections': connections,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error testing scraper connections: {e}")
        return jsonify({'error': str(e)}), 500
