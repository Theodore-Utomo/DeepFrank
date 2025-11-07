# DeepFrank API Backend

FastAPI backend for DeepFrank animal classification and detection.

## Quick Start

### Using Docker (Recommended)

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

2. Access the API:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### Using Docker directly

1. Build the image:
```bash
cd backend
docker build -t deepfrank-api .
```

2. Run the container:
```bash
docker run -p 8000:8000 deepfrank-api
```

### Local Development

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /` - Root endpoint with API status
- `GET /health` - Health check endpoint
- `GET /api/v1/breeds` - Get list of breeds (to be implemented)
- Interactive API docs available at `/docs`

## Development

The API runs on port 8000 by default. Use `--reload` flag during development for auto-reloading on code changes.

