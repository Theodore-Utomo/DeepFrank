"""Chat routes for user interactions"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models.schemas import ChatMessageRequest, ChatMessageResponse, ChatSessionResponse
from typing import List
from models.db_models import User
from services.chat_service import ChatService
from core.dependencies import get_database, get_current_user

router = APIRouter()


@router.post("/chat/session", response_model=ChatSessionResponse)
async def create_chat_session(
    db: AsyncSession = Depends(get_database),
    user: User = Depends(get_current_user)
):
    """Create a new chat session for the authenticated user"""
    session = await ChatService.create_session(user.id, db)
    return ChatSessionResponse(
        id=str(session.id),
        user_id=str(session.user_id),
        created_at=session.created_at.isoformat() if session.created_at else "",
        updated_at=session.updated_at.isoformat() if session.updated_at else ""
    )


@router.get("/chat/session/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_database),
    user: User = Depends(get_current_user)
):
    """Get a chat session by ID (must belong to the authenticated user)"""
    session = await ChatService.get_session(session_id, db)
    
    # Verify user owns the session
    if session.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this chat session"
        )
    
    return ChatSessionResponse(
        id=str(session.id),
        user_id=str(session.user_id),
        created_at=session.created_at.isoformat() if session.created_at else "",
        updated_at=session.updated_at.isoformat() if session.updated_at else ""
    )


@router.get("/chat/session/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_chat_messages(
    session_id: UUID,
    db: AsyncSession = Depends(get_database),
    user: User = Depends(get_current_user)
):
    """Get all messages for a chat session (must belong to the authenticated user)"""
    session = await ChatService.get_session(session_id, db)
    
    # Verify user owns the session
    if session.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this chat session"
        )
    
    messages = await ChatService.get_session_messages(session_id, db)
    return [
        ChatMessageResponse(
            id=str(msg.id),
            session_id=str(msg.session_id),
            sender=msg.sender,
            content=msg.content,
            created_at=msg.created_at.isoformat() if msg.created_at else "",
            updated_at=msg.updated_at.isoformat() if msg.updated_at else ""
        )
        for msg in messages
    ]


@router.post("/chat/send-message", response_model=ChatMessageResponse)
async def send_chat_message(
    message: ChatMessageRequest,
    db: AsyncSession = Depends(get_database),
    user: User = Depends(get_current_user)
):
    """
    Send a chat message and get AI response
    
    The message will be saved to the database, and the AI will generate
    a response based on the conversation history.
    """
    return await ChatService.send_message(message, user.id, db)