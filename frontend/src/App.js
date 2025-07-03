import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import axios from 'axios';

// Components
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import WordCloudGenerator from './components/WordCloudGenerator';
import Profile from './components/Profile';
import Footer from './components/Footer';

// Styles
import './App.css';

const API_BASE_URL = process.env.NODE_ENV === 'production'
  ? 'https://wordcloud-hro4.onrender.com'
  : 'https://wordcloud-n2ew.onrender.com';

// Configure axios defaults
axios.defaults.baseURL = API_BASE_URL;

// Main App Component
const AppContent = () => {
  const location = useLocation();

  // Hide footer on login and register pages (no longer needed, but keep for future if needed)
  const hideFooter = false;

  return (
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <Navbar />
        <main className="pt-16 flex-1">
          <Routes>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/generator" element={<WordCloudGenerator />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/" element={<Navigate to="/dashboard" />} />
            <Route path="*" element={<Navigate to="/dashboard" />} />
          </Routes>
        </main>
        {!hideFooter && <Footer />}
      </div>
  );
};

// Root App Component
function App() {
  return (
      <Router>
        <AppContent />
      </Router>
  );
}

export default App; 