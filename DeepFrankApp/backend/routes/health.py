"""Health check routes"""
from fastapi import APIRouter
from models.schemas import HealthResponse

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def root():
    """Root health check endpoint"""
    return {"status": "healthy", "service": "DeepFrank API"}


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "DeepFrank API"}

