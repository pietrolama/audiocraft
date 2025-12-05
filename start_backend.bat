@echo off
chcp 65001 >nul
echo ========================================
echo   AudioCraft Backend (senza Docker)
echo ========================================
echo.

REM Verifica che Python sia installato
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRORE] Python non trovato!
    echo Per favore installa Python 3.11+ da: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python trovato
echo.

REM Vai alla directory backend
cd backend

REM Verifica che le dipendenze siano installate
echo [INFO] Verifica dipendenze...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installazione dipendenze...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERRORE] Installazione dipendenze fallita!
        pause
        exit /b 1
    )
)

REM Crea directory output se non esiste
if not exist "..\data\outputs" (
    echo [INFO] Creazione directory output...
    mkdir "..\data\outputs"
)

echo.
echo [INFO] Avvio server backend...
echo [INFO] Server disponibile su: http://localhost:8000
echo [INFO] API Docs disponibili su: http://localhost:8000/docs
echo.
echo Premi CTRL+C per fermare il server
echo.

REM Avvia il server
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

pause

