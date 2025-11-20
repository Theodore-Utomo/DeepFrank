"""Application configuration"""
import os
from pathlib import Path
from typing import List

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Model configuration
MODEL_PATH = BASE_DIR / "cat_model.onnx"
MODEL_CONF_THRESHOLD = float(os.getenv("MODEL_CONF_THRESHOLD", "0.2"))
MODEL_IOU_THRESHOLD = float(os.getenv("MODEL_IOU_THRESHOLD", "0.45"))

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

# Ollama configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://cscigpu08.bc.edu:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:latest")
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0"))

# Chat system prompt
CHAT_SYSTEM_PROMPT = os.getenv(
    "CHAT_SYSTEM_PROMPT",
    "You are Frankie, a helpful, friendly, and knowledgeable assistant specializing in cat health and emotional analysis. You help users understand their cat's emotional state and provide helpful advice about cat care."
)

# Application metadata
APP_NAME = "DeepFrank API"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "API for DeepFrank cat emotional analysis using deep learning"

