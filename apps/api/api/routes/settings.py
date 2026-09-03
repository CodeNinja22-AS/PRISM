from fastapi import APIRouter
from pydantic import BaseModel
import json
import os

router = APIRouter()

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data", "config.json")

class SettingsUpdate(BaseModel):
    platt_a: float
    platt_b: float
    adversarial_strictness: float
    base_reliability: float

def load_settings():
    default_settings = {
        "platt_a": -0.8,
        "platt_b": 0.2,
        "adversarial_strictness": 0.8,
        "base_reliability": 0.85
    }
    if not os.path.exists(CONFIG_FILE):
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_settings, f)
        return default_settings
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        return default_settings

@router.get("/")
def get_settings():
    """
    Retrieves the current ML engine settings.
    """
    return load_settings()

@router.post("/")
def update_settings(settings: SettingsUpdate):
    """
    Updates the ML engine configuration.
    """
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(settings.dict(), f)
    return {"status": "success", "settings": settings.dict()}
