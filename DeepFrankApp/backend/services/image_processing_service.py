"""Image processing service for handling image uploads and analysis"""
from typing import Optional
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from services.image_service import bytes_to_cv2_image
from services.image_analysis_service import ImageAnalysisService
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
        
        # Analyze using Claude
        try:
            analysis_text = await ImageAnalysisService.analyze_image_with_claude(image_bytes)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error analyzing image with Ollama: {str(e)}"
            )
        
        # Save to database and create chat session (optional - wrapped in try/except to not fail if DB is unavailable)
        chat_session_id = None
        try:
            if db:
                analysis_record, chat_session = await ImageAnalysisService.save_analysis(
                    db=db,
                    filename=file.filename or "unknown",
                    analysis_text=analysis_text,
                    user_id=user.id if user else None
                )
                if chat_session:
                    chat_session_id = str(chat_session.id)
        except Exception as db_error:
            # Log but don't fail the request if database save fails
            print(f"Warning: Failed to save to database: {db_error}")
        
        # Build response
        return ImageAnalysisResponse(
            analysis_text=analysis_text,
            chat_session_id=chat_session_id
        )

