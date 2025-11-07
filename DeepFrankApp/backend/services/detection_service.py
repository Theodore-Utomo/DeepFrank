"""Detection service for cat body parts using ONNX model"""
import os
import cv2
import numpy as np
import onnxruntime as ort
from typing import List, Tuple, Dict


class DetectionService:
    """Service for detecting cat body parts using ONNX model"""
    
    def __init__(self, model_path: str, conf_threshold: float = 0.25, iou_threshold: float = 0.45):
        """
        Initialize the detection service
        
        Args:
            model_path: Path to the ONNX model file
            conf_threshold: Confidence threshold for detections
            iou_threshold: IoU threshold for NMS
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Initialize ONNX Runtime session
        self.session = ort.InferenceSession(
            model_path,
            providers=['CPUExecutionProvider']  # Use CPU, can switch to CUDAExecutionProvider if GPU available
        )
        
        # Get model input/output details
        self.input_name = self.session.get_inputs()[0].name
        self.output_names = [output.name for output in self.session.get_outputs()]
        
        # Get input shape (assuming format: batch, channels, height, width)
        self.input_shape = self.session.get_inputs()[0].shape
        self.input_height = self.input_shape[2] if len(self.input_shape) > 2 else 640
        self.input_width = self.input_shape[3] if len(self.input_shape) > 3 else 640
        
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        
        # Class names based on cat_body_parts.yaml
        self.class_names = ["eye", "mouth", "tail"]
    
    def preprocess_image(self, image: np.ndarray) -> Tuple[np.ndarray, float, float]:
        """
        Preprocess image for YOLO/ONNX model input
        
        Args:
            image: Input image as numpy array (BGR format from OpenCV)
            
        Returns:
            Tuple of (preprocessed_image, x_scale, y_scale) for coordinate mapping
        """
        # Get original dimensions
        original_height, original_width = image.shape[:2]
        
        # Resize image to model input size while maintaining aspect ratio
        scale = min(self.input_width / original_width, self.input_height / original_height)
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        
        # Resize image
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
        
        # Create padded image
        padded = np.full((self.input_height, self.input_width, 3), 114, dtype=np.uint8)
        padded[:new_height, :new_width] = resized
        
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB)
        
        # Normalize to [0, 1] and convert to float32
        normalized = rgb_image.astype(np.float32) / 255.0
        
        # Convert HWC to CHW format
        transposed = np.transpose(normalized, (2, 0, 1))
        
        # Add batch dimension
        batched = np.expand_dims(transposed, axis=0)
        
        # Calculate scales for coordinate mapping
        x_scale = original_width / new_width
        y_scale = original_height / new_height
        
        return batched, x_scale, y_scale
    
    def postprocess_output(self, outputs: np.ndarray, x_scale: float, y_scale: float) -> List[Dict]:
        """
        Post-process model output to get detections
        
        Args:
            outputs: Model output array with shape [batch, features, detections] or [batch, detections, features]
            x_scale: Scale factor for x coordinates
            y_scale: Scale factor for y coordinates
            
        Returns:
            List of detections with format: [{"class": str, "confidence": float, "bbox": [x1, y1, x2, y2]}]
        """
        detections = []
        
        # Remove batch dimension if present
        if len(outputs.shape) == 3:
            output = outputs[0]  # Shape: [features, detections] or [detections, features]
        else:
            output = outputs
        
        # Check output format: [features, detections] vs [detections, features]
        # YOLO v8 typically outputs [7, 8400] or [8400, 7]
        # Format [7, 8400]: [x_center, y_center, width, height, objectness, class0, class1, class2]
        
        if output.shape[0] < output.shape[1]:
            # Format: [features, detections] - need to transpose
            # Shape: [7, 8400] -> transpose to [8400, 7]
            output = output.transpose(1, 0)  # Now [8400, 7]
        
        # Now output should be [detections, features] with shape [N, 7]
        # Features: [x_center, y_center, width, height, objectness, class0, class1, class2]
        # Coordinates are in pixel values relative to model input size (640x640)
        for detection in output:
            # Extract box coordinates (in pixels, not normalized)
            x_center = float(detection[0])
            y_center = float(detection[1])
            width = float(detection[2])
            height = float(detection[3])
            
            # Get confidence/objectness score
            # For YOLO v8, this could be objectness or combined confidence
            objectness_or_conf = float(detection[4])
            
            # Get class probabilities (remaining features after x, y, w, h, objectness)
            if output.shape[1] > 5:
                class_probs = detection[5:]
                class_id = int(np.argmax(class_probs))
                class_conf = float(class_probs[class_id])
                
                # Use class probability as confidence (often more reliable than objectness * class)
                # Some YOLO models output class probabilities directly
                conf = class_conf
            else:
                # Only objectness/confidence, no class probabilities
                conf = objectness_or_conf
                class_id = 0
            
            # Lower threshold for development (YOLO models often have lower confidence)
            # Filter by confidence threshold
            if conf < self.conf_threshold:
                continue
            
            # Convert center+wh format to x1,y1,x2,y2 format (in model input space)
            x1 = x_center - width / 2
            y1 = y_center - height / 2
            x2 = x_center + width / 2
            y2 = y_center + height / 2
            
            # Scale back to original image coordinates
            x1 = int(x1 * x_scale)
            y1 = int(y1 * y_scale)
            x2 = int(x2 * x_scale)
            y2 = int(y2 * y_scale)
            
            # Validate bounding box
            if x2 <= x1 or y2 <= y1:
                continue
            
            detections.append({
                "class": self.class_names[class_id] if class_id < len(self.class_names) else f"class_{class_id}",
                "confidence": conf,
                "bbox": [x1, y1, x2, y2]
            })
        
        # Apply Non-Maximum Suppression (NMS)
        detections = self._apply_nms(detections)
        
        return detections
    
    def _apply_nms(self, detections: List[Dict]) -> List[Dict]:
        """Apply Non-Maximum Suppression to remove overlapping detections"""
        if not detections:
            return []
        
        # Convert to format for NMS
        boxes = np.array([det["bbox"] for det in detections])
        scores = np.array([det["confidence"] for det in detections])
        
        # Apply NMS using OpenCV
        indices = cv2.dnn.NMSBoxes(
            boxes.tolist(),
            scores.tolist(),
            self.conf_threshold,
            self.iou_threshold
        )
        
        if len(indices) == 0:
            return []
        
        # Filter detections using NMS indices
        if isinstance(indices, np.ndarray):
            indices = indices.flatten()
        
        filtered_detections = [detections[i] for i in indices]
        return filtered_detections
    
    def detect(self, image: np.ndarray) -> List[Dict]:
        """
        Detect cat body parts in an image
        
        Args:
            image: Input image as numpy array (BGR format from OpenCV)
            
        Returns:
            List of detections
        """
        # Preprocess image
        preprocessed, x_scale, y_scale = self.preprocess_image(image)
        
        # Run inference
        outputs = self.session.run(self.output_names, {self.input_name: preprocessed})
        
        # Get first output (assuming single output)
        output = outputs[0] if len(outputs) > 0 else outputs
        
        # Post-process
        detections = self.postprocess_output(output, x_scale, y_scale)
        
        return detections

