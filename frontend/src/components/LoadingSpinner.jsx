import React from 'react';
import { FiLoader } from 'react-icons/fi';

const LoadingSpinner = ({ size = 'md', text = 'Chargement...', className = '' }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  };

  return (
    <div className={`flex flex-col items-center justify-center space-y-4 ${className}`}>
      <div className="relative">
        <FiLoader className={`${sizeClasses[size]} text-gold animate-spin`} />
        <div className="absolute inset-0 rounded-full border-2 border-gold/20 animate-pulse"></div>
      </div>
      {text && (
        <p className="text-gray-400 text-sm font-medium animate-pulse">{text}</p>
      )}
    </div>
  );
};

const FullPageLoader = ({ text = 'Chargement en cours...', subText }) => {
  return (
    <div className="pt-20 min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="glass-card rounded-2xl p-12 max-w-sm mx-auto">
          <LoadingSpinner size="xl" text={text} />
          {subText && (
            <p className="text-gray-500 text-xs mt-4">{subText}</p>
          )}
        </div>
      </div>
    </div>
  );
};

const InlineLoader = ({ text = 'Chargement...', className = '' }) => {
  return (
    <div className={`flex items-center justify-center p-8 ${className}`}>
      <LoadingSpinner size="md" text={text} />
    </div>
  );
};

const ButtonLoader = ({ size = 'sm', className = '' }) => {
  return (
    <FiLoader className={`${size === 'sm' ? 'w-4 h-4' : 'w-5 h-5'} animate-spin ${className}`} />
  );
};

export { LoadingSpinner, FullPageLoader, InlineLoader, ButtonLoader };
export default LoadingSpinner;
