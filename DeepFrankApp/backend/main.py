"""
DeepFrank API - Main Application Entry Point
Production-ready FastAPI application for cat emotional analysis
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import (
    APP_NAME,
    APP_VERSION,
    APP_DESCRIPTION,
    API_V1_PREFIX,
    ALLOWED_ORIGINS
)
from routes import health, detection, analysis, breeds

# Initialize FastAPI application
app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(detection.router, prefix=API_V1_PREFIX, tags=["Detection"])
app.include_router(analysis.router, prefix=API_V1_PREFIX, tags=["Analysis"])
app.include_router(breeds.router, prefix=API_V1_PREFIX, tags=["Breeds"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Set to False in production
    )
