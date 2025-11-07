# DeepFrank Backend Architecture

This document describes the modular architecture of the DeepFrank backend API.

## Directory Structure

```
backend/
├── main.py                    # Application entry point
├── core/                      # Core configuration and dependencies
│   ├── __init__.py
│   ├── config.py             # Application configuration
│   └── dependencies.py       # Shared dependencies (e.g., detector service)
├── models/                    # Pydantic models and schemas
│   ├── __init__.py
│   └── schemas.py            # API request/response models
├── routes/                    # API route handlers
│   ├── __init__.py
│   ├── health.py             # Health check endpoints
│   ├── detection.py          # Body part detection endpoints
│   ├── analysis.py           # Emotional analysis endpoints
│   └── breeds.py             # Cat breeds endpoints
├── services/                  # Business logic services
│   ├── __init__.py
│   ├── detection_service.py   # ONNX model inference service
│   ├── analysis_service.py   # Body part analysis service
│   └── image_service.py      # Image processing utilities
├── body_part_analysis.py     # Body part analyzers (Eye, Mouth, Tail, Emotion)
├── cat_model.onnx            # ONNX model file
├── requirements.txt          # Python dependencies
└── Dockerfile                # Docker configuration
```

## Architecture Overview

### Core Layer (`core/`)

**config.py**: Centralized configuration management
- Model paths and thresholds
- API settings
- CORS configuration
- Data paths

**dependencies.py**: Dependency injection for FastAPI
- Lazy-loading detector service
- Shared dependencies across routes

### Models Layer (`models/`)

**schemas.py**: Pydantic models for API contracts
- Request/response validation
- Type safety
- API documentation generation

### Routes Layer (`routes/`)

Route handlers organized by functionality:
- **health.py**: Health check and root endpoints
- **detection.py**: Body part detection endpoints
- **analysis.py**: Full emotional analysis endpoints
- **breeds.py**: Cat breeds information endpoints

### Services Layer (`services/`)

Business logic separated from route handlers:

**detection_service.py**: 
- ONNX model loading and inference
- Image preprocessing for YOLO format
- Post-processing and NMS
- Returns detection results

**analysis_service.py**:
- Coordinates body part analysis
- Determines emotional state
- Uses analyzers from `body_part_analysis.py`

**image_service.py**:
- Image format conversion utilities
- ROI extraction helpers

### Analysis Module (`body_part_analysis.py`)

Standalone analysis classes:
- **EyeAnalyzer**: Analyzes eye state (wide_open, normal, closed)
- **MouthAnalyzer**: Analyzes mouth state (open, closed)
- **TailAnalyzer**: Analyzes tail position and angle
- **CatEmotionAnalyzer**: Determines emotional state from body parts

## Request Flow

1. **Client Request** → FastAPI route handler
2. **Route Handler** → Validates request, calls service
3. **Service Layer** → Business logic execution
   - Image processing
   - Model inference
   - Analysis
4. **Response** → Pydantic model validation → JSON response

## Example: Image Analysis Flow

```
POST /api/v1/analyze-image
  ↓
routes/analysis.py:analyze_image()
  ↓
services/image_service.py:bytes_to_cv2_image()
  ↓
services/detection_service.py:detect()
  ↓ (ONNX inference)
services/analysis_service.py:analyze_body_parts()
  ↓
body_part_analysis.py:EyeAnalyzer, MouthAnalyzer, TailAnalyzer
  ↓
body_part_analysis.py:CatEmotionAnalyzer
  ↓
Response: DetectionResponse
```

## Benefits of This Architecture

1. **Separation of Concerns**: Routes, services, and models are clearly separated
2. **Testability**: Services can be tested independently
3. **Maintainability**: Easy to locate and modify specific functionality
4. **Scalability**: Services can be extracted to microservices if needed
5. **Production-Ready**: Follows FastAPI best practices
6. **Dependency Injection**: Services are injected via FastAPI's Depends()

## Environment Variables

- `MODEL_CONF_THRESHOLD`: Confidence threshold for detections (default: 0.25)
- `MODEL_IOU_THRESHOLD`: IoU threshold for NMS (default: 0.45)
- `ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins (default: "*")

## Running the Application

```bash
# Development
python main.py

# Production (with uvicorn)
uvicorn main:app --host 0.0.0.0 --port 8000

# Docker
docker-compose up
```

