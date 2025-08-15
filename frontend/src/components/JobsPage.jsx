import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  FiBriefcase, 
  FiMapPin, 
  FiCalendar, 
  FiExternalLink,
  FiEye,
  FiBookmark,
  FiFilter,
  FiSearch,
  FiCheck,
  FiX
} from 'react-icons/fi';

const JobsPage = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedJob, setSelectedJob] = useState(null);
  const [filters, setFilters] = useState({
    status: 'all',
    search: '',
    company: '',
    location: ''
  });

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/jobs');
      const data = await response.json();
      setJobs(data.jobs || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching jobs:', error);
      setLoading(false);
    }
  };

  const updateJobStatus = async (jobId, newStatus) => {
    try {
      await fetch(`http://localhost:5000/api/jobs/${jobId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus }),
      });
      await fetchJobs();
    } catch (error) {
      console.error('Error updating job status:', error);
    }
  };

  const filteredJobs = jobs.filter(job => {
    const matchesStatus = filters.status === 'all' || job.status === filters.status;
    const matchesSearch = !filters.search || 
      job.title.toLowerCase().includes(filters.search.toLowerCase()) ||
      job.company.toLowerCase().includes(filters.search.toLowerCase());
    const matchesCompany = !filters.company || 
      job.company.toLowerCase().includes(filters.company.toLowerCase());
    const matchesLocation = !filters.location || 
      (job.location && job.location.toLowerCase().includes(filters.location.toLowerCase()));

    return matchesStatus && matchesSearch && matchesCompany && matchesLocation;
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'new': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'applied': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'rejected': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'interview': return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
      case 'saved': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'new': return 'Nouveau';
      case 'applied': return 'Candidature envoyée';
      case 'rejected': return 'Rejeté';
      case 'interview': return 'Entretien';
      case 'saved': return 'Sauvegardé';
      default: return 'Non défini';
    }
  };

  const JobCard = ({ job, onClick }) => (
    <div 
      className="glass-card rounded-lg p-6 hover:bg-white/10 transition-all duration-200 cursor-pointer"
      onClick={() => onClick(job)}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-start justify-between mb-3">
            <div>
              <h3 className="text-lg font-semibold text-white mb-1 line-clamp-1">
                {job.title}
              </h3>
              <p className="text-gold font-medium text-base">{job.company}</p>
            </div>
            <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(job.status)}`}>
              {getStatusText(job.status)}
            </span>
          </div>
          
          <div className="flex items-center space-x-6 text-sm text-gray-400 mb-4">
            <div className="flex items-center space-x-2">
              <FiMapPin className="w-4 h-4" />
              <span>{job.location || 'Non spécifié'}</span>
            </div>
            <div className="flex items-center space-x-2">
              <FiCalendar className="w-4 h-4" />
              <span>{new Date(job.created_at).toLocaleDateString('fr-FR')}</span>
            </div>
          </div>

          <p className="text-gray-300 text-sm line-clamp-2 mb-4">
            {job.description || 'Description non disponible'}
          </p>

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  updateJobStatus(job.id, job.status === 'saved' ? 'new' : 'saved');
                }}
                className={`p-2 rounded-lg transition-all duration-200 ${
                  job.status === 'saved' 
                    ? 'bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30' 
                    : 'bg-white/5 text-gray-400 hover:text-yellow-400 hover:bg-yellow-500/20'
                }`}
                title="Sauvegarder"
              >
                <FiBookmark className="w-4 h-4" />
              </button>
              
              {job.url && (
                <a
                  href={job.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="p-2 rounded-lg bg-white/5 text-gray-400 hover:text-gold hover:bg-white/10 transition-all duration-200"
                  title="Voir l'offre originale"
                >
                  <FiExternalLink className="w-4 h-4" />
                </a>
              )}
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  updateJobStatus(job.id, 'applied');
                }}
                className="px-3 py-1.5 bg-green-500/20 text-green-400 hover:bg-green-500/30 rounded-lg text-xs font-medium transition-all duration-200"
                title="Marquer comme postulé"
              >
                <FiCheck className="w-3 h-3" />
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  updateJobStatus(job.id, 'rejected');
                }}
                className="px-3 py-1.5 bg-red-500/20 text-red-400 hover:bg-red-500/30 rounded-lg text-xs font-medium transition-all duration-200"
                title="Marquer comme rejeté"
              >
                <FiX className="w-3 h-3" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const JobDetail = ({ job, onClose }) => (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="glass-card rounded-xl p-6 max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-start justify-between mb-6">
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-white mb-2">{job.title}</h2>
            <p className="text-gold text-lg font-semibold">{job.company}</p>
          </div>
          <div className="flex items-center space-x-3 ml-4">
            <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(job.status)}`}>
              {getStatusText(job.status)}
            </span>
            <button
              onClick={onClose}
              className="p-2 rounded-lg bg-white/5 text-gray-400 hover:text-white hover:bg-white/10 transition-all duration-200"
            >
              <FiX className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="space-y-4">
            <div>
              <h4 className="text-white font-semibold mb-2">Informations</h4>
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Localisation:</span>
                  <span className="text-white">{job.location || 'Non spécifié'}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Date de création:</span>
                  <span className="text-white">{new Date(job.created_at).toLocaleDateString('fr-FR')}</span>
                </div>
                {job.salary && (
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Salaire:</span>
                    <span className="text-white">{job.salary}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <h4 className="text-white font-semibold">Actions</h4>
            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => updateJobStatus(job.id, 'applied')}
                className="flex items-center space-x-2 px-4 py-2 bg-green-500/20 text-green-400 hover:bg-green-500/30 rounded-lg transition-all duration-200"
              >
                <FiCheck className="w-4 h-4" />
                <span>Marquer comme postulé</span>
              </button>
              <button
                onClick={() => updateJobStatus(job.id, job.status === 'saved' ? 'new' : 'saved')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                  job.status === 'saved'
                    ? 'bg-yellow-500/30 text-yellow-400'
                    : 'bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30'
                }`}
              >
                <FiBookmark className="w-4 h-4" />
                <span>{job.status === 'saved' ? 'Sauvegardé' : 'Sauvegarder'}</span>
              </button>
              {job.url && (
                <a
                  href={job.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 rounded-lg transition-all duration-200"
                >
                  <FiExternalLink className="w-4 h-4" />
                  <span>Voir l'offre</span>
                </a>
              )}
            </div>
          </div>
        </div>

        {job.description && (
          <div>
            <h4 className="text-white font-semibold mb-4">Description</h4>
            <div className="prose prose-invert max-w-none">
              <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">
                {job.description}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="pt-20 min-h-screen flex items-center justify-center">
        <div className="text-center">
          <FiBriefcase className="w-8 h-8 text-gold animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Chargement des emplois...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="pt-20 pb-10 px-4 sm:px-6 lg:px-8 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-gold bg-clip-text text-transparent mb-2">
            Emplois Trouvés
          </h1>
          <p className="text-gray-400">
            {filteredJobs.length} emploi{filteredJobs.length > 1 ? 's' : ''} trouvé{filteredJobs.length > 1 ? 's' : ''}
          </p>
        </div>

        {/* Filters */}
        <div className="glass-card rounded-xl p-6 mb-8">
          <div className="flex items-center space-x-4 mb-4">
            <FiFilter className="w-5 h-5 text-gold" />
            <h3 className="text-lg font-semibold text-white">Filtres</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Statut
              </label>
              <select
                value={filters.status}
                onChange={(e) => setFilters({...filters, status: e.target.value})}
                className="w-full px-3 py-2 bg-white/5 border border-gray-600 rounded-lg text-white text-sm focus:border-gold focus:ring-1 focus:ring-gold transition-colors"
              >
                <option value="all">Tous</option>
                <option value="new">Nouveau</option>
                <option value="saved">Sauvegardé</option>
                <option value="applied">Postulé</option>
                <option value="interview">Entretien</option>
                <option value="rejected">Rejeté</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Recherche
              </label>
              <input
                type="text"
                value={filters.search}
                onChange={(e) => setFilters({...filters, search: e.target.value})}
                className="w-full px-3 py-2 bg-white/5 border border-gray-600 rounded-lg text-white text-sm placeholder-gray-400 focus:border-gold focus:ring-1 focus:ring-gold transition-colors"
                placeholder="Titre ou entreprise..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Entreprise
              </label>
              <input
                type="text"
                value={filters.company}
                onChange={(e) => setFilters({...filters, company: e.target.value})}
                className="w-full px-3 py-2 bg-white/5 border border-gray-600 rounded-lg text-white text-sm placeholder-gray-400 focus:border-gold focus:ring-1 focus:ring-gold transition-colors"
                placeholder="Nom de l'entreprise..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Localisation
              </label>
              <input
                type="text"
                value={filters.location}
                onChange={(e) => setFilters({...filters, location: e.target.value})}
                className="w-full px-3 py-2 bg-white/5 border border-gray-600 rounded-lg text-white text-sm placeholder-gray-400 focus:border-gold focus:ring-1 focus:ring-gold transition-colors"
                placeholder="Ville, région..."
              />
            </div>
          </div>
        </div>

        {/* Jobs List */}
        <div className="space-y-4">
          {filteredJobs.length > 0 ? (
            filteredJobs.map((job) => (
              <JobCard
                key={job.id}
                job={job}
                onClick={setSelectedJob}
              />
            ))
          ) : (
            <div className="text-center py-12">
              <div className="glass-card rounded-xl p-12 max-w-md mx-auto">
                <FiBriefcase className="w-16 h-16 text-gold mx-auto mb-6 opacity-50" />
                <h3 className="text-xl font-semibold text-white mb-4">
                  Aucun emploi trouvé
                </h3>
                <p className="text-gray-400 mb-6">
                  {jobs.length > 0 
                    ? "Aucun emploi ne correspond à vos filtres actuels."
                    : "Vos recherches automatisées n'ont pas encore trouvé d'emplois. Vérifiez vos paramètres de recherche."
                  }
                </p>
                <Link
                  to="/searches"
                  className="px-6 py-3 bg-gradient-to-r from-gold to-yellow-400 text-black font-semibold rounded-lg hover:from-yellow-400 hover:to-gold transition-all duration-200 inline-block"
                >
                  Configurer mes recherches
                </Link>
              </div>
            </div>
          )}
        </div>

        {/* Job Detail Modal */}
        {selectedJob && (
          <JobDetail
            job={selectedJob}
            onClose={() => setSelectedJob(null)}
          />
        )}
      </div>
    </div>
  );
};

export default JobsPage;
