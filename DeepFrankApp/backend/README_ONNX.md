# ONNX Model Integration Guide

This guide explains how the ONNX model (`cat_model.onnx`) is integrated into the DeepFrank API, following the approach from the [Cat-Emotional-Analysis repository](https://github.com/Arwa-Fawzy/Cat-Emotional-Analysis).

## Architecture

The implementation consists of three main components:

### 1. ONNX Inference Module (`onnx_inference.py`)
- **CatBodyPartDetector**: Loads and runs inference using the ONNX model
- Detects cat body parts: **eyes**, **mouth**, and **tail**
- Handles image preprocessing (resizing, normalization for YOLO format)
- Post-processes model outputs to extract bounding boxes and confidence scores

### 2. Body Part Analysis (`body_part_analysis.py`)
Analyzes each detected body part to determine emotional state:

- **EyeAnalyzer**: 
  - Analyzes eye contours
  - Calculates ratio of whites to dark areas (pupil/iris)
  - Determines if eyes are "wide_open", "normal", or "closed"

- **MouthAnalyzer**:
  - Detects mouth opening using edge detection
  - Determines if mouth is "open" or "closed"

- **TailAnalyzer**:
  - Analyzes tail position and orientation
  - Calculates tail angle and dimensions
  - Determines tail position: "up", "down", "left", or "right"

- **CatEmotionAnalyzer**:
  - Combines all body part analyses
  - Maps body language combinations to emotional states:
    - alert, fearful, content, playful, sleepy, excited, aggressive, etc.

### 3. FastAPI Integration (`main.py`)
Provides REST API endpoints:

- `POST /api/v1/analyze-image`: Full analysis (detection + emotional state)
- `POST /api/v1/detect-body-parts`: Just body part detection
- `GET /api/v1/breeds`: Get available cat breeds

## Usage

### Starting the Server

```bash
cd DeepFrankApp/backend
pip install -r requirements.txt
python main.py
```

Or using Docker:
```bash
docker-compose up
```

### Example API Request

```python
import requests

# Upload an image for analysis
with open("cat_image.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/analyze-image",
        files={"file": f}
    )

result = response.json()
print(f"Emotion: {result['emotion']}")
print(f"Detections: {result['detections']}")
print(f"Analysis: {result['analysis']}")
```

### Response Format

```json
{
  "detections": [
    {
      "class_name": "eye",
      "confidence": 0.85,
      "bbox": [100, 150, 200, 250]
    },
    {
      "class_name": "mouth",
      "confidence": 0.78,
      "bbox": [180, 280, 250, 320]
    },
    {
      "class_name": "tail",
      "confidence": 0.92,
      "bbox": [300, 400, 350, 600]
    }
  ],
  "analysis": {
    "eye_state": "wide_open",
    "mouth_state": "closed",
    "tail_position": "up",
    "tail_angle": 45.0
  },
  "emotion": "alert"
}
```

## Model Requirements

- **Model File**: `cat_model.onnx` must be in the `DeepFrankApp/backend/` directory
- **Input Format**: The model expects images in YOLO format:
  - RGB format
  - Resized to model input size (typically 640x640)
  - Normalized to [0, 1] range
  - CHW format (Channels, Height, Width)

- **Output Format**: YOLO-style detections with:
  - Bounding box coordinates (center_x, center_y, width, height)
  - Confidence scores
  - Class probabilities

## How It Works (Similar to Original Repo)

1. **Image Preprocessing**: 
   - Resize image while maintaining aspect ratio
   - Pad to model input size
   - Normalize pixel values

2. **ONNX Inference**:
   - Load model using ONNX Runtime
   - Run inference on preprocessed image
   - Get detection predictions

3. **Post-Processing**:
   - Convert normalized coordinates to pixel coordinates
   - Apply Non-Maximum Suppression (NMS) to remove duplicates
   - Filter by confidence threshold

4. **Body Part Analysis**:
   - Extract ROI (Region of Interest) for each detected part
   - Analyze each part:
     - **Eyes**: Contour analysis, white/dark ratio
     - **Mouth**: Edge detection for opening
     - **Tail**: Position, angle, orientation
   - Combine results to determine emotional state

5. **Emotion Determination**:
   - Map body part states to emotional states
   - Return comprehensive analysis result

## Dependencies

- `onnxruntime`: For running ONNX model inference
- `opencv-python`: For image processing and computer vision operations
- `numpy`: For array operations
- `fastapi`: For the REST API
- `python-multipart`: For file uploads

## Notes

- The model is loaded lazily on first request
- If the model file is missing, the API will return a 500 error with instructions
- The implementation follows the same approach as the original Cat-Emotional-Analysis repo but uses ONNX Runtime instead of PyTorch/YOLO directly
- For video analysis, you can extend the code to process frames and use the `*_behavior()` methods that aggregate results across frames

