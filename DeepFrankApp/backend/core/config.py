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

# Data paths
DATA_DIR = BASE_DIR.parent.parent / "Data"
BREEDS_JSON_PATH = DATA_DIR / "breeds.json"

# Application metadata
APP_NAME = "DeepFrank API"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "API for DeepFrank cat emotional analysis using deep learning"

