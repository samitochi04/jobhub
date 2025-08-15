import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  FiSearch, 
  FiBriefcase, 
  FiTrendingUp, 
  FiClock, 
  FiUsers, 
  FiTarget,
  FiPlay,
  FiPause,
  FiRefreshCw,
  FiEye,
  FiCalendar,
  FiMapPin
} from 'react-icons/fi';

const Dashboard = () => {
  const [stats, setStats] = useState({
    activeSearches: 0,
    totalJobs: 0,
    todayJobs: 0,
    isRunning: false
  });
  const [recentJobs, setRecentJobs] = useState([]);
  const [searches, setSearches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch statistics
      const statsResponse = await fetch('http://localhost:5000/api/status');
      const statsData = await statsResponse.json();
      
      // Fetch recent jobs
      const jobsResponse = await fetch('http://localhost:5000/api/jobs?limit=5');
      const jobsData = await jobsResponse.json();
      
      // Fetch active searches
      const searchesResponse = await fetch('http://localhost:5000/api/searches');
      const searchesData = await searchesResponse.json();

      setStats({
        activeSearches: searchesData.searches?.length || 0,
        totalJobs: jobsData.jobs?.length || 0,
        todayJobs: jobsData.jobs?.filter(job => {
          const today = new Date().toDateString();
          return new Date(job.created_at).toDateString() === today;
        }).length || 0,
        isRunning: statsData.scheduler_status === 'running'
      });

      setRecentJobs(jobsData.jobs || []);
      setSearches(searchesData.searches || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, icon: Icon, color, trend = null }) => (
    <div className="glass-card rounded-xl p-6 hover:scale-105 transition-transform duration-200">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm font-medium">{title}</p>
          <p className={`text-3xl font-bold ${color} mt-2`}>{value}</p>
          {trend && (
            <p className={`text-sm mt-1 ${trend > 0 ? 'text-green-400' : 'text-red-400'}`}>
              {trend > 0 ? '+' : ''}{trend}% vs hier
            </p>
          )}
        </div>
        <div className={`p-3 rounded-xl ${color.includes('gold') ? 'bg-gold/20' : color.includes('green') ? 'bg-green-500/20' : color.includes('blue') ? 'bg-blue-500/20' : 'bg-purple-500/20'}`}>
          <Icon className={`w-6 h-6 ${color}`} />
        </div>
      </div>
    </div>
  );

  const JobCard = ({ job }) => (
    <div className="glass-card rounded-lg p-4 hover:bg-white/10 transition-all duration-200">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="text-white font-semibold text-lg mb-1 line-clamp-1">
            {job.title}
          </h3>
          <p className="text-gold font-medium mb-2">{job.company}</p>
          <div className="flex items-center space-x-4 text-sm text-gray-400 mb-3">
            <div className="flex items-center space-x-1">
              <FiMapPin className="w-4 h-4" />
              <span>{job.location || 'Non spécifié'}</span>
            </div>
            <div className="flex items-center space-x-1">
              <FiCalendar className="w-4 h-4" />
              <span>{new Date(job.created_at).toLocaleDateString('fr-FR')}</span>
            </div>
          </div>
          <p className="text-gray-300 text-sm line-clamp-2">
            {job.description || 'Description non disponible'}
          </p>
        </div>
        <div className="ml-4 flex flex-col items-end space-y-2">
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
            job.status === 'new' ? 'bg-blue-500/20 text-blue-400' :
            job.status === 'applied' ? 'bg-green-500/20 text-green-400' :
            'bg-gray-500/20 text-gray-400'
          }`}>
            {job.status === 'new' ? 'Nouveau' : 
             job.status === 'applied' ? 'Postulé' : 'Archivé'}
          </span>
          <button className="p-2 rounded-lg bg-white/5 text-gray-400 hover:text-gold hover:bg-white/10 transition-all duration-200">
            <FiEye className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );

  const SearchCard = ({ search }) => (
    <div className="glass-card rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-white font-semibold">{search.keywords}</h3>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          search.is_active ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'
        }`}>
          {search.is_active ? 'Actif' : 'Inactif'}
        </span>
      </div>
      <div className="space-y-2 text-sm text-gray-400">
        <div className="flex justify-between">
          <span>Localisation:</span>
          <span className="text-white">{search.location || 'Partout'}</span>
        </div>
        <div className="flex justify-between">
          <span>Fréquence:</span>
          <span className="text-white">{search.frequency || 'Quotidienne'}</span>
        </div>
        <div className="flex justify-between">
          <span>Dernière exécution:</span>
          <span className="text-white">
            {search.last_run ? new Date(search.last_run).toLocaleDateString('fr-FR') : 'Jamais'}
          </span>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <FiRefreshCw className="w-8 h-8 text-gold animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Chargement du tableau de bord...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="pt-20 pb-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-gold bg-clip-text text-transparent mb-2">
                Tableau de Bord
              </h1>
              <p className="text-gray-400">
                Vue d'ensemble de vos recherches d'emploi automatisées
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
                stats.isRunning 
                  ? 'bg-green-500/20 border border-green-500/30 text-green-400' 
                  : 'bg-red-500/20 border border-red-500/30 text-red-400'
              }`}>
                {stats.isRunning ? <FiPlay className="w-4 h-4" /> : <FiPause className="w-4 h-4" />}
                <span className="font-medium">
                  {stats.isRunning ? 'Automatisation active' : 'Automatisation arrêtée'}
                </span>
              </div>
              <button 
                onClick={fetchDashboardData}
                className="p-2 rounded-lg bg-white/5 text-gray-400 hover:text-gold hover:bg-white/10 transition-all duration-200"
              >
                <FiRefreshCw className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Recherches Actives"
            value={stats.activeSearches}
            icon={FiSearch}
            color="text-gold"
          />
          <StatCard
            title="Total Emplois"
            value={stats.totalJobs}
            icon={FiBriefcase}
            color="text-blue-400"
          />
          <StatCard
            title="Emplois Aujourd'hui"
            value={stats.todayJobs}
            icon={FiTrendingUp}
            color="text-green-400"
          />
          <StatCard
            title="Taux de Réussite"
            value="89%"
            icon={FiTarget}
            color="text-purple-400"
          />
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Recent Jobs */}
          <div className="lg:col-span-2">
            <div className="glass-card rounded-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-white flex items-center">
                  <FiBriefcase className="w-5 h-5 mr-2 text-gold" />
                  Emplois Récents
                </h2>
                <Link 
                  to="/jobs" 
                  className="text-gold hover:text-yellow-300 text-sm font-medium transition-colors"
                >
                  Voir tous →
                </Link>
              </div>
              <div className="space-y-4">
                {recentJobs.length > 0 ? (
                  recentJobs.slice(0, 5).map((job) => (
                    <JobCard key={job.id} job={job} />
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <FiBriefcase className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Aucun emploi trouvé pour le moment</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Active Searches */}
          <div>
            <div className="glass-card rounded-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-white flex items-center">
                  <FiSearch className="w-5 h-5 mr-2 text-gold" />
                  Recherches
                </h2>
                <Link 
                  to="/searches" 
                  className="text-gold hover:text-yellow-300 text-sm font-medium transition-colors"
                >
                  Gérer →
                </Link>
              </div>
              <div className="space-y-4">
                {searches.length > 0 ? (
                  searches.map((search) => (
                    <SearchCard key={search.id} search={search} />
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <FiSearch className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Aucune recherche configurée</p>
                    <button className="mt-4 px-4 py-2 bg-gold text-black rounded-lg font-medium hover:bg-yellow-400 transition-colors">
                      Créer une recherche
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
