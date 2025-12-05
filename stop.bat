@echo off
chcp 65001 >nul
echo ========================================
echo   AudioCraft - Stop Servizi
echo ========================================
echo.

echo Fermo tutti i servizi...
docker compose --profile cpu --profile gpu down

echo.
echo Servizi fermati.
echo.
pause

