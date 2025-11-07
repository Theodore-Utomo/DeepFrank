"""Breeds routes"""
import json
from fastapi import APIRouter, HTTPException
from models.schemas import BreedsResponse
from core.config import BREEDS_JSON_PATH

router = APIRouter()


@router.get("/breeds", response_model=BreedsResponse)
async def get_breeds():
    """Get list of available cat breeds"""
    try:
        if BREEDS_JSON_PATH.exists():
            with open(BREEDS_JSON_PATH, 'r') as f:
                breeds_data = json.load(f)
                return {"breeds": breeds_data, "message": None}
        
        return {
            "breeds": [],
            "message": "Breeds endpoint - implement to load from breeds.json"
        }
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Error parsing breeds.json: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading breeds: {str(e)}")

