# Guida Windows

## Setup Rapido

### 1. Prerequisiti

- **Docker Desktop**: Scarica da https://www.docker.com/products/docker-desktop
  - Assicurati che Docker Desktop sia avviato
  - Verifica: `docker --version` nel terminale

- **NVIDIA GPU (opzionale)**: Solo per modalità GPU
  - Driver NVIDIA aggiornati
  - NVIDIA Container Toolkit installato

### 2. Avvio Automatico

Esegui lo script batch:
```cmd
start.bat
```

Lo script ti guiderà attraverso:
1. Verifica Docker installato
2. Scelta modalità (CPU o GPU)
3. Verifica GPU (se GPU selezionata)
4. Avvio automatico dei servizi

### 3. Avvio Manuale

#### CPU
```cmd
docker compose --profile cpu up --build
```

#### GPU
```cmd
docker compose --profile gpu up --build
```

### 4. Stop Servizi

Esegui:
```cmd
stop.bat
```

Oppure manualmente:
```cmd
docker compose down
```

### 5. Pulizia Completa

Esegui:
```cmd
clean.bat
```

Rimuove container, immagini e volumi (preserva ./data).

## Script Disponibili

- `start.bat` - Avvia i servizi (con menu interattivo)
- `stop.bat` - Ferma i servizi
- `clean.bat` - Pulizia completa (container, immagini, cache)

## Troubleshooting Windows

### Docker non parte
1. Assicurati che Docker Desktop sia avviato
2. Verifica che WSL2 sia installato (requisito Docker Desktop)
3. Riavvia Docker Desktop

### Porta già in uso
```cmd
# Verifica cosa usa la porta 8000
netstat -ano | findstr :8000

# Verifica cosa usa la porta 3000
netstat -ano | findstr :3000
```

### GPU non riconosciuta
1. Installa NVIDIA Container Toolkit
2. Riavvia Docker Desktop
3. Verifica: `docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi`

### Permessi
Se hai problemi di permessi:
- Esegui PowerShell/CMD come Amministratore
- Oppure aggiungi utente al gruppo "docker-users"

## Accesso

Dopo l'avvio:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Note

- I file generati sono salvati in `.\data\outputs\`
- I log sono visibili nel terminale Docker Compose
- Per vedere solo i log di un servizio: `docker compose logs -f backend`

