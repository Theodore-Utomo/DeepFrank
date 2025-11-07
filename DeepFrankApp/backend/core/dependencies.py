"""Shared dependencies for FastAPI routes"""
from fastapi import HTTPException
from services.detection_service import DetectionService
from core.config import MODEL_PATH, MODEL_CONF_THRESHOLD, MODEL_IOU_THRESHOLD

# Global detector instance (lazy loaded)
_detector_service: DetectionService = None


def get_detector_service() -> DetectionService:
    """
    Get or initialize the detection service
    
    Returns:
        DetectionService instance
        
    Raises:
        HTTPException: If model fails to load
    """
    global _detector_service
    
    if _detector_service is None:
        try:
            _detector_service = DetectionService(
                model_path=str(MODEL_PATH),
                conf_threshold=MODEL_CONF_THRESHOLD,
                iou_threshold=MODEL_IOU_THRESHOLD
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load model: {str(e)}. Make sure cat_model.onnx exists in the backend directory."
            )
    
    return _detector_service

