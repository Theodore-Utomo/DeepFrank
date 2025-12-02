"""Image analysis service for database operations"""
import json
import base64
import numpy as np
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from anthropic import Anthropic
from core.config import ANTHROPIC_API_KEY, CLAUDE_MODEL, CLAUDE_TEMPERATURE, IMAGE_ANALYSIS_SYSTEM_PROMPT
from models.db_models import ImageAnalysis, ChatSession
from models.schemas import BodyPartDetection, AnalysisResult, ImageAnalysisHistoryItem, UserAnalysesResponse
from services.chat_service import ChatService


# Initialize Claude client for image analysis
claude_client = Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None


class ImageAnalysisService:
    """Service for all image analysis operations (business logic and database)"""
    
    @staticmethod
    async def analyze_image_with_claude(
        image_bytes: bytes
    ) -> str:
        """
        Analyze cat image using Claude vision API
        
        Args:
            image_bytes: Image file bytes
            
        Returns:
            Text analysis of the cat image
        """
        if not claude_client:
            raise Exception("ANTHROPIC_API_KEY not set. Please set the ANTHROPIC_API_KEY environment variable.")
        
        # Convert image to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Determine image media type (assume JPEG, but could detect from bytes)
        # For simplicity, we'll use image/jpeg. Could be enhanced to detect actual format
        media_type = "image/jpeg"
        
        try:
            # Call Claude API with vision
            message = claude_client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=1024,
                temperature=CLAUDE_TEMPERATURE,
                system=IMAGE_ANALYSIS_SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": "Please analyze this cat image and provide the body language analysis. I think my cat is sick and I want to know if it is."
                            }
                        ]
                    }
                ]
            )
            
            # Extract text from response
            response_text = message.content[0].text
            return response_text
            
        except Exception as e:
            raise Exception(f"Failed to get Claude response: {str(e)}")
    
    # Keep old method name for backward compatibility
    @staticmethod
    async def analyze_image_with_ollama(image_bytes: bytes) -> str:
        """Deprecated: Use analyze_image_with_claude instead"""
        return await ImageAnalysisService.analyze_image_with_claude(image_bytes)
    
    @staticmethod
    async def save_analysis(
        db: AsyncSession,
        filename: str,
        analysis_text: str,
        user_id: Optional[UUID] = None
    ) -> Tuple[ImageAnalysis, Optional[ChatSession]]:
        """
        Save image analysis to database
        
        Args:
            db: Database session
            filename: Original filename
            analysis_text: Text analysis from Ollama
            user_id: Optional user ID to link the analysis
            
        Returns:
            Tuple of (Saved ImageAnalysis, ChatSession if created)
        """
        # Log user information for debugging
        if user_id:
            print(f"ImageAnalysisService: Saving analysis with user_id: {user_id}")
        else:
            print("ImageAnalysisService: Saving analysis without user_id (user not authenticated)")
        
        # Create chat session first if user is authenticated (so we can link it)
        chat_session = None
        if user_id:
            chat_session = await ChatService.create_session(
                user_id=user_id,
                db=db
            )
        
        analysis_record = ImageAnalysis(
            filename=filename,
            detections=None,  # No longer using detections
            analysis_result=analysis_text,  # Store plain text
            emotion=None,  # No longer extracting emotion separately
            user_id=user_id,
            chat_session_id=chat_session.id if chat_session else None
        )
        db.add(analysis_record)
        await db.commit()
        await db.refresh(analysis_record)
        print(f"ImageAnalysisService: Successfully saved analysis with id: {analysis_record.id}, user_id: {analysis_record.user_id}, chat_session_id: {analysis_record.chat_session_id}")
        
        # Save analysis as first AI message in chat session
        if chat_session:
            await ChatService.save_message(
                session_id=chat_session.id,
                sender="assistant",
                content=analysis_text,
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
            
            # Parse analysis_result - can be either JSON (old format) or plain text (new format)
            analysis_result = None
            if analysis.analysis_result:
                try:
                    # Try to parse as JSON first (for backward compatibility with old records)
                    if isinstance(analysis.analysis_result, str):
                        try:
                            analysis_data = json.loads(analysis.analysis_result)
                            analysis_result = AnalysisResult(**analysis_data)
                        except json.JSONDecodeError:
                            # If it's not JSON, it's plain text (new format)
                            # For backward compatibility, we'll set it to None since AnalysisResult expects structured data
                            analysis_result = None
                    else:
                        analysis_data = analysis.analysis_result
                        analysis_result = AnalysisResult(**analysis_data)
                except (json.JSONDecodeError, Exception) as e:
                    print(f"Error parsing analysis_result: {e}")
            
            # Get emotion from database (now stored separately)
            emotion = analysis.emotion
            
            # Get chat_session_id if it exists
            chat_session_id = str(analysis.chat_session_id) if analysis.chat_session_id else None
            
            formatted_analyses.append(
                ImageAnalysisHistoryItem(
                    id=str(analysis.id),
                    filename=analysis.filename,
                    detections=detections,
                    analysis=analysis_result,
                    emotion=emotion,
                    chat_session_id=chat_session_id,
                    created_at=analysis.created_at.isoformat() if analysis.created_at else ""
                )
            )
        
        return UserAnalysesResponse(
            analyses=formatted_analyses,
            total=total
        )

