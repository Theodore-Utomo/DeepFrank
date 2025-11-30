"""
DeepFrank API - Main Application Entry Point
Production-ready FastAPI application for cat emotional analysis
"""
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import (
    APP_NAME,
    APP_VERSION,
    APP_DESCRIPTION,
    API_V1_PREFIX,
    ALLOWED_ORIGINS
)
from core.database import init_db
from models import db_models  # Import models to register them with Base
from routes import health, detection, analysis, breeds, auth, profile, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    # Note: Database migrations should be run separately using Alembic:
    # docker exec deepfrank-api alembic upgrade head
    try:
        await init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")
        print("The application will continue, but database features may not work.")
    yield
    # Shutdown: Clean up if needed
    pass


# Initialize FastAPI application
app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix=API_V1_PREFIX, tags=["Authentication"])
app.include_router(detection.router, prefix=API_V1_PREFIX, tags=["Detection"])
app.include_router(analysis.router, prefix=API_V1_PREFIX, tags=["Analysis"])
app.include_router(breeds.router, prefix=API_V1_PREFIX, tags=["Breeds"])
app.include_router(profile.router, prefix=API_V1_PREFIX, tags=["Profile"])
app.include_router(chat.router, prefix=API_V1_PREFIX, tags=["Chat"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Set to False in production
    )
