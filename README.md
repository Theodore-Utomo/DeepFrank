# DeepFrank - Cat Emotional Analysis App

DeepFrank is a full-stack web application for analyzing cat emotions and providing insights about cat health and behavior. The app uses AI to analyze cat images and provides a chat interface for discussing your cat's emotional state.

For a detailed reflection on the project development process, challenges, and learnings, see [reflection.txt](reflection.txt).

## Features

- 🐱 **Image Analysis**: Upload cat images for emotional state analysis
- 💬 **AI Chat**: Chat with Frankie, an AI assistant specializing in cat health
- 📊 **Profile Management**: View your analysis history and saved chats
- 🔐 **Authentication**: Secure authentication using Stytch magic links

## Branches

### Main Branch
The main branch includes all features listed above, using Claude's vision API for image analysis and full chatbot functionality.

### cv-version Branch
The `cv-version` branch is an experimental branch that does **not** include chatbot functionality. The purpose of this branch was to test how a fine-tuned YOLO object detection model would perform in a production environment. The model was designed to detect and analyze specific body parts (eyes, mouth, tail, etc.) to deduce a cat's emotional state.

**Key findings from the cv-version branch:**
- The YOLO object detection model showed significant limitations in production
- The model frequently missed critical body parts such as eyes, mouths, and tails
- These detection failures limited the model's ability to provide accurate emotional state analysis
- This evaluation helped inform the decision to use LLM-based image analysis in the main branch instead

**Note**: If switching to the `cv-version` branch, make sure to rebuild Docker containers as mentioned in the [Rebuilding Containers](#rebuilding-containers) section below.

## Tech Stack

### Backend
- **FastAPI** - Python web framework
- **PostgreSQL** - Database
- **Docker** - Containerization
- **Ollama** - LLM for chat functionality
- **Claude API** - Image analysis (optional)
- **Stytch** - Authentication

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Radix UI** - UI components

## Prerequisites

Before you begin, ensure you have the following installed:

- [Docker](https://www.docker.com/get-started) (version 20.10 or later)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 2.0 or later)
- Git

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd DeepFrankRepo
```

### 2. Set Up Environment Variables

Create a `.env` file in `DeepFrankApp/backend/`:

```bash
cd DeepFrankApp/backend
touch .env
```

Contact the repository owner for the required environment variables and add them to the `.env` file.

### 3. Start the Application

From the project root directory:

```bash
docker-compose up --build
```

This will:
- Build the Docker images for backend, frontend, and database
- Start PostgreSQL database
- Start the FastAPI backend on `http://localhost:8000`
- Start the Next.js frontend on `http://localhost:3000`

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Health Check**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs (Swagger UI)

## Development

### Running in Development Mode

The Docker setup includes hot-reload for both frontend and backend:

- **Backend**: Code changes in `DeepFrankApp/backend/` are automatically reloaded
- **Frontend**: Code changes in `DeepFrankApp/frontend/` are automatically reloaded

### Stopping the Application

```bash
docker-compose down
```

To also remove volumes (database data):

```bash
docker-compose down -v
```

### Viewing Logs

```bash
docker-compose logs -f
```

### Rebuilding Containers

If you change dependencies or Dockerfiles:

```bash
docker-compose build
docker-compose up
```

**Important**: If switching to the `cv-version` branch (or any branch with different dependencies), make sure to delete, restart, and rebuild the Docker containers so that the appropriate dependencies are installed:

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

## Database Setup

The database is automatically initialized when the backend starts. If you need to run migrations manually:

```bash
docker-compose exec api alembic upgrade head
```

To create a new migration:

```bash
docker-compose exec api alembic revision --autogenerate -m "description"
```

## Configuration

Configuration is managed through environment variables. Contact the repository owner for the required environment variable values.

## API Endpoints

### Health Check
- `GET /health` - Health check endpoint

### Authentication
- `POST /api/v1/auth/magic-link` - Request magic link
- `GET /api/v1/auth/callback` - Magic link callback
- `GET /api/v1/auth/me` - Get current user

### Image Analysis
- `POST /api/v1/analyze-image` - Analyze cat image

### Chat
- `GET /api/v1/chat/session/{session_id}/messages` - Get chat messages
- `POST /api/v1/chat/session/{session_id}/messages` - Send message

### Profile
- `GET /api/v1/profile/analyses` - Get user's analysis history

## Troubleshooting

### Port Already in Use

If ports 3000, 8000, or 5433 are already in use, you can modify them in `docker-compose.yml`:

```yaml
ports:
  - "3001:3000"  # Change frontend port
  - "8001:8000"  # Change backend port
  - "5434:5432"  # Change database port
```

### Database Connection Issues

Ensure the PostgreSQL container is healthy:

```bash
docker-compose ps
```

Check database logs:

```bash
docker-compose logs postgres
```

### Backend Not Starting

Check backend logs:

```bash
docker-compose logs api
```

Common issues:
- Missing environment variables
- Database not ready (wait for health check)
- Port conflicts

### Frontend Build Issues

If the frontend fails to build:

```bash
docker-compose build frontend --no-cache
```

### Clearing Everything

To start fresh:

```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```


