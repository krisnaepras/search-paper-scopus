@echo off
REM Setup script for Scopus Search API (Windows)

echo ================================================================
echo      Scopus Search API - Setup Script
echo ================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Python found: %PYTHON_VERSION%
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo Failed to install dependencies
    exit /b 1
)

echo Dependencies installed successfully
echo.

REM Setup .env file if it doesn't exist
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo .env file created
    echo Please edit .env and add your SCOPUS_API_KEY
) else (
    echo .env file already exists
)

echo.
echo ================================================================
echo      Setup Complete!
echo ================================================================
echo.
echo Next steps:
echo    1. Edit .env and add your SCOPUS_API_KEY
echo    2. Run: python run.py
echo    3. Open: http://localhost:8000
echo.
echo Documentation:
echo    - README_NEW.md   - Full documentation
echo    - MIGRATION.md    - Migration guide
echo    - ARCHITECTURE.txt - Architecture overview
echo.
pause
