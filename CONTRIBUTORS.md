# Guide de Contribution - JobHub

Merci de votre intérêt pour contribuer à JobHub ! 🎉

Ce guide vous aidera à contribuer efficacement au projet, que ce soit pour corriger un bug, ajouter une fonctionnalité ou améliorer la documentation.

## 📋 Table des Matières

- [Code de Conduite](#code-de-conduite)
- [Comment Contribuer](#comment-contribuer)
- [Guide de Développement](#guide-de-développement)
- [Standards de Code](#standards-de-code)
- [Processus de Pull Request](#processus-de-pull-request)
- [Types de Contributions](#types-de-contributions)
- [Configuration Développement](#configuration-développement)

## 🤝 Code de Conduite

En participant à ce projet, vous acceptez de respecter notre code de conduite :

- **Soyez respectueux** envers tous les contributeurs
- **Soyez constructif** dans vos critiques et suggestions
- **Soyez patient** avec les nouveaux contributeurs
- **Concentrez-vous sur ce qui est le mieux** pour la communauté

## 🚀 Comment Contribuer

### 1. Fork et Clone

```bash
# Fork le repository sur GitHub, puis clonez votre fork
git clone https://github.com/VOTRE_USERNAME/jobhub.git
cd jobhub

# Ajoutez le repository original comme remote
git remote add upstream https://github.com/OWNER/jobhub.git
```

### 2. Créer une Branche

```bash
# Synchronisez avec la branche main
git checkout main
git pull upstream main

# Créez une branche pour votre contribution
git checkout -b feature/nom-de-votre-feature
# ou
git checkout -b bugfix/description-du-bug
# ou  
git checkout -b docs/amelioration-documentation
```

### 3. Faire vos Changements

- Codez votre fonctionnalité ou correction
- Testez vos changements localement
- Respectez les standards de code (voir section dédiée)
- Documentez si nécessaire

### 4. Commit et Push

```bash
# Ajoutez vos fichiers
git add .

# Commit avec un message descriptif
git commit -m "feat: ajout scraper pour Pôle Emploi"
# ou
git commit -m "fix: correction bug pagination Indeed"
# ou
git commit -m "docs: mise à jour guide installation"

# Push vers votre fork
git push origin feature/nom-de-votre-feature
```

### 5. Créer une Pull Request

1. Allez sur GitHub sur votre fork
2. Cliquez sur "New Pull Request"
3. Remplissez le template de PR
4. Attendez la review

## 🛠️ Configuration Développement

### Prérequis

- Python 3.9+
- Node.js 18+
- Git
- Docker (optionnel mais recommandé)

### Installation Locale

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Outils de dev

# Frontend
cd ../frontend
npm install

# Base de données
cd ../backend
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Avec Docker (Recommandé)

```bash
# Copier le fichier d'environnement
cp .env.example .env

# Lancer en mode développement
docker-compose -f docker-compose.dev.yml up --build
```

### Tests

```bash
# Backend
cd backend
pytest tests/ -v

# Frontend
cd frontend
npm test

# Tests E2E (futur)
npm run test:e2e
```

## 📝 Standards de Code

### Python (Backend)

#### Style
- **PEP 8** pour le style Python
- **Black** pour le formatage automatique
- **Isort** pour l'organisation des imports
- **Flake8** pour le linting

```bash
# Formatage automatique
black backend/
isort backend/

# Vérification
flake8 backend/
```

#### Structure

```python
# Ordre des imports
import os  # Standard library
import sys

import requests  # Third party
from flask import Flask

from app.models import Job  # Local imports
from app.utils import helpers
```

#### Docstrings

```python
def scrape_jobs(keywords: str, job_type: str, limit: int = 50) -> List[Dict]:
    """
    Scrape jobs from a platform based on search criteria.
    
    Args:
        keywords: Search keywords (e.g., "data science")
        job_type: Type of job (e.g., "alternance", "stage")
        limit: Maximum number of jobs to return
        
    Returns:
        List of job dictionaries with keys: title, company, url, date
        
    Raises:
        ScrapingError: If the platform is unreachable
    """
    pass
```

### JavaScript (Frontend)

#### Style
- **Prettier** pour le formatage
- **ESLint** pour le linting
- **2 espaces** pour l'indentation
- **Semicolons** obligatoires

```bash
# Formatage
npm run format

# Vérification
npm run lint
```

#### Structure Composants

```jsx
// Ordre dans un composant React
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

import { Button } from './components/ui';
import { useJobs } from './hooks';

const JobCard = ({ job, onApply }) => {
  // Hooks en premier
  const [isLoading, setIsLoading] = useState(false);
  
  // Event handlers
  const handleApply = () => {
    setIsLoading(true);
    onApply(job.id);
  };
  
  // Render
  return (
    <div className="job-card">
      {/* JSX */}
    </div>
  );
};

// PropTypes
JobCard.propTypes = {
  job: PropTypes.object.isRequired,
  onApply: PropTypes.func.isRequired,
};

export default JobCard;
```

### CSS/Tailwind

```jsx
// Organisation des classes Tailwind
<div className={`
  // Layout
  flex flex-col items-center
  
  // Spacing  
  p-4 m-2
  
  // Sizing
  w-full max-w-md
  
  // Appearance
  bg-white border border-gray-200 rounded-lg shadow-md
  
  // States
  hover:shadow-lg hover:border-gold
  
  // Responsive
  sm:p-6 md:max-w-lg lg:max-w-xl
`}>
```

## 🔄 Processus de Pull Request

### Template de PR

Votre PR doit inclure :

```markdown
## Description
Brève description des changements

## Type de changement
- [ ] Bug fix (changement qui corrige un problème)
- [ ] New feature (changement qui ajoute une fonctionnalité)  
- [ ] Breaking change (correction ou fonctionnalité qui casserait la compatibilité)
- [ ] Documentation update

## Tests
- [ ] Tests existants passent
- [ ] Nouveaux tests ajoutés si nécessaire
- [ ] Tests manuels effectués

## Checklist
- [ ] Code respecte les standards du projet
- [ ] Auto-review effectuée
- [ ] Documentation mise à jour si nécessaire
- [ ] Pas de console.log ou print() oubliés
```

### Critères d'Acceptation

✅ **Pull Request acceptée si :**
- Code respecte les standards
- Tests passent
- Fonctionnalité fonctionne correctement
- Documentation mise à jour
- Review approuvée par au moins 1 mainteneur

❌ **Pull Request rejetée si :**
- Tests cassés
- Code ne respecte pas les standards
- Fonctionnalité incomplète
- Conflits non résolus

## 🎯 Types de Contributions

### 🐛 Correction de Bugs

1. Vérifiez qu'un issue existe
2. Créez une branche `bugfix/description`
3. Corrigez avec tests
4. Documentez la correction

### ✨ Nouvelles Fonctionnalités

1. Discutez de la fonctionnalité dans un issue
2. Attendez validation des mainteneurs
3. Créez une branche `feature/nom`
4. Implémentez avec tests
5. Documentez la fonctionnalité

### 🌐 Nouveaux Scrapers

Priorité haute pour ces plateformes :

- **Pôle Emploi** (France)
- **Monster** (International)
- **Glassdoor** (Reviews + Jobs)
- **AngelList** (Startups)
- **Stack Overflow Jobs**

Template pour nouveau scraper :

```python
# backend/app/scrapers/new_platform_scraper.py
from .base_scraper import BaseScraper

class NewPlatformScraper(BaseScraper):
    def __init__(self):
        self.base_url = "https://newplatform.com"
        self.name = "newplatform"
    
    def scrape(self, keywords, job_type, since_date):
        # Implémentation spécifique
        pass
```

### 📚 Documentation

- Corrections typos
- Améliorations README
- Guides tutorials
- Code comments
- API documentation

### 🎨 Design/UX

- Améliorations interface
- Nouvelles animations
- Optimisations mobile
- Accessibilité
- Dark mode (futur)

## 🏷️ Convention de Nommage

### Commits

Suivre [Conventional Commits](https://www.conventionalcommits.org/):

```bash
feat: ajoute scraper LinkedIn
fix: corrige bug pagination
docs: met à jour installation
style: formatage code Python
refactor: restructure dossier scrapers
test: ajoute tests pour Indeed scraper
chore: met à jour dépendances
```

### Branches

- `feature/nom-fonctionnalite`
- `bugfix/description-bug`  
- `hotfix/correction-urgente`
- `docs/amelioration-doc`
- `refactor/restructuration`

### Issues

- **Bug Report** : `[BUG] Scraper Indeed ne fonctionne plus`
- **Feature Request** : `[FEATURE] Ajouter notifications email`
- **Documentation** : `[DOCS] Améliorer guide installation`
- **Enhancement** : `[ENHANCEMENT] Optimiser performance scraping`

## 🆘 Besoin d'Aide ?

- **Discord** : [Lien vers serveur Discord]
- **GitHub Issues** : Pour questions techniques
- **Email** : contact@jobhub-project.com
- **Documentation** : [docs/](docs/)

## 🙏 Reconnaissance

Tous les contributeurs sont listés dans :
- **README.md** - Section contributeurs
- **CONTRIBUTORS.md** - Liste détaillée
- **Releases** - Notes de version

Merci pour votre contribution à JobHub ! 🚀
