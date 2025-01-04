from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ScrapingResponse(BaseModel):
    """Modelo de respuesta para el inicio del scraping"""
    job_id: str
    status: str
    message: str

class ArticleResponse(BaseModel):
    """Modelo de respuesta para el estado del job"""
    job_id: str
    status: str
    category: str
    model: str
    duration: Optional[float] = None
    error: Optional[str] = None
    articles_count: Optional[int] = None
    articles: Optional[List[Dict[str, Any]]] = None
