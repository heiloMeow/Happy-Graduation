@echo off
title NudgeeQ - LAN Mode Setup
color 0A

echo ========================================
echo   NudgeeQ - Local Area Network Setup
echo ========================================
echo.

REM Get local IP address
echo [Step 1] Detecting your IP address...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do set IP=%%a
set IP=%IP:~1%
echo Your IP address: %IP%
echo.

REM Start backend
echo [Step 2] Starting backend server...
if not exist "backend\.venv" (
    echo Virtual environment not found. Creating one...
    cd backend
    python -m venv .venv
    echo Installing dependencies...
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    cd ..
)

if not exist "backend\.env" (
    echo Creating .env file from sample...
    copy backend\env.sample backend\.env
)

echo Backend starting on http://%IP%:8000
start "NudgeeQ Backend" cmd /k "cd backend && .venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3 >nul

REM Configure frontend
echo.
echo [Step 3] Configuring frontend...
cd frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)

REM Create .env file
echo VITE_API_BASE=http://localhost:8000/api > .env
echo Frontend configured for local access
echo.

REM Start frontend
echo [Step 4] Starting frontend...
echo Frontend will be available at http://localhost:5173
echo.
start "NudgeeQ Frontend" cmd /k "npm run dev"

cd ..

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo This computer (Table Server):
echo   - Frontend: http://localhost:5173
echo   - Backend:  http://localhost:8000
echo.
echo Other computers on same WiFi:
echo   1. Create file: frontend\.env
echo   2. Add line: VITE_API_BASE=http://%IP%:8000/api
echo   3. Run: cd frontend ^&^& npm run dev
echo   4. Visit: http://localhost:5173
echo.
echo Press any key to open browser...
pause >nul
start http://localhost:5173


