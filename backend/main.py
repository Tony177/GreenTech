from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from pydantic import BaseModel
import random
import sqlite3
import uvicorn
from jose import JWTError, jwt
import datetime
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
import threading
import time
import sched
from chat_suggestion import router as chat_router

# Carica le variabili d'ambiente da .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Configurazione JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
if not SECRET_KEY or not ALGORITHM:
    raise RuntimeError("SECRET_KEY e ALGORITHM devono essere definiti nel file .env")

# Database setup
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS sensor_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        salinity REAL,
        ph REAL,
        soil_moisture REAL,
        organic_matter REAL
    )''')
    # Prepopola con dati realistici e variabili (10 record)
    c.execute('SELECT COUNT(*) FROM sensor_data')
    if c.fetchone()[0] == 0:
        example_data = [
            ("2025-06-28 08:52:01", 1.2, 6.8, 22.5, 3.1),
            ("2025-06-28 09:23:16", 1.1, 6.7, 23.0, 3.2),
            ("2025-06-28 10:22:56", 1.3, 6.9, 21.8, 3.0),
            ("2025-06-28 11:28:55", 1.4, 7.0, 24.0, 3.3),
            ("2025-06-28 12:11:02", 1.2, 7.1, 22.2, 3.4),
            ("2025-06-28 13:45:11", 1.5, 7.2, 23.5, 3.1),
            ("2025-06-28 14:34:06", 1.3, 7.3, 25.1, 3.6),
            ("2025-06-28 15:11:11", 1.4, 7.2, 24.0, 3.5),
            ("2025-06-28 16:53:56", 1.2, 7.0, 23.2, 3.3),
            ("2025-06-28 17:22:45", 1.3, 6.9, 22.0, 3.2),
        ]
        c.executemany("INSERT INTO sensor_data (timestamp, salinity, ph, soil_moisture, organic_matter) VALUES (?, ?, ?, ?, ?)", example_data)
    conn.commit()
    conn.close()

create_tables()

app = FastAPI()

# Imposta la working directory sul percorso del file main.py
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# CORS: consenti qualsiasi origine (sviluppo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

class User(BaseModel):
    username: str
    password: str

class SensorData(BaseModel):
    timestamp: str
    salinity: float  # Salinità suolo (dS/m)
    ph: float        # pH suolo
    soil_moisture: float  # Umidità suolo (%)
    organic_matter: float # Sostanza organica (%)

class CarbonInput(BaseModel):
    grano_kg: float
    verdura_kg: float
    energia_kwh: float

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Simulazione dati sensori

def simulate_sensor_data():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return {
        "timestamp": now,
        "salinity": round(random.uniform(0.1, 2.5), 2),  # dS/m
        "ph": round(random.uniform(5.5, 8.5), 2),         # pH
        "soil_moisture": round(random.uniform(10, 45), 2), # %
        "organic_matter": round(random.uniform(1, 8), 2),  # %
    }

# Autenticazione
@app.post("/register")
def register(user: User):
    conn = get_db()
    c = conn.cursor()
    hashed_password = pwd_context.hash(user.password)
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user.username, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username già esistente")
    finally:
        conn.close()
    return {"msg": "Registrazione avvenuta con successo"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (form_data.username,))
    user = c.fetchone()
    conn.close()
    if not user or not pwd_context.verify(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Credenziali non valide")
    # Token valido 30 minuti
    token = jwt.encode({
        "sub": form_data.username,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
    }, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token non valido")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token scaduto")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token non valido")

# Endpoint dati sensori
@app.get("/sensors", response_model=SensorData)
def get_sensor_data(user: str = Depends(get_current_user)):
    data = simulate_sensor_data()
    # Salva nel database
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO sensor_data (timestamp, salinity, ph, soil_moisture, organic_matter) VALUES (?, ?, ?, ?, ?)",
              (data["timestamp"], data["salinity"], data["ph"], data["soil_moisture"], data["organic_matter"]))
    conn.commit()
    conn.close()
    return data

@app.get("/dashboard")
def dashboard(user: str = Depends(get_current_user)):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    data = [dict(row) for row in rows]
    return {"data": data}

@app.get("/suggestions")
def suggestions(user: str = Depends(get_current_user)):
    # Logica di esempio per suggerimenti
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT AVG(water_usage), AVG(fertilizer_usage) FROM sensor_data")
    avg_water, avg_fertilizer = c.fetchone()
    conn.close()
    suggestions = []
    if avg_water is not None and avg_water > 50:
        suggestions.append("Riduci l'uso di acqua con irrigazione a goccia.")
    if avg_fertilizer is not None and avg_fertilizer > 5:
        suggestions.append("Ottimizza la fertilizzazione con analisi del suolo.")
    if not suggestions:
        suggestions.append("Le risorse sono ottimizzate.")
    return {"suggestions": suggestions}

@app.post("/carbon_footprint")
def carbon_footprint(input: CarbonInput = Body(...), user: str = Depends(get_current_user)):
    """
    Calcola il carbon footprint totale dell'azienda in base ai parametri forniti:
    - grano_kg: quantità di grano prodotto (kg)
    - verdura_kg: quantità di verdura prodotta (kg)
    - energia_kwh: consumo di energia elettrica (kWh)
    I fattori di emissione sono:
    - Grano: 0.528 kgCO2e/kgDM (dalla cradle-to-gate, include stoccaggio suolo)
    - Verdura: 0.65 kgCO2eq/kg (dalla cradle-to-gate, include produzione e distribuzione)
    - Elettricità: 0.471 kgCO2eq/kWh (rete media tensione, mix nazionale)
    """
    co2_grano = input.grano_kg * 0.528
    co2_verdura = input.verdura_kg * 0.65
    co2_energia = input.energia_kwh * 0.471
    totale = round(co2_grano + co2_verdura + co2_energia, 3)
    return {
        "dettaglio": [
            {"parametro": "Grano (kg)", "quantità": input.grano_kg, "fattore": 0.528, "co2": round(co2_grano, 3), "descrizione": "Grano, dalla cradle-to-gate, include stoccaggio suolo, pesticidi, fertilizzanti, irrigazione, raccolta"},
            {"parametro": "Verdura (kg)", "quantità": input.verdura_kg, "fattore": 0.65, "co2": round(co2_verdura, 3), "descrizione": "Verdura, dalla cradle-to-gate, include produzione e distribuzione"},
            {"parametro": "Energia elettrica (kWh)", "quantità": input.energia_kwh, "fattore": 0.471, "co2": round(co2_energia, 3), "descrizione": "Rete elettrica media tensione, mix nazionale medio"}
        ],
        "totale_kgCO2eq": totale
    }

def periodic_sensor_data(scheduler=None, interval=30):
    if scheduler is None:
        scheduler = sched.scheduler(time.time, time.sleep)
    def job():
        data = simulate_sensor_data()
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO sensor_data (timestamp, salinity, ph, soil_moisture, organic_matter) VALUES (?, ?, ?, ?, ?)",
                  (data["timestamp"], data["salinity"], data["ph"], data["soil_moisture"], data["organic_matter"]))
        conn.commit()
        conn.close()
        scheduler.enter(interval, 1, job)
    scheduler.enter(interval, 1, job)
    threading.Thread(target=scheduler.run, daemon=True).start()

app.include_router(chat_router)

# Forza HTTPS redirect solo se richiesto
if os.environ.get("FORCE_HTTPS", "0") == "1":
    app.add_middleware(HTTPSRedirectMiddleware)

# Avvia il job periodico solo se main
if __name__ == "__main__":
    periodic_sensor_data()
    import ssl
    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_ctx.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
    uvicorn.run(app, host="0.0.0.0", port=8000, ssl_certfile="cert.pem", ssl_keyfile="key.pem")
