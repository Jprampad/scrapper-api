from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import Dict
import uuid
from api.models.requests import ScrapingRequest, ScraperModel
from api.models.responses import ScrapingResponse, ArticleResponse
from api.models.jobs import ScrapingJob
from api.services.queue_service import queue_service
from api.core.config import settings
from api.core.exceptions import handle_scraper_exception

router = APIRouter(prefix="/scraping", tags=["scraping"])

@router.post("", response_model=ScrapingResponse)
async def scrape_blog(
    request: ScrapingRequest,
    background_tasks: BackgroundTasks
) -> Dict:
    """Inicia un trabajo de scraping de manera asíncrona"""
    try:
        # Validar categoría
        if request.category.lower() not in {
            cat.lower() for cat in settings.VALID_CATEGORIES
        }:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Categoría no válida",
                    "valid_categories": list(settings.VALID_CATEGORIES)
                }
            )
        
        job_id = str(uuid.uuid4())
        job = ScrapingJob(
            job_id=job_id, 
            category=request.category, 
            model=request.model,
            webhook=request.webhook,
            email=request.email
        )
        
        queue_service.add_job(job)
        background_tasks.add_task(queue_service.process_job, job)
        
        return {
            "job_id": job_id,
            "status": "accepted",
            "message": f"Trabajo de scraping iniciado. Use GET /scraping/status/{job_id} para verificar el estado"
        }
    except Exception as e:
        raise handle_scraper_exception(e)

@router.get("/queue/status")
async def get_queue_status() -> Dict:
    """Obtiene el estado actual de la cola de trabajos"""
    return queue_service.get_queue_status()

@router.get("/models")
async def get_available_models() -> Dict:
    """Retorna los modelos de scraper disponibles"""
    return {
        "models": [model.value for model in ScraperModel]
    }

@router.get("/categories")
async def get_available_categories() -> Dict:
    """Retorna las categorías disponibles para scraping"""
    return {
        "categories": list(settings.VALID_CATEGORIES)
    }

@router.get("/status/{job_id}", response_model=ArticleResponse)
async def get_job_status(job_id: str) -> Dict:
    """Obtiene el estado y resultados de un trabajo de scraping"""
    job = queue_service.get_job_status(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Trabajo no encontrado: {job_id}"
        )
    return job.to_dict()
