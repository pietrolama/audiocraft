# AudioCraft Text-to-Audio Generator

Web-app completa per generare audio da testo usando Meta AudioCraft (MusicGen e AudioGen).

## 🚀 Caratteristiche

- **Generazione Audio**: MusicGen per musica e AudioGen per effetti sonori
- **Modelli Multipli**: Supporto per musicgen-small, musicgen-medium e audiogen-medium
- **CPU e GPU**: Funziona sia su CPU che GPU (CUDA)
- **Progresso Live**: Aggiornamenti in tempo reale via SSE
- **Interfaccia Moderna**: Frontend Next.js con TailwindCSS, dark mode, i18n
- **Cronologia Locale**: Salvataggio risultati in IndexedDB
- **Rate Limiting**: Protezione contro abusi
- **Containerizzato**: Docker e docker-compose pronti all'uso

## 📋 Requisiti

### CPU
- Docker e Docker Compose
- 4GB+ RAM consigliati
- ~2GB spazio disco per modelli

### GPU
- Docker con supporto NVIDIA Container Toolkit
- GPU NVIDIA con 4GB+ VRAM per musicgen-medium
- CUDA 12.1+ supportato

## 🛠️ Installazione e Uso

### Windows (Script Automatici)

Esegui semplicemente:
```cmd
start.bat
```

Vedi [README_WINDOWS.md](README_WINDOWS.md) per dettagli.

### Linux/Mac (Manuale)

### 1. Clona il repository

```bash
git clone https://github.com/pietrolama/audiocraft.git
cd audiocraft
```

### 2. Configura variabili ambiente

```bash
cp .env.example .env
# Modifica .env secondo necessità (vedi .env.example per tutte le opzioni)
```

### 3. Esegui con Docker Compose

#### Opzione CPU (più lenta, ma funziona ovunque)
```bash
docker compose --profile cpu up --build
```

#### Opzione GPU (più veloce, richiede NVIDIA GPU)
```bash
docker compose --profile gpu up --build
```

I servizi saranno disponibili su:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 4. Esegui in sviluppo (senza Docker)

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📖 API Endpoints

### `POST /api/generate`
Crea un nuovo job di generazione audio.

**Body:**
```json
{
  "model": "musicgen-small",
  "prompt": "cinematic ambient with evolving pads",
  "duration": 12,
  "seed": 42,
  "temperature": 1.0,
  "top_k": 250,
  "top_p": 0.0,
  "cfg_coef": 3.0,
  "stereo": true,
  "sample_rate": 32000,
  "format": "wav"
}
```

**Response:**
```json
{
  "job_id": "uuid",
  "status": "queued",
  "estimated_seconds": 20
}
```

### `GET /api/jobs/{job_id}`
Ottieni lo stato di un job.

**Response:**
```json
{
  "job_id": "uuid",
  "status": "running",
  "progress": 37,
  "message": "generating audio",
  "result_url": "/api/files/audio.wav"
}
```

### `GET /api/jobs/{job_id}/events`
Stream SSE per progresso live.

### `GET /api/files/{filename}`
Scarica il file audio generato.

### `GET /api/models`
Lista modelli disponibili con metadata.

## 🎯 Preset Rapidi

### CPU Friendly
- Modello: `musicgen-small`
- Durata: ≤10s
- Configurazione ottimizzata per velocità

### GPU Quality
- Modello: `musicgen-medium`
- Durata: ≤30s
- Configurazione ottimizzata per qualità

## 🧪 Testing

```bash
# Test backend
cd backend
pytest -v

# Test smoke (genera audio reale)
pytest tests/test_generate_smoke.py -v
```

## 📊 Modelli Disponibili

| Modello | Tipo | VRAM | Qualità | Velocità |
|---------|------|------|---------|----------|
| musicgen-small | Musica | ~2GB | Base | ⚡⚡⚡ |
| musicgen-medium | Musica | ~4GB | Alta | ⚡⚡ |
| audiogen-medium | SFX | ~2GB | Media | ⚡⚡⚡ |

## ⚙️ Configurazione

Variabili d'ambiente principali (vedi [.env.example](.env.example) per la lista completa):

```env
DEVICE=auto              # auto|cpu|cuda
MODEL_DEFAULT=musicgen-small
MAX_DURATION=30
RATE_LIMIT_PER_HOUR=20
OUTPUT_DIR=/data/outputs
AUDIO_FORMAT=wav         # wav|mp3
HUGGINGFACE_TOKEN=       # Opzionale, richiesto per AudioGen
```

## 🐛 Troubleshooting

### Out of Memory
- Riduci `MAX_DURATION`
- Usa `musicgen-small` invece di `medium`
- Aumenta swap se su CPU

### GPU non riconosciuta
- Verifica NVIDIA Container Toolkit: `docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi`
- Imposta `DEVICE=cuda` nel `.env`

### Rate Limit
- Aumenta `RATE_LIMIT_PER_HOUR` in `.env`
- Riprova tra un'ora

## 📝 Note

- I modelli vengono scaricati automaticamente al primo utilizzo (~2-4GB)
- File generati salvati in `./data/outputs/`
- Cronologia locale salvata nel browser (IndexedDB)
- Progresso aggiornato ogni ~500ms

## 📄 Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedi [LICENSE](LICENSE) per i dettagli.

**Nota**: Questo progetto utilizza Meta AudioCraft, che è soggetto alla propria licenza. 
Consulta https://github.com/facebookresearch/audiocraft per i termini di licenza di AudioCraft.

## 🤝 Contribuire

PR benvenute! Vedi [CONTRIBUTING.md](CONTRIBUTING.md) per le linee guida complete.

In breve:
1. Passare i test: `pytest`
2. Formattare codice: `ruff format` (backend), `npm run format` (frontend)
3. Testare sia CPU che GPU se possibile

---

**Buona generazione audio! 🎵**

