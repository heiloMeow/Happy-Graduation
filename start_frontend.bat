@echo off
echo Starting Vue frontend...

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if dependencies are installed
if not exist "frontend\node_modules" (
    echo Installing dependencies...
    cd frontend
    npm install
    cd ..
)

REM Start the development server
cd frontend
npm run dev

