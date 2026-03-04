@echo off
REM Leadify API Starter
REM Startet die FastAPI REST-Schnittstelle

echo ========================================
echo   Leadify REST API
echo   Starting Server...
echo ========================================
echo.

REM Prüfe ob .env existiert
if not exist .env (
    echo [ERROR] .env file nicht gefunden!
    echo Bitte erstellen Sie eine .env Datei basierend auf .env.example
    echo.
    echo Beispiel:
    echo   copy .env.example .env
    echo.
    pause
    exit /b 1
)

REM API starten
echo [OK] Starte API-Server...
echo [OK] Dokumentation wird verfügbar sein unter: http://127.0.0.1:8000/docs
echo.

python -m api.main

pause
