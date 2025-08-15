import React, { useState, useEffect } from 'react';
import { 
  FiSearch, 
  FiPlus, 
  FiEdit3, 
  FiTrash2, 
  FiPlay, 
  FiPause,
  FiMapPin,
  FiClock,
  FiSettings,
  FiCalendar
} from 'react-icons/fi';

const SearchesPage = () => {
  const [searches, setSearches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingSearch, setEditingSearch] = useState(null);

  const [formData, setFormData] = useState({
    keywords: '',
    job_types: ['alternance'],
    platforms: ['linkedin'],
    duration_minutes: 15,
    is_active: true
  });

  useEffect(() => {
    fetchSearches();
  }, []);

  const fetchSearches = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/searches');
      const data = await response.json();
      setSearches(data.searches || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching searches:', error);
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const url = editingSearch 
        ? `http://localhost:5000/api/searches/${editingSearch.id}`
        : 'http://localhost:5000/api/searches';
      
      const method = editingSearch ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        await fetchSearches();
        setShowCreateForm(false);
        setEditingSearch(null);
        setFormData({
          keywords: '',
          job_types: ['alternance'],
          platforms: ['linkedin'],
          duration_minutes: 15,
          is_active: true
        });
      }
    } catch (error) {
      console.error('Error saving search:', error);
    }
  };

  const handleEdit = (search) => {
    setEditingSearch(search);
    setFormData({
      keywords: search.keywords || '',
      job_types: search.job_types || ['alternance'],
      platforms: search.platforms || ['linkedin'],
      duration_minutes: search.duration_minutes || 15,
      is_active: search.is_active
    });
    setShowCreateForm(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cette recherche ?')) {
      try {
        await fetch(`http://localhost:5000/api/searches/${id}`, {
          method: 'DELETE',
        });
        await fetchSearches();
      } catch (error) {
        console.error('Error deleting search:', error);
      }
    }
  };

  const toggleSearchStatus = async (id, currentStatus) => {
    try {
      await fetch(`http://localhost:5000/api/searches/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_active: !currentStatus }),
      });
      await fetchSearches();
    } catch (error) {
      console.error('Error toggling search status:', error);
    }
  };

  const SearchCard = ({ search }) => (
    <div className="glass-card rounded-xl p-6 hover:scale-105 transition-all duration-200">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <h3 className="text-xl font-semibold text-white">{search.keywords}</h3>
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${
              search.is_active 
                ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                : 'bg-gray-500/20 text-gray-400 border border-gray-500/30'
            }`}>
              {search.is_active ? 'Actif' : 'Inactif'}
            </span>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm text-gray-400">
            <div className="flex items-center space-x-2">
              <FiMapPin className="w-4 h-4 text-gold" />
              <span>{search.location || 'Partout'}</span>
            </div>
            <div className="flex items-center space-x-2">
              <FiClock className="w-4 h-4 text-gold" />
              <span className="capitalize">{search.frequency || 'Quotidienne'}</span>
            </div>
            <div className="flex items-center space-x-2">
              <FiCalendar className="w-4 h-4 text-gold" />
              <span>
                Créé le {new Date(search.created_at).toLocaleDateString('fr-FR')}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <FiSettings className="w-4 h-4 text-gold" />
              <span>
                {search.platforms?.join(', ') || 'LinkedIn'}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2 ml-4">
          <button
            onClick={() => toggleSearchStatus(search.id, search.is_active)}
            className={`p-2 rounded-lg transition-all duration-200 ${
              search.is_active
                ? 'bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30'
                : 'bg-green-500/20 text-green-400 hover:bg-green-500/30'
            }`}
            title={search.is_active ? 'Pause' : 'Activer'}
          >
            {search.is_active ? <FiPause className="w-4 h-4" /> : <FiPlay className="w-4 h-4" />}
          </button>
          <button
            onClick={() => handleEdit(search)}
            className="p-2 rounded-lg bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 transition-all duration-200"
            title="Modifier"
          >
            <FiEdit3 className="w-4 h-4" />
          </button>
          <button
            onClick={() => handleDelete(search.id)}
            className="p-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-all duration-200"
            title="Supprimer"
          >
            <FiTrash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {search.last_run && (
        <div className="mt-4 pt-4 border-t border-gray-700">
          <p className="text-xs text-gray-400">
            Dernière exécution: {new Date(search.last_run).toLocaleString('fr-FR')}
          </p>
        </div>
      )}
    </div>
  );

  if (loading) {
    return (
      <div className="pt-20 min-h-screen flex items-center justify-center">
        <div className="text-center">
          <FiSearch className="w-8 h-8 text-gold animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Chargement des recherches...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="pt-20 pb-10 px-4 sm:px-6 lg:px-8 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-gold bg-clip-text text-transparent mb-2">
              Mes Recherches
            </h1>
            <p className="text-gray-400">
              Gérez vos recherches d'emploi automatisées
            </p>
          </div>
          <button
            onClick={() => {
              setShowCreateForm(true);
              setEditingSearch(null);
              setFormData({
                keywords: '',
                job_types: ['alternance'],
                platforms: ['linkedin'],
                duration_minutes: 15,
                is_active: true
              });
            }}
            className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-gold to-yellow-400 text-black font-semibold rounded-lg hover:from-yellow-400 hover:to-gold transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
          >
            <FiPlus className="w-5 h-5" />
            <span>Nouvelle Recherche</span>
          </button>
        </div>

        {/* Create/Edit Form */}
        {showCreateForm && (
          <div className="glass-card rounded-xl p-6 mb-8">
            <h2 className="text-xl font-semibold text-white mb-6">
              {editingSearch ? 'Modifier la Recherche' : 'Créer une Nouvelle Recherche'}
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Mots-clés *
                  </label>
                  <input
                    type="text"
                    value={formData.keywords}
                    onChange={(e) => setFormData({...formData, keywords: e.target.value})}
                    className="w-full px-4 py-3 bg-white/5 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-gold focus:ring-1 focus:ring-gold transition-colors"
                    placeholder="Ex: Développeur React, Designer UX..."
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Types d'emploi *
                  </label>
                  <div className="space-y-2">
                    {['alternance', 'stage', 'cdi', 'cdd', 'freelance'].map((type) => (
                      <label key={type} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={formData.job_types.includes(type)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setFormData({
                                ...formData,
                                job_types: [...formData.job_types, type]
                              });
                            } else {
                              setFormData({
                                ...formData,
                                job_types: formData.job_types.filter(t => t !== type)
                              });
                            }
                          }}
                          className="rounded border-gray-600 text-gold focus:ring-gold"
                        />
                        <span className="text-gray-300 capitalize">{type}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Intervalle (minutes)
                  </label>
                  <select
                    value={formData.duration_minutes}
                    onChange={(e) => setFormData({...formData, duration_minutes: parseInt(e.target.value)})}
                    className="w-full px-4 py-3 bg-white/5 border border-gray-600 rounded-lg text-white focus:border-gold focus:ring-1 focus:ring-gold transition-colors"
                  >
                    <option value={5}>5 minutes</option>
                    <option value={15}>15 minutes</option>
                    <option value={30}>30 minutes</option>
                    <option value={60}>1 heure</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Plateformes
                  </label>
                  <div className="space-y-2">
                    {['linkedin', 'indeed', 'welcome-to-the-jungle'].map((platform) => (
                      <label key={platform} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={formData.platforms.includes(platform)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setFormData({
                                ...formData,
                                platforms: [...formData.platforms, platform]
                              });
                            } else {
                              setFormData({
                                ...formData,
                                platforms: formData.platforms.filter(p => p !== platform)
                              });
                            }
                          }}
                          className="rounded border-gray-600 text-gold focus:ring-gold"
                        />
                        <span className="text-gray-300 capitalize">{platform.replace('-', ' ')}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                  className="rounded border-gray-600 text-gold focus:ring-gold"
                />
                <label htmlFor="is_active" className="text-gray-300">
                  Activer cette recherche immédiatement
                </label>
              </div>

              <div className="flex items-center justify-end space-x-4 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="px-6 py-2 text-gray-400 hover:text-white transition-colors"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-6 py-3 bg-gradient-to-r from-gold to-yellow-400 text-black font-semibold rounded-lg hover:from-yellow-400 hover:to-gold transition-all duration-200"
                >
                  {editingSearch ? 'Mettre à Jour' : 'Créer la Recherche'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Searches Grid */}
        <div className="space-y-6">
          {searches.length > 0 ? (
            searches.map((search) => (
              <SearchCard key={search.id} search={search} />
            ))
          ) : (
            <div className="text-center py-12">
              <div className="glass-card rounded-xl p-12 max-w-md mx-auto">
                <FiSearch className="w-16 h-16 text-gold mx-auto mb-6 opacity-50" />
                <h3 className="text-xl font-semibold text-white mb-4">
                  Aucune recherche configurée
                </h3>
                <p className="text-gray-400 mb-6">
                  Commencez par créer votre première recherche automatisée pour trouver les emplois qui vous correspondent.
                </p>
                <button
                  onClick={() => setShowCreateForm(true)}
                  className="px-6 py-3 bg-gradient-to-r from-gold to-yellow-400 text-black font-semibold rounded-lg hover:from-yellow-400 hover:to-gold transition-all duration-200"
                >
                  Créer ma première recherche
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SearchesPage;
