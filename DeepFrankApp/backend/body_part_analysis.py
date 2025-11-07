"""
Body Part Analysis Modules
Based on the Cat-Emotional-Analysis repository approach
Analyzes eyes, mouth, and tail to determine cat's emotional state
"""
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
from collections import Counter
import math


class EyeAnalyzer:
    """Analyzes cat eyes to determine if they are wide open or closed"""
    
    @staticmethod
    def analyze_eye(eye_roi: np.ndarray) -> str:
        """
        Analyze a single eye region
        
        Args:
            eye_roi: Region of interest containing the eye (BGR image)
            
        Returns:
            Eye state: "wide_open", "normal", or "closed"
        """
        if eye_roi is None or eye_roi.size == 0:
            return "unknown"
        
        # Convert to grayscale
        gray = cv2.cvtColor(eye_roi, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to separate iris/pupil from whites
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Invert if needed (depends on image)
        # Typically, pupil is darker, whites are lighter
        if np.mean(gray) > 127:
            thresh = cv2.bitwise_not(thresh)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return "unknown"
        
        # Find the largest contour (likely the eye)
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Create mask for the eye region
        mask = np.zeros(gray.shape, dtype=np.uint8)
        cv2.drawContours(mask, [largest_contour], -1, 255, -1)
        
        # Calculate ratio of white (whites of eye) to black (pupil/iris)
        # In the masked region, count pixels
        masked_eye = cv2.bitwise_and(gray, mask)
        
        # Use threshold to separate whites from dark parts
        _, eye_thresh = cv2.threshold(masked_eye, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Count white pixels (eye whites) vs dark pixels (pupil/iris)
        white_pixels = np.sum(eye_thresh > 127)
        dark_pixels = np.sum(eye_thresh <= 127)
        
        if dark_pixels == 0:
            ratio = 0
        else:
            ratio = white_pixels / dark_pixels
        
        # Determine eye state based on ratio
        # Wide open eyes have more whites visible (higher ratio)
        # Closed eyes have less whites visible (lower ratio)
        if ratio > 1.5:
            return "wide_open"
        elif ratio > 0.5:
            return "normal"
        else:
            return "closed"
    
    @staticmethod
    def analyze_eyes_behavior(eye_states: List[str]) -> str:
        """
        Analyze multiple eye states (for video frames) and return most common
        
        Args:
            eye_states: List of eye states from multiple frames
            
        Returns:
            Most common eye state
        """
        if not eye_states:
            return "unknown"
        
        counter = Counter[str, int](eye_states)
        return counter.most_common(1)[0][0]


class MouthAnalyzer:
    """Analyzes cat mouth to determine if it's open or closed"""
    
    @staticmethod
    def analyze_mouth(mouth_roi: np.ndarray) -> str:
        """
        Analyze mouth region
        
        Args:
            mouth_roi: Region of interest containing the mouth (BGR image)
            
        Returns:
            Mouth state: "open" or "closed"
        """
        if mouth_roi is None or mouth_roi.size == 0:
            return "unknown"
        
        # Convert to grayscale
        gray = cv2.cvtColor(mouth_roi, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply edge detection to find mouth opening
        edges = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return "closed"
        
        # Find contours that might represent an open mouth
        # An open mouth typically has a larger, more complex contour
        large_contours = [c for c in contours if cv2.contourArea(c) > 50]
        
        if len(large_contours) > 2:  # Open mouth typically has multiple contours (upper/lower lip)
            return "open"
        
        # Check if any contour has significant area (open mouth)
        max_area = max([cv2.contourArea(c) for c in contours]) if contours else 0
        total_area = mouth_roi.shape[0] * mouth_roi.shape[1]
        
        if max_area > total_area * 0.1:  # If significant portion of ROI
            return "open"
        
        return "closed"
    
    @staticmethod
    def analyze_mouth_behavior(mouth_states: List[str]) -> str:
        """
        Analyze multiple mouth states (for video frames) and return most common
        
        Args:
            mouth_states: List of mouth states from multiple frames
            
        Returns:
            Most common mouth state
        """
        if not mouth_states:
            return "unknown"
        
        counter = Counter(mouth_states)
        return counter.most_common(1)[0][0]


class TailAnalyzer:
    """Analyzes cat tail position and movement"""
    
    @staticmethod
    def detect_tail(tail_roi: np.ndarray) -> Dict[str, float]:
        """
        Detect tail position and orientation
        
        Args:
            tail_roi: Region of interest containing the tail (BGR image)
            
        Returns:
            Dictionary with tail analysis results
        """
        if tail_roi is None or tail_roi.size == 0:
            return {"position": "unknown", "angle": 0, "width_ratio": 0, "height_ratio": 0}
        
        # Convert to grayscale
        gray = cv2.cvtColor(tail_roi, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return {"position": "unknown", "angle": 0, "width_ratio": 0, "height_ratio": 0}
        
        # Find the largest contour (the tail)
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Calculate dimensions
        width_ratio = w / tail_roi.shape[1]
        height_ratio = h / tail_roi.shape[0]
        
        # Calculate angle using minimum area rectangle
        rect = cv2.minAreaRect(largest_contour)
        angle = rect[2]
        
        # Normalize angle to 0-180 degrees
        if angle < -45:
            angle += 90
        
        # Determine tail position
        # If height is greater than width, tail is vertical (standing up or down)
        # If width is greater than height, tail is horizontal (to the side)
        if height_ratio > width_ratio:
            # Vertical tail
            if angle < 45:
                position = "up"
            else:
                position = "down"
        else:
            # Horizontal tail
            if angle < 45:
                position = "left"
            else:
                position = "right"
        
        return {
            "position": position,
            "angle": float(angle),
            "width_ratio": width_ratio,
            "height_ratio": height_ratio
        }
    
    @staticmethod
    def calculate_tail_gradient(tail_roi: np.ndarray) -> float:
        """
        Calculate tail gradient/slope
        
        Args:
            tail_roi: Region of interest containing the tail
            
        Returns:
            Gradient value
        """
        if tail_roi is None or tail_roi.size == 0:
            return 0.0
        
        gray = cv2.cvtColor(tail_roi, cv2.COLOR_BGR2GRAY)
        
        # Apply Sobel operator to detect edges and calculate gradient
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # Calculate gradient magnitude and direction
        gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
        gradient_direction = np.arctan2(sobely, sobelx)
        
        # Return average gradient direction in degrees
        avg_direction = np.mean(gradient_direction) * 180 / np.pi
        return avg_direction
    
    @staticmethod
    def analyze_tail_behavior(tail_positions: List[str]) -> str:
        """
        Analyze multiple tail positions (for video frames) and return most common
        
        Args:
            tail_positions: List of tail positions from multiple frames
            
        Returns:
            Most common tail position
        """
        if not tail_positions:
            return "unknown"
        
        counter = Counter(tail_positions)
        return counter.most_common(1)[0][0]


class CatEmotionAnalyzer:
    """Combines all body part analyses to determine cat's emotional state"""
    
    # Emotional states mapping based on body language
    EMOTION_MAPPING = {
        ("wide_open", "closed", "up"): "alert",
        ("wide_open", "closed", "down"): "fearful",
        ("normal", "closed", "up"): "content",
        ("normal", "open", "up"): "playful",
        ("closed", "closed", "down"): "sleepy",
        ("wide_open", "open", "up"): "excited",
        ("wide_open", "open", "down"): "aggressive",
    }
    
    @staticmethod
    def determine_emotion(eye_state: str, mouth_state: str, tail_position: str) -> str:
        """
        Determine cat's emotional state based on body parts
        
        Args:
            eye_state: State of eyes (wide_open, normal, closed)
            mouth_state: State of mouth (open, closed)
            tail_position: Position of tail (up, down, left, right)
            
        Returns:
            Emotional state description
        """
        # Try exact match first
        key = (eye_state, mouth_state, tail_position)
        if key in CatEmotionAnalyzer.EMOTION_MAPPING:
            return CatEmotionAnalyzer.EMOTION_MAPPING[key]
        
        # Try partial matches
        for (e, m, t), emotion in CatEmotionAnalyzer.EMOTION_MAPPING.items():
            if eye_state == e and mouth_state == m:
                return emotion
        
        # Default based on individual parts
        if eye_state == "wide_open" and mouth_state == "open":
            return "excited"
        elif eye_state == "closed":
            return "sleepy"
        elif tail_position == "down":
            return "submissive"
        else:
            return "neutral"

