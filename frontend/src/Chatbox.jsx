import React, { useState } from "react";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'https://localhost:8000';

export default function Chatbox({ sensors, footprint, token, answer, setAnswer, loading, setLoading, error, setError }) {
  const [input, setInput] = useState("");

  const ask = async () => {
    setLoading(true);
    setError("");
    setAnswer("");
    try {
      const res = await fetch(`${BACKEND_URL}/chat_suggestion`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          user_input: input,
          sensors,
          footprint
        })
      });
      const data = await res.json();
      setAnswer(data.answer);
    } catch (e) {
      setError("Errore nella richiesta al sistema di suggerimento.");
    }
    setLoading(false);
  };

  return (
    <div style={{ background: '#fff', borderRadius: 12, boxShadow: '0 2px 8px #1976d233', padding: 32, width: 900, minWidth: 0, maxWidth: '100%', margin: '32px auto' }}>
      <h3 style={{ color: '#1976d2', textAlign: 'center' }}>Chat Agronomica Intelligente</h3>
      <textarea
        value={input}
        onChange={e => setInput(e.target.value)}
        placeholder="Scrivi la tua richiesta in linguaggio naturale..."
        rows={3}
        style={{ width: '100%', borderRadius: 6, border: '1px solid #bbb', padding: 8, fontSize: 16, resize: 'none' }}
      />
      <button
        onClick={ask}
        disabled={!input.trim() || loading}
        style={{ marginTop: 8, background: '#388e3c', color: '#fff', border: 'none', borderRadius: 6, padding: '0.5rem 1.2rem', fontWeight: 'bold', fontSize: 16 }}
      >Chiedi</button>
      {loading && <div style={{ marginTop: 12, color: '#111' }}>Attendi risposta...</div>}
      {error && <div style={{ color: 'red', marginTop: 12 }}>{error}</div>}
      {answer && <div style={{ marginTop: 16, background: '#fff', borderRadius: 6, padding: 12, color: '#111' }}>{answer}</div>}
    </div>
  );
}
