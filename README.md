# Piattaforma di ottimizzazione risorse agricole

## Funzionalità
- Backend Python (FastAPI): simula dati sensori IoT, autenticazione JWT, dashboard, suggerimenti, calcolo carbon footprint.
- Frontend React (Vite): dashboard, autenticazione, suggerimenti, visualizzazione dati.
- Database SQLite per utenti e dati sensori.
- Sicurezza: autenticazione, JWT, CORS.

## Avvio Backend
1. Installa le dipendenze:
   ```sh
   pip install fastapi uvicorn pydantic python-jose[cryptography] python-jwt transformers torch
   ```
2. Avvia il backend:
   ```sh
   cd backend
   python main.py
   ```

## Avvio Frontend
1. Aggiorna Node.js (consigliato >=18):
   ```sh
   node -v
   # Se <18, aggiorna Node.js
   ```
2. Installa le dipendenze (se non già presenti) ed avvia il frontend:
   ```sh
   npm install
   npm run dev
   ```

## Note
- Il backend espone API su http://localhost:8000
- Il frontend comunica con il backend tramite fetch/axios.
