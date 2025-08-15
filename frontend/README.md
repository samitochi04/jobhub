# JobHub Frontend

Interface utilisateur moderne et responsive pour la plateforme JobHub d'automatisation de recherche d'emploi.

## 🎨 Design System

### Couleurs
- **Primary (Or)**: #FFD700 (gold)
- **Secondaire**: #FFA500 (orange)
- **Noir**: #0A0A0B (noir profond)
- **Blanc**: #FFFFFF
- **Fond**: Gradients sombres avec effets glassmorphism

### Caractéristiques Design
- **Glassmorphism**: Effets de verre avec transparence et flou
- **Responsive Design**: Compatible tous appareils
- **Animations fluides**: Transitions CSS et micro-interactions
- **Typographie moderne**: Inter font family
- **Icônes**: React Icons (Feather icons)

## 🚀 Technologies

- **React 19.1.1**: Framework frontend moderne
- **Vite**: Build tool ultra-rapide
- **Tailwind CSS v3**: Framework CSS utilitaire
- **React Router**: Navigation côté client
- **React Icons**: Bibliothèque d'icônes
- **Recharts**: Graphiques et statistiques

## 📦 Installation

```bash
# Installer les dépendances
npm install

# Démarrer le serveur de développement
npm run dev

# Build pour la production
npm run build

# Prévisualiser le build
npm run preview
```

## 🏗️ Structure du Projet

```
frontend/
├── src/
│   ├── components/           # Composants React
│   │   ├── Layout.jsx       # Layout principal
│   │   ├── Header.jsx       # Navigation
│   │   ├── Footer.jsx       # Pied de page
│   │   ├── Dashboard.jsx    # Tableau de bord
│   │   ├── SearchesPage.jsx # Gestion des recherches
│   │   ├── JobsPage.jsx     # Liste des emplois
│   │   ├── StatsPage.jsx    # Statistiques
│   │   ├── NotFound.jsx     # Page 404
│   │   └── LoadingSpinner.jsx # Composants de chargement
│   ├── App.jsx              # Composant racine
│   ├── App.css              # Styles globaux
│   ├── index.css            # Styles Tailwind
│   └── main.jsx             # Point d'entrée
├── public/
│   ├── jobhub-favicon.svg   # Favicon personnalisé
│   └── index.html           # Template HTML
├── tailwind.config.js       # Configuration Tailwind
├── vite.config.js          # Configuration Vite
└── package.json            # Dépendances
```

## 🎯 Fonctionnalités

### Dashboard
- Vue d'ensemble des statistiques
- Emplois récents
- Recherches actives
- Indicateur de statut en temps réel

### Gestion des Recherches
- Créer/modifier/supprimer des recherches
- Activer/désactiver les recherches
- Configuration des paramètres
- Interface intuitive avec formulaires

### Emplois
- Liste paginée avec filtres
- Détails des offres en modal
- Gestion des statuts (nouveau, postulé, rejeté)
- Actions rapides (sauvegarder, postuler)

### Statistiques
- Graphiques interactifs (Recharts)
- Évolution temporelle
- Répartition par statut
- Performance des recherches
- Insights et recommandations

### Interface
- Navigation responsive avec menu mobile
- Thème sombre avec effets glassmorphism
- Animations fluides et micro-interactions
- États de chargement élégants
- Page 404 personnalisée

## 🔌 API Integration

Le frontend communique avec l'API Flask backend:

```javascript
// Exemple d'appel API
const fetchJobs = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/jobs');
    const data = await response.json();
    setJobs(data.jobs || []);
  } catch (error) {
    console.error('Error fetching jobs:', error);
  }
};
```

### Endpoints utilisés
- `GET /api/jobs` - Récupérer les emplois
- `GET /api/searches` - Récupérer les recherches
- `POST /api/searches` - Créer une recherche
- `PUT /api/searches/:id` - Modifier une recherche
- `DELETE /api/searches/:id` - Supprimer une recherche
- `GET /api/status` - Statut du système

## 🎨 Classes Tailwind Personnalisées

```css
/* Effet glassmorphism */
.glass-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
}

/* Troncature de texte */
.line-clamp-1 { /* ... */ }
.line-clamp-2 { /* ... */ }

/* Animation flottante */
.animate-float {
  animation: float 3s ease-in-out infinite;
}
```

## 📱 Responsive Design

- **Mobile First**: Design optimisé mobile d'abord
- **Breakpoints Tailwind**: sm, md, lg, xl, 2xl
- **Navigation adaptative**: Menu hamburger sur mobile
- **Grilles flexibles**: Auto-adaptables selon l'écran
- **Composants modulaires**: Réutilisables sur tous formats

## 🎭 États de l'Interface

### Chargement
- Spinners élégants avec animations
- États de chargement contextuels
- Feedback utilisateur constant

### Erreurs
- Page 404 personnalisée
- Gestion gracieuse des erreurs API
- Messages d'erreur informatifs

### Vide
- États vides avec illustrations
- Call-to-actions encourageantes
- Guide utilisateur intégré

## 🔧 Configuration

### Variables d'Environnement
```env
VITE_API_URL=http://localhost:5000
```

### Tailwind Config
Configuration personnalisée avec:
- Palette de couleurs JobHub
- Extensions utilitaires
- Animations personnalisées
- Plugins supplémentaires

## 🚀 Déploiement

```bash
# Build de production
npm run build

# Les fichiers sont générés dans dist/
# Prêts pour déploiement statique (Vercel, Netlify, etc.)
```

## 📈 Performance

- **Vite HMR**: Rechargement à chaud ultra-rapide
- **Tree Shaking**: Bundle optimisé automatiquement  
- **Code Splitting**: Chargement par route
- **Images optimisées**: SVG et formats modernes
- **CSS Optimisé**: Tailwind purge automatique

## 🎯 Prochaines Étapes

- [ ] Système de notifications en temps réel
- [ ] Mode hors ligne avec cache
- [ ] Paramètres utilisateur avancés
- [ ] Export des données (PDF, Excel)
- [ ] Tests automatisés (Jest + Testing Library)
- [ ] PWA (Progressive Web App)
- [ ] Thème clair/sombre
- [ ] Internationalisation (i18n)

---

*Développé avec ❤️ pour automatiser votre recherche d'emploi*+ Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
