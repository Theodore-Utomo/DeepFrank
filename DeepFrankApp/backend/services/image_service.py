"""Image processing utilities"""
import cv2
import numpy as np
from typing import List, Optional


def bytes_to_cv2_image(image_bytes: bytes) -> Optional[np.ndarray]:
    """
    Convert image bytes to OpenCV image format
    
    Args:
        image_bytes: Image file bytes
        
    Returns:
        OpenCV image (BGR format) or None if decoding fails
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image


def extract_roi(image: np.ndarray, bbox: List[int]) -> Optional[np.ndarray]:
    """
    Extract region of interest from image
    
    Args:
        image: Input image (BGR format)
        bbox: Bounding box [x1, y1, x2, y2]
        
    Returns:
        Extracted ROI or None if invalid
    """
    if image is None or len(bbox) != 4:
        return None
    
    x1, y1, x2, y2 = bbox
    
    # Ensure coordinates are within image bounds
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(image.shape[1], x2)
    y2 = min(image.shape[0], y2)
    
    if x2 <= x1 or y2 <= y1:
        return None
    
    return image[y1:y2, x1:x2]

