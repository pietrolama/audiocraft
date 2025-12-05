@echo off
chcp 65001 >nul
echo ========================================
echo   AudioCraft Text-to-Audio Generator
echo ========================================
echo.

REM Verifica che Docker sia installato
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERRORE] Docker non trovato!
    echo Per favore installa Docker Desktop da: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo [OK] Docker trovato
echo.

REM Verifica che docker-compose sia disponibile
docker compose version >nul 2>&1
if errorlevel 1 (
    docker-compose version >nul 2>&1
    if errorlevel 1 (
        echo [ERRORE] docker-compose non trovato!
        pause
        exit /b 1
    )
    set DOCKER_COMPOSE_CMD=docker-compose
) else (
    set DOCKER_COMPOSE_CMD=docker compose
)

echo [OK] docker-compose disponibile
echo.

REM Menu di selezione
echo Seleziona modalita di esecuzione:
echo.
echo   1. CPU ^(piu lento, funziona ovunque^)
echo   2. GPU ^(richiede NVIDIA GPU con CUDA^)
echo   3. Esci
echo.
set /p choice="Inserisci scelta (1-3): "

if "%choice%"=="1" goto start_cpu
if "%choice%"=="2" goto start_gpu
if "%choice%"=="3" goto end
echo Scelta non valida!
pause
goto end

:start_cpu
echo.
echo [INFO] Avvio in modalita CPU...
echo.
echo Creazione directory data se non esiste...
if not exist "data" mkdir data
if not exist "data\outputs" mkdir data\outputs

echo.
echo Avvio servizi...
if "%DOCKER_COMPOSE_CMD%"=="docker-compose" (
    docker-compose --profile cpu up --build
) else (
    docker compose --profile cpu up --build
)
goto end

:start_gpu
echo.
echo [INFO] Verifica GPU NVIDIA...
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ATTENZIONE] GPU NVIDIA non disponibile o driver non installati!
    echo.
    echo Opzioni:
    echo   1. Usa modalita CPU invece
    echo   2. Installa NVIDIA Container Toolkit e riprova
    echo.
    set /p gpu_choice="Scegli (1 per CPU, qualsiasi altro tasto per uscire): "
    if "%gpu_choice%"=="1" goto start_cpu
    goto end
)

echo [OK] GPU NVIDIA disponibile
echo.
echo Creazione directory data se non esiste...
if not exist "data" mkdir data
if not exist "data\outputs" mkdir data\outputs

echo.
echo Avvio servizi GPU...
if "%DOCKER_COMPOSE_CMD%"=="docker-compose" (
    docker-compose --profile gpu up --build
) else (
    docker compose --profile gpu up --build
)
goto end

:end
echo.
echo Script terminato.
pause
