import { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import Dashboard from './pages/Dashboard';
import AIAssistant from './pages/AIAssistant';
import Projects from './pages/Projects';
import Settings from './pages/Settings';
import Monetization from './pages/Monetization';
import Layout from './components/Layout';
import { statsApi } from './services/api';

function App() {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null;
    if (savedTheme) {
      setTheme(savedTheme);
    } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setTheme('dark');
    }
  }, []);

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Monitor health status
  useQuery({
    queryKey: ['health'],
    queryFn: statsApi.getHealthStatus,
    refetchInterval: 30000,
  });

  return (
    <Routes>
      <Route path="/" element={<Layout theme={theme} setTheme={setTheme} />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="ai-assistant" element={<AIAssistant />} />
        <Route path="projects" element={<Projects />} />
        <Route path="monetization" element={<Monetization />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  );
}

export default App;