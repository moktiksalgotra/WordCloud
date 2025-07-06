import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import socket from '../socket';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        // Fetch dashboard statistics
        const statsResponse = await axios.get(`/api/analytics/dashboard`);
        setStats(statsResponse.data.statistics);
      } catch (error) {
        console.error('Error loading dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();

    // Listen for real-time dashboard updates
    const handleDashboardUpdate = (data) => {
      setStats(data.statistics);
    };
    socket.on('dashboard_update', handleDashboardUpdate);

    return () => {
      socket.off('dashboard_update', handleDashboardUpdate);
    };
  }, []);

  const quickActions = [
    {
      title: 'Create Word Cloud',
      description: 'Generate a new word cloud from text',
      icon: 'M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zM21 5a2 2 0 00-2-2h-4a2 2 0 00-2 2v12a4 4 0 004 4h4a2 2 0 002-2V5z',
      link: '/generator',
      color: 'bg-blue-500'
    }
  ];

  const featureCards = [
    {
      title: 'Advanced Text Analysis',
      description: 'Our NLP engine analyzes text to identify key terms, sentiment, and frequency patterns for meaningful word clouds.',
      icon: 'M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z',
      iconColor: 'text-blue-500',
    },
    {
      title: 'Extensive Customization',
      description: 'Personalize fonts, colors, layouts, and shapes to match your brand or presentation needs.',
      icon: 'M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01',
      iconColor: 'text-green-500',
    },
    {
      title: 'Export & Share',
      description: 'Export your word clouds in multiple formats including PNG, JPG, and SVG for presentations or sharing.',
      icon: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12',
      iconColor: 'text-yellow-500',
    },
    {
      title: 'Multiple Input Sources',
      description: 'Generate word clouds from text files, URLs, PDFs, or direct input for maximum flexibility.',
      icon: 'M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m6.75 12H9m1.5-12H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z',
      iconColor: 'text-indigo-500',
    },
    {
      title: 'Language Detection',
      description: 'Automatic language detection and processing for multilingual word cloud generation.',
      icon: 'M10.5 21l5.25-11.25L21 21m-9-3h7.5M3 5.621a48.474 48.474 0 016-.371m0 0c1.12 0 2.233.038 3.334.114M9 5.25V3m3.334 2.364C11.176 10.658 7.69 15.08 3 17.502m9.334-12.138c.896.061 1.785.147 2.666.257m-4.589 8.495a18.023 18.023 0 01-3.827-5.802',
      iconColor: 'text-red-500',
    },
    {
      title: 'Secure User Accounts',
      description: 'Register and log in securely. Your word clouds and data are protected with robust authentication and privacy controls.',
      icon: 'M12 11c1.104 0 2-.896 2-2V7a2 2 0 10-4 0v2c0 1.104.896 2 2 2zm6 2v-2a6 6 0 10-12 0v2a2 2 0 00-2 2v5a2 2 0 002 2h12a2 2 0 002-2v-5a2 2 0 00-2-2z',
      iconColor: 'text-cyan-600',
    }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center w-full">
      <div className="w-full max-w-6xl mx-auto px-4 sm:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-3">
            Welcome to the WordCloud Generator
          </h1>
          <p className="text-lg text-gray-500">Dashboard overview</p>
          <div className="mt-6">
            <Link
              to="/generator"
              className="inline-block px-8 py-3 rounded-full bg-blue-600 text-white font-semibold text-lg shadow hover:bg-blue-700 transition-colors duration-200"
            >
              Get Started
            </Link>
          </div>
        </div>
        <h2 className="text-2xl font-semibold text-gray-800 mb-8 text-center">Features</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {featureCards.map((feature, index) => {
            const bgColors = [
              'bg-blue-50',
              'bg-green-50',
              'bg-yellow-50',
              'bg-pink-50',
              'bg-indigo-50',
              'bg-red-50'
            ];
            const cardBg = bgColors[index % bgColors.length];
            return (
              <div key={index} className={`rounded-2xl shadow-lg p-8 flex flex-col items-center border border-gray-100 ${cardBg} transition-transform hover:scale-[1.025]`}>
                <div className={`w-14 h-14 rounded-full flex items-center justify-center mb-5 ${feature.iconColor} bg-white shadow-md`}>
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={feature.icon} />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold mb-2 text-gray-900 text-center">{feature.title}</h3>
                <p className="text-base text-gray-600 text-center">{feature.description}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 