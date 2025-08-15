# Backend JobHub - API Flask

## 🗄️ Base de Données

L'application utilise **SQLite** pour le développement avec les tables suivantes :

### Tables principales

#### `searches` - Recherches configurées
- `id` : Identifiant unique
- `keywords` : Mots-clés de recherche (ex: "data science")
- `job_types` : Types d'emploi (JSON: ["alternance", "stage"])
- `platforms` : Plateformes à scraper (JSON: ["indeed", "linkedin"])
- `duration_minutes` : Intervalle du cron job (défaut: 15min)
- `is_active` : Recherche active ou non
- `created_at`, `updated_at` : Dates de création/modification

#### `jobs` - Offres d'emploi trouvées  
- `id` : Identifiant unique
- `search_id` : Référence vers la recherche
- `title` : Titre de l'offre
- `company` : Entreprise
- `url` : URL de l'offre (unique)
- `platform` : Plateforme source
- `location` : Localisation
- `job_type` : Type de contrat
- `date_posted` : Date de publication sur la plateforme
- `date_found` : Date de découverte par JobHub
- `is_new` : Nouvelle offre (non vue)

#### `execution_logs` - Logs des exécutions
- `search_id` : Référence vers la recherche  
- `platform` : Plateforme scrapée
- `jobs_found` : Nombre d'offres trouvées
- `new_jobs_found` : Nombre de nouvelles offres
- `execution_time` : Temps d'exécution (secondes)
- `status` : 'success', 'error', 'partial'
- `executed_at` : Date d'exécution

## 🚀 Installation & Configuration

### Prérequis
```bash
# Python 3.9+
python --version

# Installer les dépendances
pip install -r requirements.txt
```

### Variables d'environnement
Copier `.env.example` vers `.env` et ajuster :
```bash
SECRET_KEY=dev-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=1
DEV_DATABASE_URL=sqlite:///jobhub_dev.db
SCRAPING_INTERVAL_MINUTES=15
```

### Initialisation base de données
```bash
# Créer les tables
python init_db.py init

# Ajouter des données de test
python init_db.py sample

# Voir les statistiques
python init_db.py stats

# Nettoyer les anciennes données
python init_db.py cleanup

# Remettre à zéro (⚠️ perte de données)
python init_db.py reset
```

## 🖥️ Lancement

### Serveur de développement
```bash
# Méthode 1 : Via run.py
python run.py

# Méthode 2 : Via Flask CLI
export FLASK_APP=app
flask run

# Méthode 3 : Avec paramètres
python run.py --host=0.0.0.0 --port=8000
```

L'API sera disponible sur `http://127.0.0.1:5000`

## 📡 Endpoints API

### Santé et statut
- `GET /health` - Santé de l'application
- `GET /api/status` - Statut global avec statistiques
- `GET /api/status/<search_id>` - Statut d'une recherche
- `GET /api/status/health` - Health check pour monitoring

### Recherches
- `POST /api/search` - Créer une recherche
- `GET /api/search/<id>` - Détails d'une recherche
- `PUT /api/search/<id>` - Modifier une recherche
- `DELETE /api/search/<id>` - Désactiver une recherche
- `GET /api/searches` - Lister les recherches

### Offres d'emploi
- `GET /api/jobs` - Lister les offres avec filtres
- `GET /api/jobs/<id>` - Détails d'une offre
- `POST /api/jobs/mark-seen` - Marquer comme vues
- `GET /api/jobs/stats` - Statistiques des offres
- `GET /api/jobs/platforms` - Plateformes disponibles
- `POST /api/jobs/search` - Rechercher dans les offres

## 📝 Exemples d'utilisation

### Créer une recherche
```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "data science",
    "job_types": ["alternance", "stage"],
    "platforms": ["indeed", "linkedin"],
    "duration_minutes": 15
  }'
```

### Récupérer les offres d'une recherche
```bash
curl "http://localhost:5000/api/jobs?search_id=1&new_only=true&limit=20"
```

### Statistiques globales
```bash
curl "http://localhost:5000/api/jobs/stats"
```

## 🗂️ Structure du code

```
backend/
├── app/
│   ├── __init__.py          # Factory Flask
│   ├── models/
│   │   └── __init__.py      # Modèles SQLAlchemy
│   ├── routes/
│   │   ├── __init__.py      # Import des blueprints
│   │   ├── search.py        # Routes des recherches
│   │   ├── jobs.py          # Routes des offres
│   │   └── status.py        # Routes de statut
│   ├── services/            # Services métier (futurs scrapers)
│   ├── scrapers/            # Modules de scraping
│   └── utils/
│       └── database.py      # Utilitaires base de données
├── config.py                # Configuration Flask
├── run.py                   # Point d'entrée principal
├── init_db.py               # Gestion base de données
├── requirements.txt         # Dépendances Python
└── .env                     # Variables d'environnement
```

## 🧪 Tests

### Test manuel des endpoints
```bash
# Santé de l'API
curl http://localhost:5000/health

# Statistiques
curl http://localhost:5000/api/jobs/stats

# Recherches actives
curl http://localhost:5000/api/searches?active_only=true

# Dernières offres
curl "http://localhost:5000/api/jobs?hours=24&limit=10"
```

### Validation base de données
```bash
# Vérifier la cohérence
python -c "from app.utils.database import DatabaseUtils; print(DatabaseUtils.get_dashboard_stats())"

# Compter les enregistrements
python init_db.py stats
```

## 🔧 Développement

### Ajout d'un nouveau scraper
1. Créer `app/scrapers/plateforme_scraper.py`
2. Hériter de `BaseScraper` (à implémenter)
3. Enregistrer dans le scheduler
4. Tester avec les utilitaires

### Base de données
- **Migrations** : Utiliser Flask-Migrate pour les changements de schéma
- **Backup** : SQLite = simple copie de fichier `.db`
- **Performance** : Index sur `url`, `date_found`, `is_new`

### Monitoring
- Logs structurés dans la console
- Métriques exposées via `/api/status/metrics`
- Health checks automatiques

## 🚨 Problèmes courants

### Base de données verrouillée
```bash
# Identifier les processus
lsof | grep jobhub_dev.db

# Redémarrer proprement
python init_db.py cleanup
```

### Erreurs de migration
```bash
# Réinitialiser
python init_db.py reset
python init_db.py init
python init_db.py sample
```

### Performance lente
```bash
# Nettoyer les anciens logs
python init_db.py cleanup

# Réindexer (si nécessaire)
sqlite3 jobhub_dev.db "REINDEX;"
```

La base de données SQLite est maintenant configurée et opérationnelle ! 🎉
