from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Optional

class ScraperModel(str, Enum):
    BASE = "base"           # Síncrono
    OPTIMIZED = "optimized" # Síncrono
    ULTRA = "ultra"        # Asíncrono

class ScrapingRequest(BaseModel):
    """Modelo de request para scraping"""
    category: str
    model: ScraperModel = ScraperModel.ULTRA
    webhook: str
    email: EmailStr