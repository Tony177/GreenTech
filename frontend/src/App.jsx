import React, { useState, useEffect } from 'react';
import Login from './Login';
import Register from './Register';
import Dashboard from './Dashboard';
import CarbonFootprintForm from './CarbonFootprintForm';
import './App.css';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'https://localhost:8000';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [showRegister, setShowRegister] = useState(false);
  const [refresh, setRefresh] = useState(0);

  useEffect(() => {
    if (!token) return;
    const interval = setInterval(() => setRefresh(r => r + 1), 30000); // 30 secondi
    return () => clearInterval(interval);
  }, [token]);

  const handleLogin = t => {
    setToken(t);
    localStorage.setItem('token', t);
  };
  const handleLogout = () => {
    setToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('carbonInputs'); // Rimuove dati calcolo
    localStorage.removeItem('carbonResult'); // Rimuove risultato calcolo
  };

  // Rimuove dati calcolo alla chiusura della pagina
  useEffect(() => {
    const clearCalcData = () => {
      localStorage.removeItem('carbonInputs');
      localStorage.removeItem('carbonResult');
    };
    window.addEventListener('beforeunload', clearCalcData);
    return () => window.removeEventListener('beforeunload', clearCalcData);
  }, []);

  if (token) return <>
    <Dashboard refresh={refresh} onLogout={handleLogout} CarbonForm={<CarbonFootprintForm token={token} />} />
  </>;
  if (showRegister) return <Register onRegister={() => setShowRegister(false)} onSwitchToLogin={() => setShowRegister(false)} />;
  return <Login onLogin={handleLogin} onSwitchToRegister={() => setShowRegister(true)} />;
}

export default App;
