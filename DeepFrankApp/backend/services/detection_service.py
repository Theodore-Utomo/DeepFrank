"""YOLOv8 detection service for cat body part detection"""
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple
import onnxruntime as ort
from core.config import BASE_DIR
from models.schemas import BodyPartDetection


class DetectionService:
    """Service for running YOLOv8 detection on cat images"""
    
    CLASS_NAMES = ["tail", "eye", "mouth"]
    
    MODEL_INPUT_SIZE = 640
    CONFIDENCE_THRESHOLD = 0.25
    NMS_THRESHOLD = 0.45
    
    def __init__(self):
        """Initialize the detection service and load the ONNX model"""
        model_path = BASE_DIR / "cat_model.onnx"
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found at {model_path}")
        
        self.session = ort.InferenceSession(
            str(model_path),
            providers=['CPUExecutionProvider']
        )
        
        self.input_name = self.session.get_inputs()[0].name
        input_shape = self.session.get_inputs()[0].shape
        self.input_height = input_shape[2] if len(input_shape) > 2 else self.MODEL_INPUT_SIZE
        self.input_width = input_shape[3] if len(input_shape) > 3 else self.MODEL_INPUT_SIZE
    
    def preprocess_image(self, image: np.ndarray) -> Tuple[np.ndarray, float, float]:
        """
        Preprocess image for YOLOv8 model
        
        Args:
            image: OpenCV image (BGR format)
            
        Returns:
            Tuple of (preprocessed image, x_scale, y_scale) for coordinate scaling
        """
        original_height, original_width = image.shape[:2]
        
        scale = min(self.input_width / original_width, self.input_height / original_height)
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
        
        padded = np.full((self.input_height, self.input_width, 3), 114, dtype=np.uint8)
        padded[:new_height, :new_width] = resized
        
        rgb_image = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB)
        normalized = rgb_image.astype(np.float32) / 255.0
        transposed = np.transpose(normalized, (2, 0, 1))
        batched = np.expand_dims(transposed, axis=0)
        
        x_scale = original_width / new_width
        y_scale = original_height / new_height
        
        return batched, x_scale, y_scale
    
    def postprocess_output(
        self,
        output: np.ndarray,
        x_scale: float,
        y_scale: float
    ) -> List[BodyPartDetection]:
        """
        Post-process YOLOv8 model output
        
        Args:
            output: Model output array [batch, features, detections] or [batch, detections, features]
                    Format: [x_center, y_center, width, height, objectness, class0, class1, class2]
                    Coordinates are in PIXEL values relative to model input size (640x640)
            x_scale: Scale factor for x coordinates (original_width / resized_width)
            y_scale: Scale factor for y coordinates (original_height / resized_height)
            
        Returns:
            List of BodyPartDetection objects
        """
        detections = []
        
        if len(output.shape) == 3:
            output = output[0]
        
        if output.shape[0] < output.shape[1]:
            output = output.transpose(1, 0)
        
        max_confidence_found = 0.0
        boxes_above_threshold = 0
        
        for detection in output:
            x_center = float(detection[0])
            y_center = float(detection[1])
            width = float(detection[2])
            height = float(detection[3])
            objectness = float(detection[4])
            
            if output.shape[1] > 5:
                class_probs = detection[5:]
                class_id = int(np.argmax(class_probs))
                class_conf = float(class_probs[class_id])
                conf = class_conf
            else:
                conf = objectness
                class_id = 0
            
            max_confidence_found = max(max_confidence_found, conf)
            if conf >= self.CONFIDENCE_THRESHOLD:
                boxes_above_threshold += 1
            
            if conf < self.CONFIDENCE_THRESHOLD:
                continue
            
            x1 = x_center - width / 2
            y1 = y_center - height / 2
            x2 = x_center + width / 2
            y2 = y_center + height / 2
            
            x1 = int(x1 * x_scale)
            y1 = int(y1 * y_scale)
            x2 = int(x2 * x_scale)
            y2 = int(y2 * y_scale)
            
            if x2 <= x1 or y2 <= y1:
                continue
            
            if 0 <= class_id < len(self.CLASS_NAMES):
                class_name = self.CLASS_NAMES[class_id]
            else:
                continue
            
            detections.append(BodyPartDetection(
                class_name=class_name,
                confidence=conf,
                bbox=[x1, y1, x2, y2]
            ))
        
        print(f"Max confidence found: {max_confidence_found:.4f}, Boxes above threshold ({self.CONFIDENCE_THRESHOLD}): {boxes_above_threshold}, Detections before NMS: {len(detections)}")
        
        detections = self._apply_nms(detections)
        
        print(f"Detections after NMS: {len(detections)}")
        
        return detections
    
    def _apply_nms(self, detections: List[BodyPartDetection]) -> List[BodyPartDetection]:
        """
        Apply Non-Maximum Suppression to remove overlapping detections
        
        Args:
            detections: List of detections
            
        Returns:
            Filtered list of detections after NMS
        """
        if not detections:
            return []
        
        boxes = np.array([[d.bbox[0], d.bbox[1], d.bbox[2], d.bbox[3]] for d in detections])
        scores = np.array([d.confidence for d in detections])
        class_ids = np.array([self.CLASS_NAMES.index(d.class_name) for d in detections])
        
        indices = cv2.dnn.NMSBoxes(
            boxes.tolist(),
            scores.tolist(),
            self.CONFIDENCE_THRESHOLD,
            self.NMS_THRESHOLD
        )
        
        if len(indices) == 0:
            return []
        
        if isinstance(indices, np.ndarray):
            indices = indices.flatten()
        
        return [detections[i] for i in indices]
    
    def detect(self, image: np.ndarray) -> List[BodyPartDetection]:
        """
        Run detection on an image
        
        Args:
            image: OpenCV image (BGR format)
            
        Returns:
            List of BodyPartDetection objects
        """
        preprocessed, x_scale, y_scale = self.preprocess_image(image)
        outputs = self.session.run(None, {self.input_name: preprocessed})
        output = outputs[0] if len(outputs) > 0 else outputs
        
        print(f"Detection output shape: {output.shape}, dtype: {output.dtype}")
        
        detections = self.postprocess_output(output, x_scale, y_scale)
        
        print(f"Found {len(detections)} detections")
        
        return detections


_detection_service = None


def get_detection_service() -> DetectionService:
    global _detection_service
    if _detection_service is None:
        _detection_service = DetectionService()
    return _detection_service

