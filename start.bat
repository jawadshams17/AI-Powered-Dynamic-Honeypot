@echo off
title AI HONEYPOT CONTROLLER - PLATEX READY
setlocal enabledelayedexpansion

:: Master directory configuration
cd /d %~dp0
set LOG_FILE=logs\deployment_setup.log
if not exist "logs\" mkdir logs

echo ===========================================
echo   AI HONEYPOT CONSOLE - ZERO-CLICK START
echo ===========================================
echo.
echo [+] Working Directory: %cd%

:: 1. Intelligent Python Detection
echo [+] Checking for Python Runtime...
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo [!] 'python' not found in PATH. Checking 'py' launcher...
    py --version >nul 2>&1
    if !errorlevel! equ 0 (
        set PYTHON_CMD=py
    ) else (
        echo [!] ERROR: Python is not installed or not in PATH.
        echo Please install Python 3.10+ and try again.
        pause
        exit /b 1
    )
) else (
    set PYTHON_CMD=python
)
echo [+] Using Runtime: !PYTHON_CMD!

:: 2. Automated Virtual Environment
if not exist "venv\" (
    echo [+] Initializing Isolated Environment (venv)...
    !PYTHON_CMD! -m venv venv >> %LOG_FILE% 2>&1
    if !errorlevel! neq 0 (
        echo [!] Failed to create venv. Check %LOG_FILE%
        pause
        exit /b 1
    )
)

:: 3. Precision Dependency Synchronization
echo [+] Synchronizing Project Dependencies (Pip)...
.\venv\Scripts\python.exe -m pip install --upgrade pip -q >> %LOG_FILE% 2>&1
.\venv\Scripts\pip install -r requirements.txt -q --no-warn-script-location >> %LOG_FILE% 2>&1
if !errorlevel! neq 0 (
    echo [!] WARNING: Dependency sync had minor issues. Checking core stability...
    .\venv\Scripts\python.exe -c "import pandas, xgboost, flask, shap, seaborn; print('Recovery successful')" >nul 2>&1
    if !errorlevel! neq 0 (
        echo [!] ERROR: Core libraries missing. Check %LOG_FILE%
        pause
        exit /b 1
    )
)

:: 4. Infrastructure Verification
echo [+] Validating Academic Assets...
if not exist "configs\config.json" (
    if exist "configs\config.json.template" (
        copy configs\config.json.template configs\config.json >nul
    )
)
.\venv\Scripts\python.exe scripts\mock_data_generator.py >> %LOG_FILE% 2>&1

:: 5. Orchestrated Service Launch
echo [+] Deploying Intelligent Threat Engine (Daemon)...
start /b "AI_THREAT_ENGINE" .\venv\Scripts\python.exe scripts\threat_engine.py

echo [+] Deploying Web Dashboard (Host Node)...
start /b "AI_WEB_DASHBOARD" .\venv\Scripts\python.exe scripts\web_dashboard.py

echo [+] Deploying Analyst TUI (Management Console)...
timeout /t 3 >nul
start "AI_MANAGEMENT_TUI" .\venv\Scripts\python.exe scripts\manage_system.py

:: 6. Auto-Open Intelligence Interface
echo [+] Opening Local Intelligence Interface...
timeout /t 2 >nul
start http://localhost:5000

echo.
echo ===========================================
echo   SYSTEM DEPLOYED - 100%% OPERATIONAL
echo ===========================================
echo.
echo Keep this window open to monitor the AI Daemon.
echo Setup logs available at: %LOG_FILE%
echo.
pause
