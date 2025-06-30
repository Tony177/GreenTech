# Piattaforma di ottimizzazione risorse agricole

## Funzionalità
- Backend Python (FastAPI): simula dati sensori IoT, autenticazione JWT, dashboard, suggerimenti, calcolo carbon footprint.
- Frontend React (Vite): dashboard, autenticazione, suggerimenti, visualizzazione dati.
- Database SQLite per utenti e dati sensori.
- Sicurezza: autenticazione, JWT, CORS.

## Avvio Backend
1. Installa le dipendenze:
   ```sh
   pip install -r backend/requirements.txt
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

## Configurazione variabili d'ambiente

### Backend (`backend/.env`)
Crea un file `backend/.env` con le seguenti variabili obbligatorie:

```
SECRET_KEY="SUPERSECRETKEYHERE"
ALGORITHM="HS512"                        
HF_TOKEN="hf_LONGTOKENHERE"
FORCE_HTTPS=0
```

- `SECRET_KEY`: chiave segreta usata per firmare e verificare i token JWT, fondamentale per la sicurezza dell'autenticazione.
- `ALGORITHM`: algoritmo di cifratura utilizzato per i JWT (es. HS256 o HS512).
- `HF_TOKEN`: token di autenticazione per accedere alle API HuggingFace (ad esempio per suggerimenti AI o NLP).
- `FORCE_HTTPS`: se impostato a 1, il backend accetta solo connessioni HTTPS; se 0, accetta anche HTTP (utile in sviluppo).

### Frontend (`frontend/.env`)
Crea un file `frontend/.env` con la seguente variabile:

```
VITE_BACKEND_URL=https://localhost:8000
```

Questa variabile viene usata dal frontend per tutte le chiamate API verso il backend. Modificala se il backend gira su un host o porta diversi.

## Note
- Il backend espone API su http://localhost:8000 (o https se configurato)
- Il frontend comunica con il backend tramite la variabile d'ambiente `VITE_BACKEND_URL`.
