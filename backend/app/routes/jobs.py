from flask import Blueprint, request, jsonify
from app.models import db, Job
from app.utils.database import DatabaseUtils

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/jobs', methods=['GET'])
def get_jobs():
    """Récupère les offres d'emploi avec filtres optionnels"""
    try:
        # Paramètres de la requête
        search_id = request.args.get('search_id', type=int)
        limit = request.args.get('limit', default=50, type=int)
        new_only = request.args.get('new_only', 'false').lower() == 'true'
        platform = request.args.get('platform')
        hours = request.args.get('hours', type=int)  # Jobs des dernières X heures
        
        # Limiter le nombre de résultats
        if limit > 200:
            limit = 200
        
        jobs = []
        
        if search_id:
            # Jobs pour une recherche spécifique
            jobs = DatabaseUtils.get_jobs_for_search(search_id, limit, new_only)
        elif hours:
            # Jobs récents
            jobs = DatabaseUtils.get_recent_jobs(hours, limit)
        else:
            # Tous les jobs avec filtres optionnels
            query = Job.query
            
            if new_only:
                query = query.filter_by(is_new=True)
            
            if platform:
                query = query.filter_by(platform=platform)
            
            jobs = query.order_by(Job.date_found.desc()).limit(limit).all()
        
        return jsonify({
            'jobs': [job.to_dict() for job in jobs],
            'total': len(jobs),
            'filters': {
                'search_id': search_id,
                'limit': limit,
                'new_only': new_only,
                'platform': platform,
                'hours': hours
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@jobs_bp.route('/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    """Récupère les détails d'une offre d'emploi spécifique"""
    try:
        job = Job.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify({'job': job.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@jobs_bp.route('/jobs/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    """Met à jour une offre d'emploi spécifique"""
    try:
        job = Job.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Mettre à jour les champs modifiables
        if 'is_new' in data:
            job.is_new = data['is_new']
        
        if 'status' in data:
            # Ajouter un champ status si nécessaire
            job.status = data['status']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Job updated successfully',
            'job': job.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@jobs_bp.route('/jobs/mark-seen', methods=['POST'])
def mark_jobs_seen():
    """Marque des offres comme vues (is_new = false)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        search_id = data.get('search_id')
        job_ids = data.get('job_ids', [])
        
        if search_id:
            # Marquer toutes les offres d'une recherche comme vues
            DatabaseUtils.mark_jobs_as_seen(search_id)
            message = f'All jobs for search {search_id} marked as seen'
            
        elif job_ids:
            # Marquer des offres spécifiques comme vues
            Job.query.filter(Job.id.in_(job_ids)).update({Job.is_new: False})
            db.session.commit()
            message = f'{len(job_ids)} jobs marked as seen'
            
        else:
            return jsonify({'error': 'Either search_id or job_ids must be provided'}), 400
        
        return jsonify({'message': message}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@jobs_bp.route('/jobs/stats', methods=['GET'])
def get_jobs_stats():
    """Récupère des statistiques sur les offres d'emploi"""
    try:
        # Paramètres optionnels
        search_id = request.args.get('search_id', type=int)
        days = request.args.get('days', default=7, type=int)
        
        if search_id:
            # Statistiques pour une recherche spécifique
            stats = DatabaseUtils.get_search_stats(search_id)
        else:
            # Statistiques globales
            stats = DatabaseUtils.get_dashboard_stats()
            
            # Ajouter les tendances si demandées
            if days > 0:
                stats['trends'] = DatabaseUtils.get_job_trends(days)
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@jobs_bp.route('/jobs/platforms', methods=['GET'])
def get_platforms():
    """Récupère la liste des plateformes disponibles avec leurs statistiques"""
    try:
        # Compter les jobs par plateforme
        from sqlalchemy import func
        platform_stats = db.session.query(
            Job.platform,
            func.count(Job.id).label('total_jobs'),
            func.sum(func.cast(Job.is_new, db.Integer)).label('new_jobs')
        ).group_by(Job.platform).all()
        
        platforms = [
            {
                'name': stat[0],
                'total_jobs': stat[1],
                'new_jobs': stat[2] or 0
            }
            for stat in platform_stats
        ]
        
        return jsonify({
            'platforms': platforms,
            'total_platforms': len(platforms)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@jobs_bp.route('/jobs/search', methods=['POST'])
def search_jobs():
    """Recherche dans les offres d'emploi existantes"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No search criteria provided'}), 400
        
        query_text = data.get('query', '').strip()
        platforms = data.get('platforms', [])
        job_types = data.get('job_types', [])
        limit = data.get('limit', 50)
        
        if limit > 200:
            limit = 200
        
        # Construire la requête
        query = Job.query
        
        # Recherche textuelle dans le titre et la description
        if query_text:
            from sqlalchemy import or_
            search_filter = or_(
                Job.title.ilike(f'%{query_text}%'),
                Job.description_snippet.ilike(f'%{query_text}%'),
                Job.company.ilike(f'%{query_text}%')
            )
            query = query.filter(search_filter)
        
        # Filtrer par plateformes
        if platforms:
            query = query.filter(Job.platform.in_(platforms))
        
        # Filtrer par types d'emploi
        if job_types:
            query = query.filter(Job.job_type.in_(job_types))
        
        jobs = query.order_by(Job.date_found.desc()).limit(limit).all()
        
        return jsonify({
            'jobs': [job.to_dict() for job in jobs],
            'total': len(jobs),
            'search_criteria': {
                'query': query_text,
                'platforms': platforms,
                'job_types': job_types,
                'limit': limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500
