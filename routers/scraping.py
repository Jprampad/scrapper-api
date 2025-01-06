from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import Dict
import uuid
from models.requests import ScrapingRequest
from models.responses import ScrapingResponse, ArticleResponse
from services.queue_service import queue_service
from core.config import settings
from core.exceptions import handle_scraper_exception
from models.jobs import ScrapingJob
from pydantic import ValidationError
from core.logging import logger
import json
from pathlib import Path
import os

router = APIRouter(prefix="/scraping", tags=["Scraping"])

SCRIPT_DIR = Path(__file__).resolve().parent
DOCS_DIR = os.path.join(SCRIPT_DIR.parent , 'docs')

def load_endpoint_docs(filename: str) -> Dict:
    """
    Load endpoint documentation from JSON files.
    Uses paths relative to the script location.
    """
    # Construir ruta completa al archivo JSON
    json_path = os.path.join('./docs', filename)
    
    # Verificar que el archivo existe
    if not os.path.exists(json_path):
        raise FileNotFoundError(
            f"Documentation file not found at: {json_path}"
        )
        
    # Cargar y retornar el contenido del JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)
        


# Cargar la documentación al inicio
#scraping_docs = load_endpoint_docs("scraping_post.json")
#status_docs = load_endpoint_docs("status_get.json")
#queue_docs = load_endpoint_docs("queue_status_get.json")
#models_docs = load_endpoint_docs("models_get.json")
#categories_docs = load_endpoint_docs("categories_get.json")

@router.post(
    "",
    response_model=ScrapingResponse,
   # summary=scraping_docs["summary"],
   # description=scraping_docs["description"],
   # responses=scraping_docs["responses"]
)
async def scrape_blog(
    request: ScrapingRequest,
    background_tasks: BackgroundTasks
) -> Dict:
    """Inicia un trabajo de scraping de manera asíncrona"""
    try:
        # Convertir categorías a minúsculas para comparación
        valid_categories = {cat.lower() for cat in settings.VALID_CATEGORIES}
        requested_category = request.category.lower()

        # Validar categoría
        if requested_category not in valid_categories:
            logger.warning(f"Intento de scraping con categoría inválida: {request.category}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Categoría no válida",
                    "message": f"La categoría '{request.category}' no está disponible",
                    "valid_categories": sorted(list(settings.VALID_CATEGORIES)),
                    "suggestion": "Usa el endpoint GET /scraping/categories para ver las categorías disponibles"
                }
            )
        
        # Crear job
        job_id = str(uuid.uuid4())
        logger.info(f"Creando nuevo job {job_id} para categoría {request.category}")
        
        try:
            job = ScrapingJob(
                job_id=job_id, 
                category=request.category, 
                model=request.model,
                webhook=request.webhook,
                email=request.email
            )
        except Exception as e:
            logger.error(f"Error al crear el job: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Error al crear el trabajo",
                    "message": str(e)
                }
            )
        
        # Agregar job a la cola
        queue_service.add_job(job)
        background_tasks.add_task(queue_service.process_job, job)
        
        logger.info(f"Job {job_id} creado exitosamente para categoría {request.category}")
        return {
            "job_id": job_id,
            "status": "accepted",
            "message": f"Trabajo de scraping iniciado. Use GET /scraping/status/{job_id} para verificar el estado"
        }

    except ValidationError as e:
        logger.error(f"Error de validación: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail={
                "error": "Error de validación",
                "message": "Los datos proporcionados no son válidos",
                "details": e.errors()
            }
        )
    except HTTPException as e:
        logger.error(f"Error HTTP {e.status_code}: {e.detail}")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail
        )
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        raise handle_scraper_exception(e)

@router.get(
    "/queue/status",
    #summary=queue_docs["summary"],
    #description=queue_docs["description"],
    #responses=queue_docs["responses"]
)
async def get_queue_status() -> Dict:
    """Obtiene el estado actual de la cola de trabajos"""
    return queue_service.get_queue_status()

@router.get(
    "/models",
    #summary=models_docs["summary"],
    #description=models_docs["description"],
    #responses=models_docs["responses"]
)
async def get_available_models() -> Dict:
    """Retorna los modelos de scraper disponibles"""
    return {
        "models": [model.value for model in ScraperModel]
    }

@router.get(
    "/categories",
   # summary=categories_docs["summary"],
   # description=categories_docs["description"],
   # responses=categories_docs["responses"]
)
async def get_available_categories() -> Dict:
    """Retorna las categorías disponibles para scraping"""
    return {
        "categories": list(settings.VALID_CATEGORIES)
    }

@router.get(
    "/status/{job_id}",
    response_model=ArticleResponse,
    #summary=status_docs["summary"],
    #description=status_docs["description"],
    #responses=status_docs["responses"]
)
async def get_job_status(job_id: str) -> Dict:
    """Obtiene el estado y resultados de un trabajo de scraping"""
    job = queue_service.get_job_status(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Trabajo no encontrado: {job_id}"
        )
    return job.to_dict()
