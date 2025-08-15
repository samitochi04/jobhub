import React from 'react';
import { Link } from 'react-router-dom';
import { FiHeart, FiGithub, FiLinkedin, FiMail } from 'react-icons/fi';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="mt-auto bg-black/60 backdrop-blur-md border-t border-gold/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Brand Section */}
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-gold to-yellow-400 rounded-lg flex items-center justify-center">
                <span className="text-black font-bold text-sm">JH</span>
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-white to-gold bg-clip-text text-transparent">
                JobHub
              </span>
            </div>
            <p className="text-gray-400 text-sm leading-relaxed">
              Plateforme d'automatisation de recherche d'emploi avec intelligence artificielle. 
              Trouvez votre prochain emploi plus efficacement.
            </p>
          </div>

          {/* Links Section */}
          <div className="space-y-4">
            <h3 className="text-white font-semibold">Navigation</h3>
            <div className="grid grid-cols-2 gap-2">
              {[
                { name: 'Accueil', href: '/' },
                { name: 'Recherches', href: '/searches' },
                { name: 'Emplois', href: '/jobs' },
                { name: 'Statistiques', href: '/stats' },
                { name: 'Paramètres', href: '/settings' },
                { name: 'Documentation', href: '/docs' }
              ].map((link) => (
                <Link
                  key={link.name}
                  to={link.href}
                  className="text-gray-400 hover:text-gold transition-colors duration-200 text-sm"
                >
                  {link.name}
                </Link>
              ))}
            </div>
          </div>

          {/* Contact Section */}
          <div className="space-y-4">
            <h3 className="text-white font-semibold">Contact</h3>
            <div className="flex space-x-4">
              {[
                { icon: FiGithub, href: '#', label: 'GitHub' },
                { icon: FiLinkedin, href: '#', label: 'LinkedIn' },
                { icon: FiMail, href: 'mailto:contact@jobhub.com', label: 'Email' }
              ].map((social) => {
                const Icon = social.icon;
                return (
                  <a
                    key={social.label}
                    href={social.href}
                    className="p-2 rounded-lg bg-white/5 text-gray-400 hover:text-gold hover:bg-white/10 transition-all duration-200"
                    aria-label={social.label}
                  >
                    <Icon className="w-5 h-5" />
                  </a>
                );
              })}
            </div>
            <div className="text-sm text-gray-400">
              <p>Version 1.0.0</p>
              <p>Dernière mise à jour: {new Date().toLocaleDateString('fr-FR')}</p>
            </div>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="mt-8 pt-6 border-t border-gray-800 flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          <div className="text-sm text-gray-400">
            © {currentYear} JobHub. Tous droits réservés.
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-400">
            <span>Fait avec</span>
            <FiHeart className="w-4 h-4 text-red-500 animate-pulse" />
            <span>pour les chercheurs d'emploi</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
