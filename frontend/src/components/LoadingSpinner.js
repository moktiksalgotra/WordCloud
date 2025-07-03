import React from 'react';

const LoadingSpinner = ({ message = "Generating your word cloud..." }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8">
      <div className="relative">
        {/* Outer ring */}
        <div className="w-16 h-16 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
        
        {/* Inner ring */}
        <div className="absolute top-2 left-2 w-12 h-12 border-4 border-transparent border-t-primary-400 rounded-full animate-spin" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
      </div>
      
      <p className="mt-4 text-lg text-gray-600 font-medium">{message}</p>
      
      {/* Pulsing dots */}
      <div className="flex space-x-1 mt-2">
        <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse-slow"></div>
        <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse-slow" style={{ animationDelay: '0.2s' }}></div>
        <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse-slow" style={{ animationDelay: '0.4s' }}></div>
      </div>
    </div>
  );
};

export default LoadingSpinner; 