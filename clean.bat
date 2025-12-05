@echo off
chcp 65001 >nul
echo ========================================
echo   AudioCraft - Pulizia
echo ========================================
echo.

echo Questo script rimuoverà:
echo - Container Docker
echo - Immagini Docker del progetto
echo - Volume dati (audio generati)
echo.
set /p confirm="Sei sicuro? (S/N): "

if /i not "%confirm%"=="S" (
    echo Operazione annullata.
    pause
    exit /b 0
)

echo.
echo Fermo servizi...
docker compose --profile cpu --profile gpu down -v

echo.
echo Rimuovo immagini...
docker rmi audiocraft-backend audiocraft-frontend 2>nul
docker rmi audiocraft-backend-gpu 2>nul

echo.
echo Rimuovo cache Docker (opzionale)...
set /p clean_cache="Rimuovere anche cache Docker? (S/N): "
if /i "%clean_cache%"=="S" (
    docker system prune -f
)

echo.
echo Pulizia completata!
echo.
echo NOTA: I file in ./data/outputs sono stati preservati.
echo       Per rimuoverli completamente, elimina manualmente la cartella ./data
echo.
pause

