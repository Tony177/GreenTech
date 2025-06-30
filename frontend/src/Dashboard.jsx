import React, { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";
import Chatbox from './Chatbox';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'https://localhost:8000';

const params = [
  { key: "salinity", label: "Salinità del suolo (dS/m)", color: "#1976d2" }, // blu
  { key: "ph", label: "pH del suolo", color: "#fbc02d" }, // giallo
  { key: "soil_moisture", label: "Umidità del suolo (%)", color: "#388e3c" }, // verde
  { key: "organic_matter", label: "Sostanza organica (%)", color: "#0288d1" } // blu acqua
];

function Dashboard({ refresh, onLogout, CarbonForm }) {
  const [data, setData] = useState([]);
  const [carbon, setCarbon] = useState(0);
  const [loading, setLoading] = useState(true);
  const [cfTotale, setCfTotale] = useState(() => {
    const saved = localStorage.getItem('cf_result');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        return parsed?.totale_kgCO2eq ?? null;
      } catch { return null; }
    }
    return null;
  });
  // Ricava footprint dettagliato (oggetto) se presente
  const [cfDettaglio, setCfDettaglio] = useState(() => {
    const saved = localStorage.getItem('cf_result');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch { return null; }
    }
    return null;
  });
  const [chatAnswer, setChatAnswer] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    setLoading(true);
    fetch(`${BACKEND_URL}/dashboard`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then((res) => res.json())
      .then((res) => {
        setData(res.data.reverse()); // reverse per ordine cronologico
        setCarbon(res.carbon_footprint);
        setLoading(false);
      });
  }, [refresh]);

  // Aggiorna il totale quando cambia il risultato del form
  React.useEffect(() => {
    const saved = localStorage.getItem('cf_result');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setCfTotale(parsed?.totale_kgCO2eq ?? null);
      } catch { setCfTotale(null); }
    } else {
      setCfTotale(null);
    }
  }, [localStorage.getItem('cf_result')]);
  // Aggiorna cfDettaglio quando cambia il risultato del form
  React.useEffect(() => {
    const saved = localStorage.getItem('cf_result');
    if (saved) {
      try {
        setCfDettaglio(JSON.parse(saved));
      } catch { setCfDettaglio(null); }
    } else {
      setCfDettaglio(null);
    }
  }, [localStorage.getItem('cf_result')]);

  if (loading) return <div style={{color:'#111'}}>Caricamento dati...</div>;

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto", padding: 0 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{marginLeft: 0, textAlign: 'center', color: '#111', flex: 1}}>Green Tech Dashboard</h2>
        <button onClick={onLogout} style={{marginRight: 24, background: '#1976d2', color: '#fff', border: 'none', borderRadius: 6, padding: '0.5rem 1.2rem', fontWeight: 'bold', cursor: 'pointer', fontSize: 16}}>Logout</button>
      </div>
      {CarbonForm}
      <div style={{textAlign: 'center', margin: '16px 0 0 0', fontSize: 20, color: '#388e3c', fontWeight: 600}}>
        Carbon footprint stimata (ultimo dato): {cfTotale !== null ? `${cfTotale} kg CO₂eq` : <span style={{color:'#bdbdbd'}}>non ancora calcolato</span>}
      </div>
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 48,
        marginTop: 32,
        alignItems: 'center'
      }}>
        {params.map((p) => (
          <div key={p.key} style={{ background: '#fff', borderRadius: 12, boxShadow: '0 2px 8px #1976d233', padding: 32, width: 900, minWidth: 0, maxWidth: '100%' }}>
            <h4>{p.label}</h4>
            <ResponsiveContainer width={900} height={340}>
              <LineChart data={data} margin={{ top: 5, right: 40, left: 40, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" tick={{ fontSize: 16 }} tickFormatter={v => v.split(' ')[1] || v} />
                <YAxis tick={{ fontSize: 16 }} label={{ value: p.label.split('(')[1]?.replace(')', ''), angle: -90, position: 'insideLeft', offset: 10 }} />
                <Tooltip formatter={(value) => `${value} ${p.label.split('(')[1]?.replace(')', '') || ''}`}
                  labelFormatter={l => `Orario: ${l.split(' ')[1] || l}`}
                />
                <Legend />
                <Line type="monotone" dataKey={p.key} stroke={p.color} dot={true} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ))}
      </div>
      <Chatbox
        sensors={data[0] || {}}
        footprint={cfDettaglio}
        token={localStorage.getItem('token')}
        answer={chatAnswer}
        setAnswer={setChatAnswer}
        loading={chatLoading}
        setLoading={setChatLoading}
        error={chatError}
        setError={setChatError}
      />
    </div>
  );
}

export default Dashboard;
