"""Pydantic models for API requests and responses"""
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


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: Optional[str] = None


class BreedsResponse(BaseModel):
    """Breeds endpoint response"""
    breeds: List[dict]
    message: Optional[str] = None

