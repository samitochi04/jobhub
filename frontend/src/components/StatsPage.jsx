import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { 
  FiTrendingUp, 
  FiBarChart, 
  FiPieChart, 
  FiActivity,
  FiBriefcase,
  FiSearch,
  FiClock,
  FiTarget
} from 'react-icons/fi';

const StatsPage = () => {
  const [stats, setStats] = useState({
    totalJobs: 0,
    activeSearches: 0,
    successRate: 0,
    averageJobsPerDay: 0
  });
  const [chartData, setChartData] = useState({
    jobsOverTime: [],
    jobsByStatus: [],
    jobsByCompany: [],
    searchPerformance: []
  });
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('7d'); // 7d, 30d, 90d

  useEffect(() => {
    fetchStatsData();
  }, [timeRange]);

  const fetchStatsData = async () => {
    try {
      // Fetch jobs and searches
      const [jobsResponse, searchesResponse] = await Promise.all([
        fetch('http://localhost:5000/api/jobs'),
        fetch('http://localhost:5000/api/searches')
      ]);

      const jobsData = await jobsResponse.json();
      const searchesData = await searchesResponse.json();

      const jobs = jobsData.jobs || [];
      const searches = searchesData.searches || [];

      // Calculate basic stats
      const totalJobs = jobs.length;
      const activeSearches = searches.filter(s => s.is_active).length;
      const appliedJobs = jobs.filter(j => j.status === 'applied').length;
      const successRate = totalJobs > 0 ? Math.round((appliedJobs / totalJobs) * 100) : 0;

      // Calculate jobs over time
      const jobsOverTime = generateJobsOverTime(jobs, timeRange);
      const jobsByStatus = generateJobsByStatus(jobs);
      const jobsByCompany = generateJobsByCompany(jobs);
      const searchPerformance = generateSearchPerformance(searches, jobs);

      setStats({
        totalJobs,
        activeSearches,
        successRate,
        averageJobsPerDay: Math.round(totalJobs / Math.max(getDaysInRange(timeRange), 1))
      });

      setChartData({
        jobsOverTime,
        jobsByStatus,
        jobsByCompany,
        searchPerformance
      });

      setLoading(false);
    } catch (error) {
      console.error('Error fetching stats:', error);
      setLoading(false);
    }
  };

  const getDaysInRange = (range) => {
    switch (range) {
      case '7d': return 7;
      case '30d': return 30;
      case '90d': return 90;
      default: return 7;
    }
  };

  const generateJobsOverTime = (jobs, range) => {
    const days = getDaysInRange(range);
    const endDate = new Date();
    const startDate = new Date(endDate.getTime() - (days - 1) * 24 * 60 * 60 * 1000);

    const data = [];
    
    for (let i = 0; i < days; i++) {
      const date = new Date(startDate.getTime() + i * 24 * 60 * 60 * 1000);
      const dateStr = date.toISOString().split('T')[0];
      const jobsOnDate = jobs.filter(job => {
        // Validation de la date avant de l'utiliser
        const jobDate = job.date_found || job.created_at || job.date_posted;
        if (!jobDate) return false;
        
        try {
          const parsedDate = new Date(jobDate);
          if (isNaN(parsedDate.getTime())) return false;
          return parsedDate.toISOString().split('T')[0] === dateStr;
        } catch (error) {
          console.warn('Invalid date format:', jobDate);
          return false;
        }
      }).length;

      data.push({
        date: date.toLocaleDateString('fr-FR', { month: 'short', day: 'numeric' }),
        jobs: jobsOnDate,
        cumulative: data.reduce((sum, item) => sum + item.jobs, 0) + jobsOnDate
      });
    }

    return data;
  };

  const generateJobsByStatus = (jobs) => {
    const statusCounts = {
      'Nouveau': jobs.filter(j => j.status === 'new').length,
      'Sauvegardé': jobs.filter(j => j.status === 'saved').length,
      'Postulé': jobs.filter(j => j.status === 'applied').length,
      'Entretien': jobs.filter(j => j.status === 'interview').length,
      'Rejeté': jobs.filter(j => j.status === 'rejected').length,
    };

    return Object.entries(statusCounts)
      .filter(([_, count]) => count > 0)
      .map(([status, count]) => ({ name: status, value: count }));
  };

  const generateJobsByCompany = (jobs) => {
    const companyCounts = {};
    jobs.forEach(job => {
      const company = job.company || 'Non spécifié';
      companyCounts[company] = (companyCounts[company] || 0) + 1;
    });

    return Object.entries(companyCounts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10)
      .map(([company, count]) => ({ 
        company: company.length > 20 ? company.substring(0, 20) + '...' : company, 
        jobs: count 
      }));
  };

  const generateSearchPerformance = (searches, jobs) => {
    return searches.map(search => {
      const searchJobs = jobs.filter(job => 
        job.title.toLowerCase().includes(search.keywords.toLowerCase()) ||
        job.description?.toLowerCase().includes(search.keywords.toLowerCase())
      );
      
      return {
        name: search.keywords.length > 15 ? search.keywords.substring(0, 15) + '...' : search.keywords,
        jobs: searchJobs.length,
        active: search.is_active ? 1 : 0
      };
    });
  };

  const COLORS = ['#FFD700', '#FFA500', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57'];

  const StatCard = ({ title, value, icon: Icon, color, subtitle }) => (
    <div className="glass-card rounded-xl p-6 hover:scale-105 transition-transform duration-200">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm font-medium">{title}</p>
          <p className={`text-3xl font-bold ${color} mt-2`}>{value}</p>
          {subtitle && (
            <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
          )}
        </div>
        <div className={`p-3 rounded-xl ${color.includes('gold') ? 'bg-gold/20' : color.includes('green') ? 'bg-green-500/20' : color.includes('blue') ? 'bg-blue-500/20' : 'bg-purple-500/20'}`}>
          <Icon className={`w-6 h-6 ${color}`} />
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="pt-20 min-h-screen flex items-center justify-center">
        <div className="text-center">
          <FiBarChart className="w-8 h-8 text-gold animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Chargement des statistiques...</p>
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
              Statistiques
            </h1>
            <p className="text-gray-400">
              Analysez les performances de vos recherches d'emploi
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="px-4 py-2 bg-white/5 border border-gray-600 rounded-lg text-white text-sm focus:border-gold focus:ring-1 focus:ring-gold transition-colors"
            >
              <option value="7d">7 derniers jours</option>
              <option value="30d">30 derniers jours</option>
              <option value="90d">90 derniers jours</option>
            </select>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Emplois"
            value={stats.totalJobs}
            icon={FiBriefcase}
            color="text-gold"
            subtitle="Emplois découverts"
          />
          <StatCard
            title="Recherches Actives"
            value={stats.activeSearches}
            icon={FiSearch}
            color="text-blue-400"
            subtitle="Recherches en cours"
          />
          <StatCard
            title="Taux de Candidature"
            value={`${stats.successRate}%`}
            icon={FiTarget}
            color="text-green-400"
            subtitle="Emplois avec candidature"
          />
          <StatCard
            title="Moyenne/Jour"
            value={stats.averageJobsPerDay}
            icon={FiActivity}
            color="text-purple-400"
            subtitle="Nouveaux emplois"
          />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Jobs Over Time */}
          <div className="glass-card rounded-xl p-6">
            <div className="flex items-center mb-6">
              <FiTrendingUp className="w-5 h-5 text-gold mr-2" />
              <h3 className="text-xl font-semibold text-white">Évolution des Emplois</h3>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={chartData.jobsOverTime}>
                <defs>
                  <linearGradient id="colorJobs" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#FFD700" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#FFD700" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(0, 0, 0, 0.8)', 
                    border: '1px solid #FFD700',
                    borderRadius: '8px'
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="jobs"
                  stroke="#FFD700"
                  fillOpacity={1}
                  fill="url(#colorJobs)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Jobs by Status */}
          <div className="glass-card rounded-xl p-6">
            <div className="flex items-center mb-6">
              <FiPieChart className="w-5 h-5 text-gold mr-2" />
              <h3 className="text-xl font-semibold text-white">Répartition par Statut</h3>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={chartData.jobsByStatus}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {chartData.jobsByStatus.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(0, 0, 0, 0.8)', 
                    border: '1px solid #FFD700',
                    borderRadius: '8px'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Jobs by Company */}
          <div className="glass-card rounded-xl p-6">
            <div className="flex items-center mb-6">
              <FiBarChart className="w-5 h-5 text-gold mr-2" />
              <h3 className="text-xl font-semibold text-white">Top Entreprises</h3>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData.jobsByCompany} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis type="number" stroke="#9CA3AF" />
                <YAxis dataKey="company" type="category" width={80} stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(0, 0, 0, 0.8)', 
                    border: '1px solid #FFD700',
                    borderRadius: '8px'
                  }}
                />
                <Bar dataKey="jobs" fill="#FFD700" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Search Performance */}
          <div className="glass-card rounded-xl p-6">
            <div className="flex items-center mb-6">
              <FiSearch className="w-5 h-5 text-gold mr-2" />
              <h3 className="text-xl font-semibold text-white">Performance des Recherches</h3>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData.searchPerformance}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(0, 0, 0, 0.8)', 
                    border: '1px solid #FFD700',
                    borderRadius: '8px'
                  }}
                />
                <Bar dataKey="jobs" fill="#4ECDC4" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Additional Insights */}
        <div className="mt-8 glass-card rounded-xl p-6">
          <h3 className="text-xl font-semibold text-white mb-6">Insights & Recommandations</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="text-center p-4">
              <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <FiClock className="w-6 h-6 text-blue-400" />
              </div>
              <h4 className="text-white font-semibold mb-2">Meilleure Période</h4>
              <p className="text-gray-400 text-sm">
                La plupart des offres sont publiées en début de semaine
              </p>
            </div>
            
            <div className="text-center p-4">
              <div className="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <FiTarget className="w-6 h-6 text-green-400" />
              </div>
              <h4 className="text-white font-semibold mb-2">Optimisation</h4>
              <p className="text-gray-400 text-sm">
                Ajustez vos mots-clés pour améliorer la pertinence
              </p>
            </div>
            
            <div className="text-center p-4">
              <div className="w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <FiTrendingUp className="w-6 h-6 text-purple-400" />
              </div>
              <h4 className="text-white font-semibold mb-2">Croissance</h4>
              <p className="text-gray-400 text-sm">
                Vos recherches deviennent plus efficaces avec le temps
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatsPage;
