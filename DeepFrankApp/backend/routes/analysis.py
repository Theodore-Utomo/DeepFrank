"""Analysis routes for cat emotional state"""
from typing import Optional
from fastapi import APIRouter, File, UploadFile, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.schemas import DetectionResponse
from models.db_models import User
from services.detection_service import DetectionService
from services.image_processing_service import ImageProcessingService
from core.dependencies import get_detector_service, get_database, get_optional_user

router = APIRouter()


@router.post("/analyze-image", response_model=DetectionResponse)
async def analyze_image(
    file: UploadFile = File(...),
    detector: DetectionService = Depends(get_detector_service),
    db: AsyncSession = Depends(get_database),
    user: Optional[User] = Depends(get_optional_user)
):
    """
    Analyze a cat image to detect body parts and determine emotional state
    
    Upload an image file and get:
    - Detected body parts (eyes, mouth, tail)
    - Analysis of each body part
    - Overall emotional state
    """
    return await ImageProcessingService.analyze_image_file(
        file=file,
        detector=detector,
        db=db,
        user=user
    )

