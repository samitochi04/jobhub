#!/usr/bin/env python3
"""
Point d'entrée principal pour l'application JobHub
"""
import os
from app import create_app
from app.models import db

# Créer l'application
app = create_app()

if __name__ == '__main__':
    # Configuration pour le développement
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    
    print("🚀 Starting JobHub API...")
    print(f"📡 Server running on http://{host}:{port}")
    print(f"🔍 Debug mode: {'ON' if debug else 'OFF'}")
    print(f"💾 Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Lancer l'application
    app.run(host=host, port=port, debug=debug)
