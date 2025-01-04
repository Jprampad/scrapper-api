from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class ScraperModel(str, Enum):
    BASE = "base"
    OPTIMIZED = "optimized"
    ULTRA = "ultra"

class ScrapingRequest(BaseModel):
    """Modelo de request para scraping"""
    category: str
    model: ScraperModel = ScraperModel.ULTRA
    webhook: str
    email: EmailStr