"""Pydantic models for API requests and responses"""
from re import L
from pydantic import BaseModel
from typing import Optional, List


class BodyPartDetection(BaseModel):
    """Body part detection result"""
    class_name: str
    confidence: float
    bbox: List[int]


class AnalysisResult(BaseModel):
    """Body part analysis result"""
    eye_state: Optional[str] = None
    mouth_state: Optional[str] = None
    tail_position: Optional[str] = None
    tail_angle: Optional[float] = None


class EmotionResult(BaseModel):
    """Emotion analysis result"""
    emotion: str
    confidence: float
    analysis: AnalysisResult


class DetectionResponse(BaseModel):
    """Response model for detection endpoints"""
    detections: List[BodyPartDetection]
    analysis: Optional[AnalysisResult] = None
    emotion: Optional[str] = None
    chat_session_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: Optional[str] = None


class BreedsResponse(BaseModel):
    """Breeds endpoint response"""
    breeds: List[dict]
    message: Optional[str] = None


class MagicLinkRequest(BaseModel):
    """Request model for sending magic link"""
    email: str


class MagicLinkAuthenticateRequest(BaseModel):
    """Request model for authenticating magic link"""
    token: str


class UserResponse(BaseModel):
    """User information response"""
    id: str
    email: str
    stytch_user_id: str
    created_at: Optional[str] = None


class AuthResponse(BaseModel):
    """Authentication response"""
    session_token: str
    user: UserResponse


class SessionResponse(BaseModel):
    """Current session response"""
    user: UserResponse
    session_id: Optional[str] = None
    expires_at: Optional[str] = None


class MagicLinkSendResponse(BaseModel):
    """Magic link send response"""
    status: str
    message: str
    email_id: Optional[str] = None


class LogoutResponse(BaseModel):
    """Logout response"""
    status: str
    message: str


class ImageAnalysisHistoryItem(BaseModel):
    """Single image analysis history item"""
    id: str
    filename: str
    detections: List[BodyPartDetection]
    analysis: Optional[AnalysisResult] = None
    emotion: Optional[str] = None
    chat_session_id: Optional[str] = None
    created_at: str


class UserAnalysesResponse(BaseModel):
    """Response for user's image analyses history"""
    analyses: List[ImageAnalysisHistoryItem]
    total: int

class ChatSessionResponse(BaseModel):
    """Chat session response"""
    id: str
    user_id: str
    created_at: str
    updated_at: str

class ChatMessageRequest(BaseModel):
    """Chat message request"""
    session_id: str
    content: str

class ChatMessageResponse(BaseModel):
    """Chat message response"""
    id: str
    session_id: str
    sender: str
    content: str
    created_at: str
    updated_at: str


class ImageAnalysisResponse(BaseModel):
    """Response model for image analysis endpoint"""
    analysis_text: str
    chat_session_id: Optional[str] = None