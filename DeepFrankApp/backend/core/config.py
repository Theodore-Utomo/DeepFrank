"""Application configuration"""
import os
from pathlib import Path
from typing import List

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# API configuration
API_V1_PREFIX = "/api/v1"
ALLOWED_ORIGINS: List[str] = os.getenv(
    "ALLOWED_ORIGINS", "*"
).split(",") if os.getenv("ALLOWED_ORIGINS") != "*" else ["*"]

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://localhost:5432/deepfrank_test"
)
# For synchronous operations (Alembic migrations)
DATABASE_URL_SYNC = DATABASE_URL.replace("+asyncpg", "").replace("postgresql+asyncpg", "postgresql+psycopg2")

# Stytch configuration
STYTCH_PROJECT_ID = os.getenv("STYTCH_PROJECT_ID")
STYTCH_SECRET = os.getenv("STYTCH_SECRET")
STYTCH_ENVIRONMENT = os.getenv("STYTCH_ENVIRONMENT", "test")
MAGIC_LINK_REDIRECT_URL = os.getenv(
    "MAGIC_LINK_REDIRECT_URL",
    "http://localhost:3000/auth/callback"
)

# Data paths
DATA_DIR = BASE_DIR.parent.parent / "Data"
BREEDS_JSON_PATH = DATA_DIR / "breeds.json"

# Ollama configuration (for chat)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://cscigpu08.bc.edu:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:latest")
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0"))

# Claude API configuration (for image analysis)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20240620")
CLAUDE_TEMPERATURE = float(os.getenv("CLAUDE_TEMPERATURE", "0.7"))

# Chat system prompt
CHAT_SYSTEM_PROMPT = os.getenv(
    "CHAT_SYSTEM_PROMPT",
    "You are Frankie, a helpful, friendly, and knowledgeable assistant specializing in cat health and emotional analysis. You help users understand their cat's emotional state and provide helpful advice about cat care."
)

# Image analysis system prompt
IMAGE_ANALYSIS_SYSTEM_PROMPT = os.getenv(
    "IMAGE_ANALYSIS_SYSTEM_PROMPT",
    """You are an expert in analyzing cat body language and behavior. Analyze the provided cat image and describe:
- Is the cat loafing (paws tucked under)?
- Does it have airplane ears (ears flattened back)?
- Overall body posture and emotional state
- Any other notable body language cues
- Your response should be able to be rendered in Markdown format.

Provide a friendly, conversational analysis that helps the owner understand their cat's current state."""
)

# Application metadata
APP_NAME = "DeepFrank API"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "API for DeepFrank cat emotional analysis using deep learning"

