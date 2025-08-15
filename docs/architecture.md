# Architecture JobHub

## Vue d'ensemble

JobHub est une application web qui automatise la veille des offres d'emploi en scrapant plusieurs plateformes de recrutement et en notifiant l'utilisateur des nouvelles opportunités en temps réel.

## Architecture Système

```
┌─────────────────────────────────────────────────────────────────┐
│                           FRONTEND                              │
│                      React + Vite + Tailwind                   │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Dashboard     │  │   Formulaire    │  │   Résultats     │ │
│  │   Principal     │  │   Recherche     │  │   en Temps      │ │
│  │                 │  │                 │  │   Réel          │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ HTTP/WebSocket
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                            BACKEND                              │
│                          Flask API                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   API Routes    │  │   Scheduler     │  │   Scrapers      │ │
│  │   /search       │  │   Cron Jobs     │  │   Module        │ │
│  │   /jobs         │  │   (15min)       │  │                 │ │
│  │   /status       │  │                 │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                          DATABASE                               │
│                        SQLite/PostgreSQL                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Jobs          │  │   Searches      │  │   Logs          │ │
│  │   - url         │  │   - keywords    │  │   - timestamp   │ │
│  │   - title       │  │   - type        │  │   - status      │ │
│  │   - company     │  │   - duration    │  │   - errors      │ │
│  │   - date_added  │  │   - active      │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Architecture Frontend

### Structure des composants
```
src/
├── components/
│   ├── common/
│   │   ├── Header.jsx
│   │   ├── Footer.jsx
│   │   └── Layout.jsx
│   ├── forms/
│   │   ├── SearchForm.jsx
│   │   └── FilterForm.jsx
│   ├── dashboard/
│   │   ├── Dashboard.jsx
│   │   ├── StatsCard.jsx
│   │   └── RecentJobs.jsx
│   └── jobs/
│       ├── JobCard.jsx
│       ├── JobList.jsx
│       └── JobDetails.jsx
├── pages/
│   ├── Home.jsx
│   ├── Search.jsx
│   └── Results.jsx
├── hooks/
│   ├── useWebSocket.js
│   ├── useSearch.js
│   └── useJobs.js
├── services/
│   ├── api.js
│   └── websocket.js
├── utils/
│   ├── constants.js
│   └── helpers.js
└── styles/
    └── globals.css
```

### Design System

#### Palette de couleurs
- **Primary Black**: `#0A0A0B` - Noir profond et élégant
- **Gold**: `#FFD700` - Jaune or pour les accents
- **Light Gold**: `#FFF8DC` - Or clair pour les backgrounds
- **White**: `#FFFFFF` - Blanc pur
- **Gray**: `#6B7280` - Gris pour le texte secondaire
- **Success**: `#10B981` - Vert pour les succès
- **Warning**: `#F59E0B` - Orange pour les alertes

#### Typographie
- **Font Primary**: Inter (Google Fonts)
- **Font Secondary**: JetBrains Mono (pour le code)

#### Éléments graphiques
- Patterns géométriques subtils en arrière-plan
- Animations micro-interactions
- Glassmorphism pour les cartes
- Gradients or/noir pour les éléments premium

## Architecture Backend

### Structure des modules
```
backend/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── job.py
│   │   ├── search.py
│   │   └── log.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── search.py
│   │   ├── jobs.py
│   │   └── status.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── scraper.py
│   │   ├── scheduler.py
│   │   └── notification.py
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base_scraper.py
│   │   ├── indeed_scraper.py
│   │   ├── linkedin_scraper.py
│   │   ├── welcometothejungle_scraper.py
│   │   └── apec_scraper.py
│   └── utils/
│       ├── __init__.py
│       ├── database.py
│       ├── config.py
│       └── helpers.py
├── requirements.txt
├── config.py
└── run.py
```

### API Endpoints

#### POST /api/search
Démarre une nouvelle recherche avec cron job
```json
{
  "keywords": "data science",
  "job_types": ["alternance", "stage"],
  "duration_minutes": 15,
  "platforms": ["indeed", "linkedin", "welcometothejungle"]
}
```

#### GET /api/jobs
Récupère les offres trouvées
```json
{
  "jobs": [
    {
      "id": 1,
      "url": "https://...",
      "title": "Data Scientist - Alternance",
      "company": "TechCorp",
      "location": "Paris",
      "date_added": "2025-08-15T10:30:00Z",
      "platform": "indeed"
    }
  ],
  "total": 25,
  "new_since_last": 3
}
```

#### GET /api/status/{search_id}
État du cron job de recherche
```json
{
  "status": "active",
  "next_run": "2025-08-15T10:45:00Z",
  "jobs_found": 12,
  "errors": []
}
```

#### DELETE /api/search/{search_id}
Arrête un cron job de recherche

## Flux de données

### 1. Création d'une recherche
1. Utilisateur remplit le formulaire
2. Frontend envoie POST /api/search
3. Backend crée l'entrée en base
4. Scheduler programme le cron job
5. Premier scraping immédiat
6. Retour des résultats au frontend

### 2. Exécution des cron jobs
1. Scheduler déclenche le scraping
2. Chaque scraper vérifie les nouvelles offres
3. Comparaison avec les offres existantes
4. Stockage des nouvelles offres
5. Notification WebSocket au frontend (optionnel)

### 3. Affichage temps réel
1. Frontend poll l'API toutes les minutes
2. Ou utilise WebSocket pour mises à jour temps réel
3. Affichage des nouvelles offres avec animation
4. Statistiques mises à jour

## Considérations techniques

### Scalabilité
- Base de données: SQLite pour dev, PostgreSQL pour prod
- Cache Redis pour les résultats fréquents
- Rate limiting pour éviter le spam des scrapers
- Queue system (Celery) pour les gros volumes

### Sécurité
- Rate limiting sur les APIs
- Validation des entrées
- CORS configuré
- Headers de sécurité
- Pas de stockage de données personnelles

### Monitoring
- Logs structurés
- Métriques de performance des scrapers
- Alertes en cas d'échec répétés
- Dashboard admin pour monitoring

### Déploiement
- Docker containers
- Docker Compose pour développement
- GitHub Actions pour CI/CD
- Déploiement possible sur Coolify
