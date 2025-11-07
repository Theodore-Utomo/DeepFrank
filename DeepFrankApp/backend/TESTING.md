# Testing the Analysis Route

This guide shows you how to test the `/api/v1/analyze-image` endpoint.

## Method 1: Using FastAPI's Interactive Docs (Easiest)

1. Open your browser and go to: **http://localhost:8000/docs**
2. Find the `POST /api/v1/analyze-image` endpoint
3. Click "Try it out"
4. Click "Choose File" and select a cat image
5. Click "Execute"
6. View the response with detections, analysis, and emotion

## Method 2: Using cURL

```bash
# Test with a cat image from your Data directory
curl -X POST "http://localhost:8000/api/v1/analyze-image" \
  -F "file=@/Users/theodoreutomo/DeepFrankRepo/Data/cat_body_parts_dataset/images/test/Abyssinian_3.jpg" \
  | python3 -m json.tool
```

Or with a prettier output:
```bash
curl -X POST "http://localhost:8000/api/v1/analyze-image" \
  -F "file=@/Users/theodoreutomo/DeepFrankRepo/Data/cat_body_parts_dataset/images/test/British_Shorthair_113.jpg" \
  | jq '.'
```

## Method 3: Using Python requests

Create a test script:

```python
import requests
import json

# Path to your test image
image_path = "../Data/cat_body_parts_dataset/images/test/Abyssinian_3.jpg"

# Make the request
url = "http://localhost:8000/api/v1/analyze-image"
with open(image_path, "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)

# Print the response
print(json.dumps(response.json(), indent=2))
```

## Method 4: Quick Test Script

Run this in your terminal:

```bash
cd /Users/theodoreutomo/DeepFrankRepo
python3 -c "
import requests
import json

image_path = 'Data/cat_body_parts_dataset/images/test/Abyssinian_3.jpg'
url = 'http://localhost:8000/api/v1/analyze-image'

with open(image_path, 'rb') as f:
    files = {'file': f}
    response = requests.post(url, files=files)

print(json.dumps(response.json(), indent=2))
"
```

## Expected Response Format

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

## Available Test Images

You have test images available in:
- `Data/cat_body_parts_dataset/images/test/`
  - Abyssinian_3.jpg
  - British_Shorthair_113.jpg
  - British_Shorthair_65.jpg
  - Egyptian_Mau_149.jpg
  - Ragdoll_104.jpg
  - Ragdoll_105.jpg
  - Russian_Blue_94.jpg
  - Siamese_40.jpg
  - Sphynx_9.jpg

## Testing Tips

1. **Start with the Swagger UI** (http://localhost:8000/docs) - it's the easiest way to test
2. **Check the logs** if something fails: `docker-compose logs -f`
3. **Verify the model file** exists: `cat_model.onnx` should be in the backend directory
4. **Test with different images** to see how the analysis varies

