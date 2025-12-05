# Backend AudioCraft API

API FastAPI per la generazione audio con Meta AudioCraft.

## Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Esecuzione

```bash
# Sviluppo
uvicorn app:app --reload

# Produzione
uvicorn app:app --host 0.0.0.0 --port 8000
```

## Testing

```bash
pytest -v
pytest tests/test_generate_smoke.py -v
```

## Struttura

- `app.py`: Applicazione FastAPI principale
- `api/`: Endpoints REST
- `core/`: Logica core (jobs, rate limiting, settings)
- `ml/`: Modelli ML e generazione audio
- `tests/`: Test suite

