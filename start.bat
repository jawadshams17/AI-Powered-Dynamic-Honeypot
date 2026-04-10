@echo off
title AI HONEYPOT CONTROLLER - AUTO-DEPLOY
setlocal enabledelayedexpansion

echo ===========================================
echo   AI HONEYPOT CONSOLE - AUTO-INITIALIZING
echo ===========================================
echo.
cd /d %~dp0

:: 1. Automated Environment Setup
if not exist "venv\" (
    echo [+] Creating Virtual Environment...
    python -m venv venv >nul
)

:: 2. Resilient Dependency Sync
echo [+] Synchronizing Dependencies...
.\venv\Scripts\pip install -r requirements.txt -q --no-warn-script-location
if !errorlevel! neq 0 (
    echo [!] Network sync failed, checking local core packages...
    .\venv\Scripts\python.exe -c "import pandas, xgboost, flask; print('Core OK')" >nul 2>&1
)

:: 3. Verification & Mock Data
echo [+] Verifying System Integrity...
if not exist "configs\config.json" (
    copy configs\config.json.template configs\config.json >nul
)
.\venv\Scripts\python.exe scripts\mock_data_generator.py >nul

:: 4. Zero-Click Web Dashboard Launch (Flask)
echo [+] Launching Web Dashboard (localhost:5000)...
start /b "AI_WEB_DASHBOARD" .\venv\Scripts\python.exe scripts\web_dashboard.py
timeout /t 2 >nul
start http://localhost:5000

:: 5. Zero-Click Console Dashboard (TUI)
echo [+] Launching Management Console...
start "AI_MANAGEMENT_TUI" .\venv\Scripts\python.exe scripts\manage_system.py

:: 6. Silent Daemon Launch
start /b "AI_THREAT_ENGINE" .\venv\Scripts\python.exe scripts\threat_engine.py

echo.
echo ===========================================
echo   SYSTEM ACTIVE - BROWSER OPENED
echo ===========================================
echo.
timeout /t 5 >nul
exit
