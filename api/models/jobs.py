from datetime import datetime
import time
from typing import Optional, List, Dict, Any
from api.models.requests import ScraperModel
from pydantic import EmailStr

class ScrapingJob:
    def __init__(
        self, 
        job_id: str, 
        category: str, 
        model: ScraperModel, 
        webhook: Optional[str] = None,
        email: str = None
    ):
        self.job_id = job_id
        self.category = category
        self.model = model
        self.webhook = webhook
        self.email = email
        self.status = "pending"
        self.results: Optional[List[Dict[str, Any]]] = None
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.queued_at = time.time()
        self.partial_results: List[Dict[str, Any]] = []
        self.error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        response = {
            "job_id": self.job_id,
            "status": self.status,
            "category": self.category,
            "model": self.model,
            "email": self.email
        }

        if self.start_time:
            response["duration"] = round(
                (self.end_time or time.time()) - self.start_time,
                2
            )

        if self.error:
            response["error"] = self.error

        if self.status in ["completed", "partial"]:
            response["articles_count"] = len(self.results) if self.results else 0
            response["articles"] = self.results

        return response
