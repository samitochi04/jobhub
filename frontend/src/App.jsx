import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import SearchesPage from './components/SearchesPage';
import JobsPage from './components/JobsPage';
import StatsPage from './components/StatsPage';
import NotFound from './components/NotFound';
import './App.css';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/searches" element={<SearchesPage />} />
          <Route path="/jobs" element={<JobsPage />} />
          <Route path="/stats" element={<StatsPage />} />
          <Route path="/settings" element={<Dashboard />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
