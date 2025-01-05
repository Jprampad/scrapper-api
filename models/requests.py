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
    email: EmailStr
    model: Optional[ScraperModel] = ScraperModel.ULTRA

    class Config:
        json_schema_extra = {
            "example": {
                "category": "xepelin",
                "webhook_url": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr",
                "email": "jpramirez5@uc.cl"
            }
        }