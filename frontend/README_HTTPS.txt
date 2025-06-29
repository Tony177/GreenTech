// Copia i certificati self-signed dal backend al frontend per HTTPS locale
// Puoi usare questi comandi da terminale:
//
// cd frontend
// cp ../backend/cert.pem .
// cp ../backend/key.pem .
//
// Se preferisci, puoi generare nuovi certificati con:
// openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=localhost"
//
// Dopo aver copiato i certificati, riavvia il dev server Vite e accetta il certificato nel browser.
