from flask import Blueprint, request, jsonify
from app.models import db
from app.utils.database import DatabaseUtils
import json

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['POST'])
def create_search():
    """Crée une nouvelle recherche avec cron job"""
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
        
        # TODO: Démarrer le cron job pour cette recherche
        # Cette partie sera implémentée avec le scheduler
        
        return jsonify({
            'message': 'Search created successfully',
            'search': search.to_dict()
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
    """Met à jour une recherche existante"""
    try:
        search = DatabaseUtils.get_search_by_id(search_id)
        if not search:
            return jsonify({'error': 'Search not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
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
        
        return jsonify({
            'message': 'Search updated successfully',
            'search': search.to_dict()
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
        
        # Désactiver la recherche au lieu de la supprimer (pour garder l'historique)
        success = DatabaseUtils.deactivate_search(search_id)
        
        if success:
            # TODO: Arrêter le cron job associé
            return jsonify({'message': 'Search deactivated successfully'}), 200
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
