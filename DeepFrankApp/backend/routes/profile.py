"""Profile routes for user data"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models.schemas import UserAnalysesResponse
from models.db_models import User
from services.image_analysis_service import ImageAnalysisService
from core.dependencies import get_database, get_current_user

router = APIRouter()


@router.get("/profile/analyses", response_model=UserAnalysesResponse)
async def get_user_analyses(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database),
    limit: int = 100,
    offset: int = 0
):
    """
    Get current user's image analyses history
    
    Query parameters:
    - limit: Maximum number of results (default: 100)
    - offset: Number of results to skip (default: 0)
    """
    try:
        return await ImageAnalysisService.get_user_analyses_history(
            db=db,
            user_id=user.id,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve user analyses: {str(e)}"
        )

