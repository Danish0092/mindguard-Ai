from fastapi import FastAPI
from sqlalchemy import text
import app.models

from app.db.database import engine
from app.api.auth import router as auth_router
from app.api.conversations import router as conversations_router
from app.api.messages import router as messages_router
app = FastAPI(
    title="MindGuard AI API",
    description="Backend API for MindGuard AI",
    version="1.0.0",
)
app.include_router(auth_router)
app.include_router(conversations_router)
app.include_router(messages_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "MindGuard AI API"
    }


@app.get("/health/database")
def database_health_check():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected",
            "result": result.scalar(),
        }
