from pydantic import BaseModel, EmailStr, HttpUrl
from enum import Enum
from typing import Optional

class ScraperModel(str, Enum):
    BASE = "base"
    OPTIMIZED = "optimized"
    ULTRA = "ultra"

class ScrapingRequest(BaseModel):
    """Modelo de request para scraping"""
    category: str
    webhook: HttpUrl
    model: Optional[ScraperModel] = ScraperModel.ULTRA
    email: Optional[EmailStr] = "jpramirez5@uc.cl"

    class Config:
        json_schema_extra = {
            "example": {
                "category": "xepelin",
                "webhook_url": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr"
            }
        }