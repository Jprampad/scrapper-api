from enum import Enum
from pydantic import BaseModel
from typing import Optional

class ScraperModel(str, Enum):
    BASE = "base"           # Síncrono
    OPTIMIZED = "optimized" # Síncrono
    ULTRA = "ultra"        # Asíncrono

class ScrapingRequest(BaseModel):
    category: str
    model: ScraperModel = ScraperModel.ULTRA
    webhook: Optional[str] = None