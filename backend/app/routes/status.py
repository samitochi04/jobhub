from flask import Blueprint, jsonify, request
from app.models import db, Search, ExecutionLog
from app.utils.database import DatabaseUtils
from datetime import datetime

status_bp = Blueprint('status', __name__)

@status_bp.route('/status', methods=['GET'])
def get_global_status():
    """Récupère le statut global de l'application"""
    try:
        # Statistiques globales
        dashboard_stats = DatabaseUtils.get_dashboard_stats()
        
        # Dernières exécutions
        recent_logs = ExecutionLog.query.order_by(ExecutionLog.executed_at.desc())\
                                       .limit(10).all()
        
        # Vérifier la santé du système
        health_status = "healthy"
        issues = []
        
        # Vérifier s'il y a des recherches actives sans exécution récente
        active_searches = DatabaseUtils.get_active_searches()
        for search in active_searches:
            last_log = ExecutionLog.query.filter_by(search_id=search.id)\
                                        .order_by(ExecutionLog.executed_at.desc())\
                                        .first()
            
            if last_log:
                time_since_last = datetime.utcnow() - last_log.executed_at
                expected_interval_minutes = search.duration_minutes
                
                # Si plus de 2x l'intervalle attendu, c'est un problème
                if time_since_last.total_seconds() > (expected_interval_minutes * 2 * 60):
                    health_status = "warning"
                    issues.append(f"Search {search.id} hasn't run for {int(time_since_last.total_seconds() / 60)} minutes")
        
        return jsonify({
            'status': health_status,
            'timestamp': datetime.utcnow().isoformat(),
            'stats': dashboard_stats,
            'recent_executions': [log.to_dict() for log in recent_logs],
            'issues': issues
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat(),
            'error': f'Internal server error: {str(e)}'
        }), 500

@status_bp.route('/status/<int:search_id>', methods=['GET'])
def get_search_status(search_id):
    """Récupère le statut d'une recherche spécifique"""
    try:
        search = DatabaseUtils.get_search_by_id(search_id)
        if not search:
            return jsonify({'error': 'Search not found'}), 404
        
        # Statistiques de la recherche
        stats = DatabaseUtils.get_search_stats(search_id)
        
        # Dernières exécutions pour cette recherche
        recent_logs = ExecutionLog.query.filter_by(search_id=search_id)\
                                       .order_by(ExecutionLog.executed_at.desc())\
                                       .limit(5).all()
        
        # Calculer le temps jusqu'à la prochaine exécution
        next_run_estimate = None
        if search.is_active and recent_logs:
            last_execution = recent_logs[0].executed_at
            interval_seconds = search.duration_minutes * 60
            next_run_estimate = last_execution.timestamp() + interval_seconds
        
        # Déterminer le statut de la recherche
        search_status = "inactive"
        if search.is_active:
            if recent_logs:
                last_log = recent_logs[0]
                if last_log.status == 'success':
                    search_status = "active"
                elif last_log.status == 'error':
                    search_status = "error"
                else:
                    search_status = "partial"
            else:
                search_status = "pending"  # Pas encore d'exécution
        
        return jsonify({
            'search_id': search_id,
            'status': search_status,
            'is_active': search.is_active,
            'next_run_estimate': next_run_estimate,
            'stats': stats,
            'recent_executions': [log.to_dict() for log in recent_logs],
            'search_config': search.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@status_bp.route('/status/logs', methods=['GET'])
def get_execution_logs():
    """Récupère les logs d'exécution avec filtres"""
    try:
        # Paramètres optionnels
        search_id = request.args.get('search_id', type=int)
        platform = request.args.get('platform')
        status = request.args.get('status')
        limit = request.args.get('limit', default=50, type=int)
        
        if limit > 200:
            limit = 200
        
        # Construire la requête
        query = ExecutionLog.query
        
        if search_id:
            query = query.filter_by(search_id=search_id)
        
        if platform:
            query = query.filter_by(platform=platform)
        
        if status:
            query = query.filter_by(status=status)
        
        logs = query.order_by(ExecutionLog.executed_at.desc()).limit(limit).all()
        
        return jsonify({
            'logs': [log.to_dict() for log in logs],
            'total': len(logs),
            'filters': {
                'search_id': search_id,
                'platform': platform,
                'status': status,
                'limit': limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@status_bp.route('/status/health', methods=['GET'])
def health_check():
    """Endpoint de santé pour monitoring"""
    try:
        # Vérifier la connexion à la base de données
        db.session.execute(db.text('SELECT 1'))
        
        # Compter les éléments basiques
        total_searches = Search.query.count()
        active_searches = Search.query.filter_by(is_active=True).count()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat(),
            'basic_stats': {
                'total_searches': total_searches,
                'active_searches': active_searches
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'error',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500

@status_bp.route('/status/metrics', methods=['GET'])
def get_metrics():
    """Récupère les métriques pour monitoring (format Prometheus-like)"""
    try:
        stats = DatabaseUtils.get_dashboard_stats()
        trends = DatabaseUtils.get_job_trends(days=1)  # Dernières 24h
        
        # Format simple pour les métriques
        metrics = {
            'jobhub_searches_total': stats['total_searches'],
            'jobhub_searches_active': stats['active_searches'],
            'jobhub_jobs_total': stats['total_jobs'],
            'jobhub_jobs_new': stats['new_jobs'],
            'jobhub_jobs_24h': stats['jobs_24h'],
            'jobhub_platforms_count': len(stats['platform_stats']),
            'jobhub_trends_today': len(trends)
        }
        
        # Ajouter les métriques par plateforme
        for platform_stat in stats['platform_stats']:
            platform = platform_stat['platform'].replace('-', '_')
            metrics[f'jobhub_jobs_platform_{platform}_total'] = platform_stat['total']
            metrics[f'jobhub_jobs_platform_{platform}_new'] = platform_stat['new']
        
        return jsonify({
            'metrics': metrics,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500
