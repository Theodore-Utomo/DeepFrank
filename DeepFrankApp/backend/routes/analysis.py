"""Analysis routes for cat emotional state"""
from typing import Optional
from fastapi import APIRouter, File, UploadFile, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.schemas import ImageAnalysisResponse
from models.db_models import User
from services.image_processing_service import ImageProcessingService
from core.dependencies import get_database, get_optional_user

router = APIRouter()


@router.post("/analyze-image", response_model=ImageAnalysisResponse)
async def analyze_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_database),
    user: Optional[User] = Depends(get_optional_user)
):
    """
    Analyze a cat image using Ollama vision model
    
    Upload an image file and get:
    - Text analysis of the cat's body language and behavior
    - Chat session ID (if user is authenticated) where the analysis is saved as the first message
    """
    return await ImageProcessingService.analyze_image_file(
        file=file,
        db=db,
        user=user
    )

