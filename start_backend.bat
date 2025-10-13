@echo off
echo Starting FastAPI backend...

REM Check if virtual environment exists
if not exist "backend\.venv" (
    echo Virtual environment not found. Creating one...
    cd backend
    python -m venv .venv
    echo Installing dependencies...
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    cd ..
)

REM Check if .env file exists
if not exist "backend\.env" (
    echo Creating .env file from sample...
    copy backend\env.sample backend\.env
)

REM Start server using virtual environment's python
cd backend
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

