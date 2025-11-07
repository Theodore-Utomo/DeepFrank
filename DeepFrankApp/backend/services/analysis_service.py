"""Analysis service for cat body parts and emotional state"""
import numpy as np
from typing import Tuple, Optional
from body_part_analysis import EyeAnalyzer, MouthAnalyzer, TailAnalyzer, CatEmotionAnalyzer
from services.image_service import extract_roi
from models.schemas import AnalysisResult


class AnalysisService:
    """Service for analyzing cat body parts and determining emotional state"""
    
    @staticmethod
    def analyze_body_parts(
        image: np.ndarray,
        detections: list
    ) -> Tuple[AnalysisResult, Optional[str]]:
        """
        Analyze detected body parts and determine emotional state
        
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

