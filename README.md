# 🚀 JobHub

> **Automatisez votre recherche d'emploi avec une veille intelligente des offres**

JobHub est une application web qui scrape automatiquement les principales plateformes de recrutement et vous notifie en temps réel des nouvelles offres correspondant à vos critères. Fini les candidatures tardives - soyez le premier à postuler !

[![MIT License](https://img.shields.io/badge/License-MIT-gold.svg)](https://choosealicense.com/licenses/mit/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTORS.md)

## ✨ Fonctionnalités

🔍 **Recherche intelligente**
- Scraping automatique de multiple plateformes (Indeed, LinkedIn, Welcome to the Jungle, APEC)
- Filtres avancés par mots-clés, type de contrat, localisation
- Détection des nouvelles offres en temps réel

⏰ **Veille automatisée** 
- Cron jobs personnalisables (toutes les 15 minutes par défaut)
- Notifications instantanées des nouvelles opportunités
- Historique complet des offres trouvées

🎨 **Interface élégante**
- Design moderne et professionnel (noir/or/blanc)
- Responsive design pour tous les appareils
- Animations fluides et micro-interactions

📊 **Tableau de bord**
- Statistiques en temps réel
- Suivi des performances de recherche
- Gestion des recherches actives

## 🛠️ Stack Technique

### Frontend
- **React 18** avec Vite (JSX, pas de TypeScript)
- **Tailwind CSS v3** pour le styling
- **WebSocket** pour les mises à jour temps réel
- Design responsive avec patterns graphiques

### Backend
- **Flask API** avec architecture modulaire
- **Cron Jobs** pour l'automatisation
- **SQLite** (dev) / **PostgreSQL** (prod)
- **Beautiful Soup** + **Selenium** pour le scraping

## 🚀 Installation

### Prérequis
- Python 3.9+
- Node.js 18+
- Git

### Installation rapide

```bash
# Cloner le repository
git clone https://github.com/votre-username/jobhub.git
cd jobhub

# Backend
cd backend
pip install -r requirements.txt
flask run

# Frontend (nouveau terminal)
cd ../frontend
npm install
npm run dev
```

### Avec Docker (Recommandé)

```bash
# Cloner et lancer avec Docker Compose
git clone https://github.com/votre-username/jobhub.git
cd jobhub
docker-compose up --build
```

L'application sera disponible sur `http://localhost:3000`

## 💻 Utilisation

1. **Créer une recherche**
   - Remplir le formulaire avec vos critères
   - Définir la fréquence de vérification (15min par défaut)
   - Lancer la veille automatique

2. **Surveiller les résultats**
   - Dashboard en temps réel
   - Nouvelles offres surlignées
   - Links directs vers les annonces

3. **Gérer vos recherches**
   - Pauser/reprendre les cron jobs
   - Modifier les critères
   - Consulter l'historique

## 📋 Roadmap

- [ ] **v1.0** - MVP avec scraping basic
- [ ] **v1.1** - WebSocket temps réel
- [ ] **v1.2** - Notifications email/push
- [ ] **v1.3** - ML pour scoring des offres
- [ ] **v2.0** - API publique + mobile app

## 🤝 Contribution

Les contributions sont les bienvenues ! Consultez [CONTRIBUTORS.md](CONTRIBUTORS.md) pour commencer.

### Comment contribuer
1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push sur la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Documentation

- [Guide d'architecture](docs/architecture.md)
- [Contexte technique](docs/CONTEXT.md)
- [Guide de développement](docs/GUIDE.md)

## ⚖️ Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- Inspiré par la frustration des candidatures tardives
- Merci à la communauté open source pour les outils utilisés
- Créé avec ❤️ pour les chercheurs d'emploi

---

**⭐ Si ce projet vous aide dans votre recherche d'emploi, n'hésitez pas à lui donner une étoile !**
