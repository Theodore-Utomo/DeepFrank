"""Image processing service for handling image uploads and analysis"""
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from services.detection_service import DetectionService
from services.image_service import bytes_to_cv2_image
from services.image_analysis_service import ImageAnalysisService
from models.schemas import DetectionResponse, BodyPartDetection
from models.db_models import User


class ImageProcessingService:
    """Service for processing image uploads and performing analysis"""
    
    @staticmethod
    async def analyze_image_file(
        file: UploadFile,
        detector: DetectionService,
        db: AsyncSession,
        user: Optional[User] = None
    ) -> DetectionResponse:
        """
        Process uploaded image file and perform analysis
        
        This is the main business logic for image analysis.
        
        Args:
            file: Uploaded file
            detector: Detection service instance
            db: Database session
            user: Optional authenticated user
            
        Returns:
            DetectionResponse with detections, analysis, and emotion
            
        Raises:
            HTTPException: If file is invalid or processing fails
        """
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and decode image
        image_bytes = await file.read()
        image = bytes_to_cv2_image(image_bytes)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Could not decode image")
        
        # Detect body parts
        detections = detector.detect(image)
        
        # Analyze body parts and determine emotion
        analysis_result, emotion = ImageAnalysisService.analyze_body_parts(image, detections)
        
        # Format detections for response
        formatted_detections = [
            BodyPartDetection(
                class_name=d["class"],
                confidence=d["confidence"],
                bbox=d["bbox"]
            )
            for d in detections
        ]
        
        # Build response
        result = DetectionResponse(
            detections=formatted_detections,
            analysis=analysis_result,
            emotion=emotion
        )
        
        # Save to database (optional - wrapped in try/except to not fail if DB is unavailable)
        chat_session_id = None
        try:
            analysis_record, chat_session = await ImageAnalysisService.save_analysis(
                db=db,
                filename=file.filename or "unknown",
                detections=formatted_detections,
                analysis_result=analysis_result,
                user_id=user.id if user else None,
                emotion=emotion
            )
            if chat_session:
                chat_session_id = str(chat_session.id)
        except Exception as db_error:
            # Log but don't fail the request if database save fails
            print(f"Warning: Failed to save to database: {db_error}")
        
        # Add chat session ID to response
        result.chat_session_id = chat_session_id
        
        return result

