"""Detection routes for cat body parts"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from models.schemas import DetectionResponse, BodyPartDetection
from services.detection_service import DetectionService
from services.image_service import bytes_to_cv2_image
from core.dependencies import get_detector_service

router = APIRouter()


@router.post("/detect-body-parts", response_model=DetectionResponse)
async def detect_body_parts(
    file: UploadFile = File(...),
    detector: DetectionService = Depends(get_detector_service)
):
    """
    Detect cat body parts in an image without full emotional analysis
    
    Returns only the detected body parts with their bounding boxes and confidence scores.
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read and decode image
        image_bytes = await file.read()
        image = bytes_to_cv2_image(image_bytes)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Could not decode image")
        
        # Detect body parts
        detections = detector.detect(image)
        
        # Format detections for response
        formatted_detections = [
            BodyPartDetection(
                class_name=d["class"],
                confidence=d["confidence"],
                bbox=d["bbox"]
            )
            for d in detections
        ]
        
        return DetectionResponse(
            detections=formatted_detections,
            analysis=None,
            emotion=None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

