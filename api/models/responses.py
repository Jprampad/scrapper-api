from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ScrapingResponse(BaseModel):
    job_id: str
    status: str
    message: str

class ArticleResponse(BaseModel):
    job_id: str
    status: str
    category: str
    model: str
    articles_count: Optional[int] = None
    articles: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    duration: Optional[float] = None
