import React from 'react';
import { Link } from 'react-router-dom';
import { FiHome, FiSearch, FiAlertTriangle } from 'react-icons/fi';

const NotFound = () => {
  return (
    <div className="pt-20 pb-10 px-4 sm:px-6 lg:px-8 min-h-screen flex items-center justify-center">
      <div className="text-center max-w-md mx-auto">
        <div className="glass-card rounded-2xl p-12">
          {/* 404 Animation */}
          <div className="relative mb-8">
            <div className="text-8xl font-bold bg-gradient-to-r from-gold to-yellow-400 bg-clip-text text-transparent opacity-20">
              404
            </div>
            <div className="absolute inset-0 flex items-center justify-center">
              <FiAlertTriangle className="w-16 h-16 text-gold animate-pulse" />
            </div>
          </div>

          {/* Title */}
          <h1 className="text-3xl font-bold text-white mb-4">
            Page Introuvable
          </h1>
          
          {/* Description */}
          <p className="text-gray-400 mb-8 leading-relaxed">
            Oups ! Il semble que cette page n'existe pas ou a été déplacée. 
            Vérifiez l'URL ou retournez à l'accueil pour continuer votre recherche d'emploi.
          </p>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/"
              className="flex items-center justify-center space-x-2 px-6 py-3 bg-gradient-to-r from-gold to-yellow-400 text-black font-semibold rounded-lg hover:from-yellow-400 hover:to-gold transition-all duration-200 transform hover:scale-105"
            >
              <FiHome className="w-5 h-5" />
              <span>Retour à l'accueil</span>
            </Link>
            
            <Link
              to="/searches"
              className="flex items-center justify-center space-x-2 px-6 py-3 bg-white/5 text-white border border-gray-600 rounded-lg hover:bg-white/10 hover:border-gold transition-all duration-200"
            >
              <FiSearch className="w-5 h-5" />
              <span>Mes recherches</span>
            </Link>
          </div>

          {/* Additional Info */}
          <div className="mt-8 pt-6 border-t border-gray-700">
            <p className="text-xs text-gray-500">
              Si le problème persiste, n'hésitez pas à nous contacter pour obtenir de l'aide.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
