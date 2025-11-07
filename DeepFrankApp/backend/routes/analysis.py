"""Analysis routes for cat emotional state"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from models.schemas import DetectionResponse, BodyPartDetection
from services.detection_service import DetectionService
from services.analysis_service import AnalysisService
from services.image_service import bytes_to_cv2_image
from core.dependencies import get_detector_service

router = APIRouter()


@router.post("/analyze-image", response_model=DetectionResponse)
async def analyze_image(
    file: UploadFile = File(...),
    detector: DetectionService = Depends(get_detector_service)
):
    """
    Analyze a cat image to detect body parts and determine emotional state
    
    Upload an image file and get:
    - Detected body parts (eyes, mouth, tail)
    - Analysis of each body part
    - Overall emotional state
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
        
        # Analyze body parts and determine emotion
        analysis_result, emotion = AnalysisService.analyze_body_parts(image, detections)
        
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
            analysis=analysis_result,
            emotion=emotion
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

