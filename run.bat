@echo off
title Afforestation Potential Analyzer - Launcher
echo ===================================================================
echo            🌳 Afforestation Potential Analyzer Launcher 🌳
echo ===================================================================
echo.
echo [INFO] Starting the launcher script...
echo [INFO] Current Directory: %CD%
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to your system PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/
    echo Make sure to check the box "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Verify/install python dependencies
echo [INFO] Checking python dependencies from requirements.txt...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Failed to automatically verify or install some dependencies.
    echo Attempting to start the application anyway...
)
echo [SUCCESS] Dependencies checked!
echo.

:: Start Flask app in a separate background cmd window so it keeps running
echo [INFO] Launching the Flask Web Server...
start "Afforestation Analyzer Server" cmd /k "python app.py"

:: Wait a brief moment (3 seconds) for Flask to initialize
echo [INFO] Waiting for Flask server to initialize...
timeout /t 3 /nobreak >nul

:: Open browser
echo [INFO] Opening default browser to http://localhost:5000...
start http://localhost:5000

echo.
echo ===================================================================
echo [SUCCESS] The Flask server is now running!
echo [INFO] You can access the application at: http://localhost:5000
echo.
echo [INFO] Keep the other command prompt window ("Afforestation Analyzer Server") 
echo        open. To stop the server, simply close that window.
echo ===================================================================
echo.
pause
