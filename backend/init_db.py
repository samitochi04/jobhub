#!/usr/bin/env python3
"""
Script pour initialiser et gérer la base de données JobHub
"""
import os
import sys
from app import create_app
from app.models import db, Search, Job, ExecutionLog, JobMetrics
from app.utils.database import DatabaseUtils
from datetime import datetime
import json

def init_db():
    """Initialise la base de données"""
    print("🔧 Initializing database...")
    
    app = create_app()
    with app.app_context():
        try:
            # Créer toutes les tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Vérifier les tables créées
            tables = db.inspect(db.engine).get_table_names()
            print(f"📋 Created tables: {', '.join(tables)}")
            
        except Exception as e:
            print(f"❌ Error creating database: {e}")
            return False
    
    return True

def add_sample_data():
    """Ajoute des données de test"""
    print("📝 Adding sample data...")
    
    app = create_app()
    with app.app_context():
        try:
            # Vérifier s'il y a déjà des données
            if Search.query.count() > 0:
                print("ℹ️  Database already contains data, skipping sample data")
                return True
            
            # Créer une recherche d'exemple
            sample_search = DatabaseUtils.create_search(
                keywords="data science",
                job_types=["alternance", "stage"],
                platforms=["indeed", "linkedin"],
                duration_minutes=15
            )
            
            print(f"✅ Created sample search with ID: {sample_search.id}")
            
            # Ajouter quelques jobs d'exemple
            sample_jobs = [
                {
                    'title': 'Data Scientist - Alternance',
                    'company': 'TechCorp',
                    'url': 'https://example.com/job1',
                    'platform': 'indeed',
                    'location': 'Paris, France',
                    'job_type': 'alternance',
                    'description_snippet': 'Rejoignez notre équipe data science...'
                },
                {
                    'title': 'Stage Machine Learning',
                    'company': 'StartupAI',
                    'url': 'https://example.com/job2',
                    'platform': 'linkedin',
                    'location': 'Lyon, France',
                    'job_type': 'stage',
                    'description_snippet': 'Découvrez le machine learning en pratique...'
                }
            ]
            
            for job_data in sample_jobs:
                job, is_new = DatabaseUtils.add_job(
                    search_id=sample_search.id,
                    **job_data
                )
                if is_new:
                    print(f"✅ Added sample job: {job_data['title']}")
            
            # Ajouter un log d'exécution
            DatabaseUtils.log_execution(
                search_id=sample_search.id,
                platform='indeed',
                jobs_found=2,
                new_jobs_found=2,
                execution_time=1.5,
                status='success'
            )
            
            print("✅ Sample data added successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error adding sample data: {e}")
            return False

def reset_db():
    """Remet à zéro la base de données"""
    print("⚠️  Resetting database...")
    
    app = create_app()
    with app.app_context():
        try:
            # Supprimer toutes les tables
            db.drop_all()
            print("🗑️  Dropped all tables")
            
            # Recréer les tables
            db.create_all()
            print("✅ Recreated all tables")
            
        except Exception as e:
            print(f"❌ Error resetting database: {e}")
            return False
    
    return True

def show_stats():
    """Affiche les statistiques de la base de données"""
    print("📊 Database Statistics:")
    
    app = create_app()
    with app.app_context():
        try:
            stats = DatabaseUtils.get_dashboard_stats()
            
            print(f"🔍 Total searches: {stats['total_searches']}")
            print(f"✅ Active searches: {stats['active_searches']}")
            print(f"💼 Total jobs: {stats['total_jobs']}")
            print(f"🆕 New jobs: {stats['new_jobs']}")
            print(f"📈 Jobs in last 24h: {stats['jobs_24h']}")
            
            print("\n📋 Platform breakdown:")
            for platform_stat in stats['platform_stats']:
                print(f"   {platform_stat['platform']}: {platform_stat['total']} total, {platform_stat['new']} new")
            
        except Exception as e:
            print(f"❌ Error getting stats: {e}")

def cleanup():
    """Nettoie les anciennes données"""
    print("🧹 Cleaning up old data...")
    
    app = create_app()
    with app.app_context():
        try:
            # Nettoyer les anciens logs (plus de 30 jours)
            deleted_logs = DatabaseUtils.cleanup_old_logs(days=30)
            print(f"🗑️  Deleted {deleted_logs} old log entries")
            
            # Marquer les anciennes offres comme vues
            from datetime import timedelta
            cutoff = datetime.utcnow() - timedelta(days=7)
            old_jobs = Job.query.filter(
                Job.date_found < cutoff,
                Job.is_new == True
            ).update({Job.is_new: False})
            
            db.session.commit()
            print(f"👁️  Marked {old_jobs} old jobs as seen")
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")

def main():
    """Fonction principale"""
    if len(sys.argv) < 2:
        print("Usage: python init_db.py <command>")
        print("Commands:")
        print("  init     - Initialize database")
        print("  reset    - Reset database (WARNING: deletes all data)")
        print("  sample   - Add sample data")
        print("  stats    - Show database statistics")
        print("  cleanup  - Clean up old data")
        return
    
    command = sys.argv[1]
    
    if command == 'init':
        init_db()
    elif command == 'reset':
        if input("⚠️  Are you sure you want to reset the database? (yes/no): ") == 'yes':
            reset_db()
        else:
            print("❌ Database reset cancelled")
    elif command == 'sample':
        add_sample_data()
    elif command == 'stats':
        show_stats()
    elif command == 'cleanup':
        cleanup()
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == '__main__':
    main()
