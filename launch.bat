@echo off
REM Axiom Browser Launch Script for Windows
REM This script sets up and launches the Axiom Browser

echo ==========================================
echo   Axiom Browser - Setup and Launch
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo [INFO] Python found
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created
) else (
    echo [INFO] Virtual environment already exists
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo [INFO] Installing dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    pip install PyQt5 PyQtWebEngine httpx ollama requests beautifulsoup4 lxml
)

if errorlevel 1 (
    echo [WARNING] Some packages may have failed to install
)

REM Check Ollama
echo.
echo [INFO] Checking Ollama...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Ollama not found
    echo Please install from: https://ollama.ai/download
    set /p continue="Continue without Ollama? (y/n): "
    if /i not "%continue%"=="y" exit /b 0
) else (
    echo [SUCCESS] Ollama found
    
    REM Start Ollama
    echo [INFO] Starting Ollama service...
    start /B ollama serve
    
    REM Wait a bit
    timeout /t 3 /nobreak >nul
    
    REM List models
    echo [INFO] Fetching available models...
    ollama list
)

REM Launch browser
echo.
echo [INFO] Launching Axiom Browser...
python web-browser.py

pause

