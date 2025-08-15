from flask import Blueprint, request, jsonify
from app.models import db
from app.utils.database import DatabaseUtils
import json

search_bp = Blueprint('search', __name__)

# Référence globale au service de scraping (sera injectée)
_scraping_service = None

def set_scraping_service(service):
    """Injection du service de scraping"""
    global _scraping_service
    _scraping_service = service

@search_bp.route('/search', methods=['POST'])
def create_search():
    """Crée une nouvelle recherche avec cron job automatique"""
    try:
        data = request.get_json()
        
        # Validation des données
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        keywords = data.get('keywords', '').strip()
        job_types = data.get('job_types', [])
        platforms = data.get('platforms', [])
        duration_minutes = data.get('duration_minutes', 15)
        
        # Validations
        if not keywords:
            return jsonify({'error': 'Keywords are required'}), 400
        
        if not job_types:
            return jsonify({'error': 'At least one job type is required'}), 400
        
        if not platforms:
            return jsonify({'error': 'At least one platform is required'}), 400
        
        if duration_minutes < 5 or duration_minutes > 60:
            return jsonify({'error': 'Duration must be between 5 and 60 minutes'}), 400
        
        # Créer la recherche
        search = DatabaseUtils.create_search(
            keywords=keywords,
            job_types=job_types,
            platforms=platforms,
            duration_minutes=duration_minutes
        )
        
        # Programmer automatiquement la recherche si le service est disponible
        scheduled = False
        if _scraping_service:
            try:
                scheduled = _scraping_service.schedule_search(search.id)
            except Exception as e:
                print(f"Warning: Failed to schedule search {search.id}: {e}")
        
        return jsonify({
            'message': 'Search created successfully',
            'search': search.to_dict(),
            'scheduled': scheduled
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@search_bp.route('/search/<int:search_id>', methods=['GET'])
def get_search(search_id):
    """Récupère les détails d'une recherche"""
    try:
        search = DatabaseUtils.get_search_by_id(search_id)
        if not search:
            return jsonify({'error': 'Search not found'}), 404
        
        # Récupérer les statistiques
        stats = DatabaseUtils.get_search_stats(search_id)
        
        return jsonify({
            'search': search.to_dict(),
            'stats': stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@search_bp.route('/search/<int:search_id>', methods=['PUT'])
def update_search(search_id):
    """Met à jour une recherche existante et reprogramme si nécessaire"""
    try:
        search = DatabaseUtils.get_search_by_id(search_id)
        if not search:
            return jsonify({'error': 'Search not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        was_active = search.is_active
        
        # Mettre à jour les champs modifiables
        if 'keywords' in data:
            search.keywords = data['keywords'].strip()
        
        if 'job_types' in data:
            search.job_types = json.dumps(data['job_types'])
        
        if 'platforms' in data:
            search.platforms = json.dumps(data['platforms'])
        
        if 'duration_minutes' in data:
            duration = data['duration_minutes']
            if duration < 5 or duration > 60:
                return jsonify({'error': 'Duration must be between 5 and 60 minutes'}), 400
            search.duration_minutes = duration
        
        if 'is_active' in data:
            search.is_active = bool(data['is_active'])
        
        db.session.commit()
        
        # Reprogrammer si nécessaire
        rescheduled = False
        if _scraping_service:
            try:
                if was_active and not search.is_active:
                    # Désactiver le job
                    _scraping_service.unschedule_search(search_id)
                    rescheduled = "unscheduled"
                elif search.is_active:
                    # Reprogrammer (que ce soit nouveau ou mise à jour)
                    rescheduled = _scraping_service.schedule_search(search_id)
                    rescheduled = "rescheduled" if rescheduled else "failed"
            except Exception as e:
                print(f"Warning: Failed to reschedule search {search_id}: {e}")
        
        return jsonify({
            'message': 'Search updated successfully',
            'search': search.to_dict(),
            'rescheduled': rescheduled
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@search_bp.route('/search/<int:search_id>', methods=['DELETE'])
def delete_search(search_id):
    """Supprime une recherche et arrête son cron job"""
    try:
        search = DatabaseUtils.get_search_by_id(search_id)
        if not search:
            return jsonify({'error': 'Search not found'}), 404
        
        # Arrêter le job programmé
        unscheduled = False
        if _scraping_service:
            try:
                unscheduled = _scraping_service.unschedule_search(search_id)
            except Exception as e:
                print(f"Warning: Failed to unschedule search {search_id}: {e}")
        
        # Désactiver la recherche au lieu de la supprimer (pour garder l'historique)
        success = DatabaseUtils.deactivate_search(search_id)
        
        if success:
            return jsonify({
                'message': 'Search deactivated successfully',
                'unscheduled': unscheduled
            }), 200
        else:
            return jsonify({'error': 'Failed to deactivate search'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@search_bp.route('/searches', methods=['GET'])
def list_searches():
    """Liste toutes les recherches"""
    try:
        # Paramètres optionnels
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        
        if active_only:
            searches = DatabaseUtils.get_active_searches()
        else:
            from app.models import Search
            searches = Search.query.order_by(Search.created_at.desc()).all()
        
        return jsonify({
            'searches': [search.to_dict() for search in searches],
            'total': len(searches)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@search_bp.route('/searches', methods=['POST'])
def create_search_plural():
    """Crée une nouvelle recherche avec cron job (route plurielle)"""
    return create_search()

@search_bp.route('/searches/<int:search_id>', methods=['DELETE'])
def delete_search_plural(search_id):
    """Supprime une recherche (route plurielle)"""
    return delete_search(search_id)

@search_bp.route('/searches/<int:search_id>', methods=['PUT'])
def update_search_plural(search_id):
    """Met à jour une recherche (route plurielle)"""
    return update_search(search_id)
