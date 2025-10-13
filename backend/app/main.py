"""FastAPI main application."""
import os
import yaml
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.database import engine, Base, get_db
from app.routers import users, seats, signals, tables, messages
from app.routers.ws import manager

load_dotenv()

Base.metadata.create_all(bind=engine)

# Load config.yaml
config_path = Path(__file__).parent.parent.parent / "config.yaml"
config = {}
if config_path.exists():
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

app = FastAPI(title="NudgeeQ API", version="1.0.0")

# Allow common local origins by default
origins_env = os.getenv("CORS_ORIGINS")
if origins_env:
    origins = origins_env.split(",")
else:
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(seats.router)
app.include_router(signals.router)
app.include_router(tables.router)
app.include_router(messages.router)

# Include admin router only if test mode is enabled
if config.get('test', {}).get('enabled', False):
    from app.routers import admin
    app.include_router(admin.router)
    print("⚠️  Admin routes enabled (test mode)")
else:
    print("✓ Admin routes disabled (production mode)")


@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "NudgeeQ API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(user_id, websocket)
    try:
        while True:
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)

