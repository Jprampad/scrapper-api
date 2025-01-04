from fastapi import HTTPException
from typing import Any, Dict, Union

class ScraperException(Exception):
    """Excepción base para errores del scraper"""
    def __init__(self, message: str, status_code: int = 500, details: Dict[str, Any] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class JobNotFoundException(ScraperException):
    """Excepción para cuando no se encuentra un trabajo"""
    def __init__(self, job_id: str):
        super().__init__(
            message=f"Trabajo no encontrado: {job_id}",
            status_code=404,
            details={"job_id": job_id}
        )

class InvalidCategoryException(ScraperException):
    """Excepción para categorías inválidas"""
    def __init__(self, category: str, valid_categories: list):
        super().__init__(
            message=f"Categoría no válida: {category}",
            status_code=400,
            details={
                "category": category,
                "valid_categories": valid_categories
            }
        )

class ScraperTimeoutException(ScraperException):
    """Excepción para timeouts del scraper"""
    def __init__(self, timeout: int, partial_results: bool = False):
        super().__init__(
            message=f"El scraping excedió el tiempo límite de {timeout} segundos",
            status_code=408,
            details={
                "timeout": timeout,
                "partial_results_available": partial_results
            }
        )

class ScraperExecutionException(ScraperException):
    """Excepción para errores durante la ejecución del scraper"""
    def __init__(self, error: str, scraper_type: str):
        super().__init__(
            message=f"Error en la ejecución del scraper: {error}",
            status_code=500,
            details={"scraper_type": scraper_type}
        )

def handle_scraper_exception(e: Exception) -> HTTPException:
    """
    Convierte excepciones del scraper en HTTPException
    
    Args:
        e: Excepción a manejar
    Returns:
        HTTPException configurada según el tipo de error
    """
    if isinstance(e, ScraperException):
        return HTTPException(
            status_code=e.status_code,
            detail={
                "error": e.message,
                "details": e.details
            }
        )
    
    # Manejar excepciones no controladas
    return HTTPException(
        status_code=500,
        detail={
            "error": "Error interno del servidor",
            "message": str(e)
        }
    )

def raise_scraper_exception(
    message: str,
    status_code: int = 500,
    details: Dict[str, Any] = None
) -> None:
    """
    Utilidad para lanzar excepciones del scraper de forma consistente
    
    Args:
        message: Mensaje de error
        status_code: Código HTTP de error
        details: Detalles adicionales del error
    Raises:
        ScraperException
    """
    raise ScraperException(
        message=message,
        status_code=status_code,
        details=details
    )
