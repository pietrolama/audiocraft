# Contribuire

Grazie per il tuo interesse a contribuire a questo progetto! 🎉

## Come Contribuire

### Segnalare Bug

Se trovi un bug, apri una GitHub Issue con:
- Descrizione chiara del problema
- Passi per riprodurre
- Sistema operativo e versione Docker
- Log di errore (se disponibili)

### Proporre Nuove Funzionalità

Apri una GitHub Issue con:
- Descrizione della funzionalità
- Caso d'uso
- Proposta di implementazione (opzionale)

### Pull Request

1. **Fork** il repository
2. **Crea un branch** per la tua feature (`git checkout -b feature/amazing-feature`)
3. **Fai commit** delle modifiche (`git commit -m 'Add amazing feature'`)
4. **Push** al branch (`git push origin feature/amazing-feature`)
5. **Apri una Pull Request**

### Standard di Codice

#### Backend (Python)
- Usa `ruff format` per formattare il codice
- Segui PEP 8
- Aggiungi docstring alle funzioni
- Scrivi test per nuove funzionalità

```bash
cd backend
ruff format .
pytest -v
```

#### Frontend (TypeScript/React)
- Usa `npm run format` per formattare
- Segui le convenzioni React/Next.js
- Aggiungi TypeScript types dove necessario

```bash
cd frontend
npm run format
npm run lint
```

### Testing

Prima di fare una PR, assicurati che:
- ✅ Tutti i test passano: `pytest` (backend)
- ✅ Il codice è formattato correttamente
- ✅ Non ci sono errori di linting
- ✅ Hai testato sia su CPU che GPU (se possibile)
- ✅ La documentazione è aggiornata

### Struttura del Progetto

```
audiocraft/
├── backend/          # FastAPI backend
│   ├── api/         # API routes
│   ├── core/        # Core functionality
│   └── ml/          # ML models & generation
├── frontend/         # Next.js frontend
│   └── src/
│       ├── app/     # Next.js app router
│       └── components/  # React components
└── data/            # Generated audio (gitignored)
```

### Domande?

Apri una GitHub Discussion per domande o discussioni!

---

**Grazie per il tuo contributo!** 🙏

