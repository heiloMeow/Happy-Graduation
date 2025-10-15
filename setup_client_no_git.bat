@echo off
title NudgeeQ - Client Setup (No Git Required)
color 0A

echo ========================================
echo   NudgeeQ - Client Computer Setup
echo   (No Git Required Version)
echo ========================================
echo.

echo IMPORTANT: Before running this script:
echo 1. Download the ZIP file from GitHub:
echo    https://github.com/heiloMeow/Happy-Graduation/tree/Yueteng_Ma
echo    Click "Code" -> "Download ZIP"
echo.
echo 2. Extract the ZIP file
echo.
echo 3. Run this script from the extracted folder
echo    (You should see "frontend" and "backend" folders here)
echo.

pause

REM Check if we're in the correct directory
if not exist "frontend" (
    echo Error: Cannot find "frontend" folder
    echo Please make sure you're running this script from the Happy-Graduation folder
    pause
    exit /b 1
)

REM Prompt for server IP
set /p SERVER_IP="Enter server IP address (e.g., 192.168.1.100): "

echo.
echo Setting up client with server: %SERVER_IP%
echo.

REM Setup frontend
echo [Step 1] Installing frontend dependencies...
cd frontend

if not exist "node_modules" (
    echo Running npm install...
    echo This may take a few minutes on first run...
    call npm install
    if errorlevel 1 (
        echo.
        echo Error: npm install failed
        echo.
        echo Please make sure Node.js is installed:
        echo Download from: https://nodejs.org/
        echo.
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
echo Trying to connect to http://%SERVER_IP%:8000/health
echo.

REM Try to test connection (curl might not be available on older Windows)
where curl >nul 2>&1
if %errorlevel% equ 0 (
    curl -s http://%SERVER_IP%:8000/health >nul 2>&1
    if errorlevel 1 (
        echo Warning: Cannot connect to server at http://%SERVER_IP%:8000
        echo Please make sure:
        echo   1. Server is running on %SERVER_IP%
        echo   2. Both computers are on the same WiFi
        echo   3. Firewall allows port 8000
        echo.
        echo You can continue anyway and try later.
    ) else (
        echo Success! Connected to server.
    )
) else (
    echo Skipping connection test (curl not available)
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Configuration:
echo   Server: http://%SERVER_IP%:8000
echo   Frontend: http://localhost:5173
echo.
echo Press any key to start frontend...
pause >nul

start "NudgeeQ Client" cmd /k "npm run dev"

cd ..
echo.
echo Frontend is starting...
echo Wait a few seconds and browser should open automatically
echo If not, visit: http://localhost:5173
echo.
timeout /t 5 >nul
start http://localhost:5173


