"""Image processing utilities"""
import cv2
import numpy as np
from typing import Optional


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



