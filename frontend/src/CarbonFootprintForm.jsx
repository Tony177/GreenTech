import React, { useState } from "react";
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'https://localhost:8000';

export default function CarbonFootprintForm({ token }) {
  const [grano, setGrano] = useState(() => localStorage.getItem('cf_grano') || 0);
  const [verdura, setVerdura] = useState(() => localStorage.getItem('cf_verdura') || 0);
  const [energia, setEnergia] = useState(() => localStorage.getItem('cf_energia') || 0);
  const [result, setResult] = useState(() => {
    const saved = localStorage.getItem('cf_result');
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Validazione semplice: tutti devono essere float >= 0
    if (
      isNaN(parseFloat(grano)) || parseFloat(grano) < 0 ||
      isNaN(parseFloat(verdura)) || parseFloat(verdura) < 0 ||
      isNaN(parseFloat(energia)) || parseFloat(energia) < 0
    ) {
      setError("Tutti i valori devono essere numeri validi maggiori o uguali a zero.");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await fetch(`${BACKEND_URL}/carbon_footprint`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          grano_kg: parseFloat(grano),
          verdura_kg: parseFloat(verdura),
          energia_kwh: parseFloat(energia)
        })
      });
      if (!res.ok) throw new Error("Errore nel calcolo");
      const data = await res.json();
      setResult(data);
      localStorage.setItem('cf_result', JSON.stringify(data));
    } catch (e) {
      setError("Errore nel calcolo del carbon footprint");
    }
    setLoading(false);
  };

  // Salva i valori inseriti
  React.useEffect(() => {
    localStorage.setItem('cf_grano', grano);
    localStorage.setItem('cf_verdura', verdura);
    localStorage.setItem('cf_energia', energia);
  }, [grano, verdura, energia]);

  return (
    <div style={{ background: '#fff', borderRadius: 12, boxShadow: '0 2px 8px #1976d233', padding: 32, maxWidth: 600, margin: '32px auto' }}>
      <h3 style={{ color: '#111', textAlign: 'center' }}>Calcolo Carbon Footprint Aziendale</h3>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <label style={{ color: '#111' }}>Grano prodotto (kg)
          <input type="number" min="0" step="any" value={grano} onChange={e => setGrano(e.target.value)} required />
        </label>
        <label style={{ color: '#111' }}>Verdura prodotta (kg)
          <input type="number" min="0" step="any" value={verdura} onChange={e => setVerdura(e.target.value)} required />
        </label>
        <label style={{ color: '#111' }}>Consumo energia elettrica (kWh)
          <input type="number" min="0" step="any" value={energia} onChange={e => setEnergia(e.target.value)} required />
        </label>
        <button type="submit" style={{ background: '#388e3c', color: '#fff', border: 'none', borderRadius: 6, padding: '0.7rem 0', fontWeight: 'bold', fontSize: 16 }}>Calcola</button>
      </form>
      {loading && <div style={{ marginTop: 16, color: '#111' }}>Calcolo in corso...</div>}
      {error && <div style={{ color: 'red', marginTop: 16 }}>{error}</div>}
      {result && (
        <div style={{ marginTop: 24 }}>
          <h4 style={{ color: '#111' }}>Risultato dettagliato:</h4>
          <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: 16 }}>
            <thead>
              <tr style={{ background: '#e3f2fd', color: '#111' }}>
                <th>Parametro</th>
                <th>Quantità</th>
                <th>Fattore (kgCO₂eq/unità)</th>
                <th>CO₂eq</th>
                <th>Descrizione</th>
              </tr>
            </thead>
            <tbody>
              {result.dettaglio.map((r, i) => (
                <tr key={i} style={{ color: '#111' }}>
                  <td>{r.parametro}</td>
                  <td>{r.quantità}</td>
                  <td>{r.fattore}</td>
                  <td>{r.co2}</td>
                  <td style={{ fontSize: 13 }}>{r.descrizione}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ fontWeight: 600, fontSize: 18, color: '#111' }}>
            Totale: {result.totale_kgCO2eq} kg CO₂eq
          </div>
        </div>
      )}
    </div>
  );
}
