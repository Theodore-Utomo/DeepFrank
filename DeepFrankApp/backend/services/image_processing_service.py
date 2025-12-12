"""Image processing service for handling image uploads and analysis"""
from typing import Optional
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from services.image_service import bytes_to_cv2_image
from services.detection_service import get_detection_service
from models.schemas import ImageAnalysisResponse
from models.db_models import User


class ImageProcessingService:
    """Service for processing image uploads and performing analysis"""
    
    @staticmethod
    async def analyze_image_file(
        file: UploadFile,
        db: AsyncSession,
        user: Optional[User] = None
    ) -> ImageAnalysisResponse:
        """
        Process uploaded image file and perform analysis using Ollama
        
        This is the main business logic for image analysis.
        
        Args:
            file: Uploaded file
            db: Database session
            user: Optional authenticated user
            
        Returns:
            ImageAnalysisResponse with analysis text and chat session ID
            
        Raises:
            HTTPException: If file is invalid or processing fails
        """
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image bytes
        image_bytes = await file.read()
        
        # Validate image can be decoded (basic validation)
        image = bytes_to_cv2_image(image_bytes)
        if image is None:
            raise HTTPException(status_code=400, detail="Could not decode image")
        
        # Run YOLOv8 detection
        try:
            detection_service = get_detection_service()
            detections = detection_service.detect(image)
            print(f"Detection completed: {len(detections)} detections found")
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Detection error: {str(e)}")
            print(f"Traceback: {error_trace}")
            raise HTTPException(
                status_code=500,
                detail=f"Error running detection: {str(e)}"
            )
        
        return ImageAnalysisResponse(
            analysis_text=None,
            detections=detections,
            chat_session_id=None
        )

