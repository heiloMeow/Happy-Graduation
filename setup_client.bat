@echo off
title NudgeeQ - Client Setup
color 0A

echo ========================================
echo   NudgeeQ - Client Computer Setup
echo ========================================
echo.

REM Prompt for server IP
set /p SERVER_IP="Enter server IP address (e.g., 192.168.1.100): "

echo.
echo Setting up client with server: %SERVER_IP%
echo.

REM Check if we're in the Happy-Graduation directory
if not exist "frontend" (
    echo Error: Please run this script from the Happy-Graduation directory
    echo Or clone the repository first with:
    echo   git clone -b Yueteng_Ma https://github.com/heiloMeow/Happy-Graduation.git
    pause
    exit /b 1
)

REM Setup frontend
echo [Step 1] Installing frontend dependencies...
cd frontend

if not exist "node_modules" (
    echo Running npm install...
    call npm install
    if errorlevel 1 (
        echo Error: npm install failed
        echo Please make sure Node.js is installed
        pause
        exit /b 1
    )
) else (
    echo Dependencies already installed.
)

echo.
echo [Step 2] Configuring API connection...
echo VITE_API_BASE=http://%SERVER_IP%:8000/api > .env
echo Configuration saved to .env

echo.
echo [Step 3] Testing connection to server...
curl -s http://%SERVER_IP%:8000/health >nul 2>&1
if errorlevel 1 (
    echo Warning: Cannot connect to server at http://%SERVER_IP%:8000
    echo Please make sure:
    echo   1. Server is running on %SERVER_IP%
    echo   2. Both computers are on the same WiFi
    echo   3. Firewall allows port 8000
    echo.
    echo You can continue anyway and try later.
    pause
) else (
    echo Success! Connected to server.
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Frontend will start now...
echo Visit: http://localhost:5173
echo Server: http://%SERVER_IP%:8000
echo.
echo Press any key to start frontend...
pause >nul

start "NudgeeQ Client" cmd /k "npm run dev"

cd ..
echo.
echo Frontend is starting...
timeout /t 3 >nul
start http://localhost:5173


