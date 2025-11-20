"""Image analysis service for database operations"""
import json
import numpy as np
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from body_part_analysis import EyeAnalyzer, MouthAnalyzer, TailAnalyzer, CatEmotionAnalyzer
from services.image_service import extract_roi
from models.db_models import ImageAnalysis, ChatSession
from models.schemas import BodyPartDetection, AnalysisResult, ImageAnalysisHistoryItem, UserAnalysesResponse
from services.chat_service import ChatService


class ImageAnalysisService:
    """Service for all image analysis operations (business logic and database)"""
    
    @staticmethod
    def analyze_body_parts(
        image: np.ndarray,
        detections: list
    ) -> Tuple[AnalysisResult, Optional[str]]:
        """
        Analyze detected body parts and determine emotional state
        
        This is the core business logic for analyzing cat body parts.
        
        Args:
            image: Input image (BGR format)
            detections: List of detections from DetectionService
            
        Returns:
            Tuple of (AnalysisResult, emotion)
        """
        # Organize detections by class
        eyes = [d for d in detections if d["class"] == "eye"]
        mouths = [d for d in detections if d["class"] == "mouth"]
        tails = [d for d in detections if d["class"] == "tail"]
        
        analysis_result = AnalysisResult()
        
        # Analyze eyes
        if eyes:
            eye_detection = max(eyes, key=lambda x: x["confidence"])
            eye_roi = extract_roi(image, eye_detection["bbox"])
            if eye_roi is not None:
                analysis_result.eye_state = EyeAnalyzer.analyze_eye(eye_roi)
        
        # Analyze mouth
        if mouths:
            mouth_detection = max(mouths, key=lambda x: x["confidence"])
            mouth_roi = extract_roi(image, mouth_detection["bbox"])
            if mouth_roi is not None:
                analysis_result.mouth_state = MouthAnalyzer.analyze_mouth(mouth_roi)
        
        # Analyze tail
        if tails:
            tail_detection = max(tails, key=lambda x: x["confidence"])
            tail_roi = extract_roi(image, tail_detection["bbox"])
            if tail_roi is not None:
                tail_analysis = TailAnalyzer.detect_tail(tail_roi)
                analysis_result.tail_position = tail_analysis["position"]
                analysis_result.tail_angle = tail_analysis["angle"]
        
        # Determine emotion
        emotion = None
        if analysis_result.eye_state and analysis_result.mouth_state and analysis_result.tail_position:
            emotion = CatEmotionAnalyzer.determine_emotion(
                analysis_result.eye_state,
                analysis_result.mouth_state,
                analysis_result.tail_position
            )
        
        return analysis_result, emotion
    
    @staticmethod
    async def save_analysis(
        db: AsyncSession,
        filename: str,
        detections: List[BodyPartDetection],
        analysis_result: Optional[AnalysisResult],
        user_id: Optional[UUID] = None,
        emotion: Optional[str] = None
    ) -> Tuple[ImageAnalysis, Optional[ChatSession]]:
        """
        Save image analysis to database
        
        Args:
            db: Database session
            filename: Original filename
            detections: List of detected body parts
            analysis_result: Analysis result object
            user_id: Optional user ID to link the analysis
            
        Returns:
            Saved ImageAnalysis database model
        """
        # Log user information for debugging
        if user_id:
            print(f"ImageAnalysisService: Saving analysis with user_id: {user_id}")
        else:
            print("ImageAnalysisService: Saving analysis without user_id (user not authenticated)")
        
        analysis_record = ImageAnalysis(
            filename=filename,
            detections=[d.model_dump() for d in detections],
            analysis_result=json.dumps(analysis_result.model_dump(), indent=2) if analysis_result else None,
            emotion=emotion,
            user_id=user_id
        )
        db.add(analysis_record)
        await db.commit()
        await db.refresh(analysis_record)
        print(f"ImageAnalysisService: Successfully saved analysis with id: {analysis_record.id}, user_id: {analysis_record.user_id}")
        
        # Create chat session if user is authenticated
        chat_session = None
        if user_id:
            chat_session = await ChatService.create_session(
                user_id=user_id,
                db=db
            )

        return analysis_record, chat_session
    
    @staticmethod
    async def get_analyses_by_user(
        db: AsyncSession,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0
    ) -> List[ImageAnalysis]:
        """
        Get all analyses for a specific user
        
        Args:
            db: Database session
            user_id: User UUID
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of ImageAnalysis records
        """
        result = await db.execute(
            select(ImageAnalysis)
            .where(ImageAnalysis.user_id == user_id)
            .order_by(ImageAnalysis.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_analysis_by_id(
        db: AsyncSession,
        analysis_id: UUID
    ) -> Optional[ImageAnalysis]:
        """
        Get analysis by ID
        
        Args:
            db: Database session
            analysis_id: Analysis UUID
            
        Returns:
            ImageAnalysis database model or None if not found
        """
        result = await db.execute(
            select(ImageAnalysis).where(ImageAnalysis.id == analysis_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_analyses(
        db: AsyncSession,
        limit: int = 100,
        offset: int = 0
    ) -> List[ImageAnalysis]:
        """
        Get all analyses (for admin purposes)
        
        Args:
            db: Database session
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of ImageAnalysis records
        """
        result = await db.execute(
            select(ImageAnalysis)
            .order_by(ImageAnalysis.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_user_analyses_history(
        db: AsyncSession,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0
    ) -> UserAnalysesResponse:
        """
        Get user's image analyses history with formatted response
        
        This is the main business logic for retrieving user's analysis history.
        
        Args:
            db: Database session
            user_id: User UUID
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            UserAnalysesResponse with formatted analysis history
        """
        # Get analyses from database
        analyses = await ImageAnalysisService.get_analyses_by_user(
            db, user_id, limit, offset
        )
        
        # Get total count
        count_result = await db.execute(
            select(func.count(ImageAnalysis.id))
            .where(ImageAnalysis.user_id == user_id)
        )
        total = count_result.scalar() or 0
        
        # Format analyses for response
        formatted_analyses = []
        for analysis in analyses:
            # Parse detections from JSON
            detections = []
            if analysis.detections:
                if isinstance(analysis.detections, list):
                    detections = [
                        BodyPartDetection(**det) if isinstance(det, dict) else det
                        for det in analysis.detections
                    ]
            
            # Parse analysis_result from JSON string
            analysis_result = None
            if analysis.analysis_result:
                try:
                    if isinstance(analysis.analysis_result, str):
                        analysis_data = json.loads(analysis.analysis_result)
                    else:
                        analysis_data = analysis.analysis_result
                    analysis_result = AnalysisResult(**analysis_data)
                except (json.JSONDecodeError, Exception) as e:
                    print(f"Error parsing analysis_result: {e}")
            
            # Get emotion from database (now stored separately)
            emotion = analysis.emotion
            
            formatted_analyses.append(
                ImageAnalysisHistoryItem(
                    id=str(analysis.id),
                    filename=analysis.filename,
                    detections=detections,
                    analysis=analysis_result,
                    emotion=emotion,
                    created_at=analysis.created_at.isoformat() if analysis.created_at else ""
                )
            )
        
        return UserAnalysesResponse(
            analyses=formatted_analyses,
            total=total
        )

