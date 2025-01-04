from collections import deque
from typing import Dict, Optional, List, Any
import asyncio
from asyncio import Semaphore, TimeoutError
import time
from core.logging import logger
from models.jobs import ScrapingJob
from models.requests import ScraperModel
from services.scraper_factory import ScraperFactory
from core.config import settings
from core.notifications import notify_job_completion
from services.sheets_service import sheets_service

class QueueService:
    def __init__(self):
        self.queue: deque = deque()
        self.results: Dict[str, ScrapingJob] = {}
        self._model_semaphores: Dict[ScraperModel, Semaphore] = {
            ScraperModel.BASE: Semaphore(1),
            ScraperModel.OPTIMIZED: Semaphore(1),
            ScraperModel.ULTRA: Semaphore(1)
        }
        self.scraper_factory = ScraperFactory()

    def _force_partial_if_timeout(self, job: ScrapingJob) -> None:
        """Fuerza el estado partial si se excede el tiempo"""
        if not job.start_time or not job.end_time:
            return
            
        duration = job.end_time - job.start_time
        # Si la duración es 60 o más, SIEMPRE es partial
        if duration >= settings.MAX_TIMEOUT:
            job.status = "partial"
            job.error = f"Timeout: se devuelven resultados parciales (duración: {duration:.2f}s)"
            logger.warning(f"Job {job.job_id} forzado a partial por duración: {duration:.2f}s")

    async def process_job(self, job: ScrapingJob) -> None:
        """Procesa un trabajo de scraping de manera asíncrona"""
        try:
            async with self._model_semaphores[job.model]:
                start = time.time()
                job.start_time = start
                job.status = "processing"
                logger.info(f"Iniciando procesamiento de job {job.job_id} con modelo {job.model}")

                try:
                    scraper = self.scraper_factory.get_scraper(job.model)
                    
                    async def do_scraping():
                        if hasattr(scraper, 'scrape_async'):
                            return await scraper.scrape_async(job.category)
                        else:
                            loop = asyncio.get_running_loop()
                            return await loop.run_in_executor(None, scraper.scrape, job.category)

                    try:
                        results = await asyncio.wait_for(do_scraping(), timeout=settings.MAX_TIMEOUT - 1)
                        job.results = results if results else []
                        job.status = "completed"
                        
                        print(f"\n=== Scraping Completado ===")
                        print(f"ID: {job.job_id}")
                        print(f"Modelo: {job.model}")
                        print(f"Categoría: {job.category}")
                        print(f"Total artículos: {len(job.results)}")
                        print("===========================\n")
                        
                    except asyncio.TimeoutError:
                        job.status = "partial"
                        if hasattr(scraper, 'get_partial_results'):
                            job.results = await scraper.get_partial_results()
                        elif hasattr(scraper, 'partial_results'):
                            job.results = scraper.partial_results
                        else:
                            job.results = []
                        job.error = "Timeout: se devuelven resultados parciales"
                        logger.warning(f"Timeout en job {job.job_id}. Artículos: {len(job.results) if job.results else 0}")

                except Exception as e:
                    job.status = "error"
                    job.error = str(e)
                    logger.error(f"Error procesando job {job.job_id}: {str(e)}")

                finally:
                    end = time.time()
                    job.end_time = end
                    
                    self._force_partial_if_timeout(job)
                    
                    # Si hay resultados, guardar en Google Sheets y notificar
                    if job.results and len(job.results) > 0:
                        # Save to Google Sheets asíncronamente
                        success, sheet_url = await sheets_service.save_job_results(job)
                        
                        if success:
                            # Notify completion with sheet URL and email
                            notify_job_completion(
                                job_id=job.job_id,
                                webhook_url=job.webhook,
                                sheet_url=sheet_url,
                                email=job.email
                            )
                    
                    if job in self.queue:
                        self.queue.remove(job)
                    self.results[job.job_id] = job

        except Exception as e:
            logger.error(f"Error en job {job.job_id}: {str(e)}")
            job.status = "error"
            job.error = str(e)
            job.end_time = time.time()
            if job in self.queue:
                self.queue.remove(job)
            self.results[job.job_id] = job

    def add_job(self, job: ScrapingJob) -> None:
        """Agrega un trabajo a la cola"""
        self.queue.append(job)

    def get_job_status(self, job_id: str) -> Optional[ScrapingJob]:
        """Obtiene el estado de un trabajo específico"""
        # Buscar en la cola
        for job in self.queue:
            if job.job_id == job_id:
                return job
        # Buscar en resultados
        return self.results.get(job_id)

    def _format_job_info(self, job: ScrapingJob, job_type: str) -> Dict[str, Any]:
        """Formatea la información del trabajo según su tipo"""
        info = {
            "job_id": job.job_id,
            "status": job.status,
            "category": job.category,
            "model": job.model
        }

        if job_type == "queue":
            # Para trabajos en cola, mostrar tiempo de espera
            info["waiting_time"] = round(time.time() - job.queued_at, 2)
        elif job_type == "processing":
            # Para trabajos en proceso, información básica
            if job.start_time:
                info["duration"] = round(time.time() - job.start_time, 2)
        elif job_type == "finished":
            # Para trabajos completados, mostrar estadísticas
            info["articles_count"] = len(job.results) if job.results else 0
            if job.start_time and job.end_time:
                info["duration"] = round(job.end_time - job.start_time, 2)

        return info

    def get_queue_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual de la cola"""
        # Obtener trabajos por estado
        pending_jobs = [job for job in self.queue if job.status == "pending"]
        processing_jobs = [
            job for job in list(self.queue) + list(self.results.values())
            if job.status == "processing"
        ]
        completed_jobs = [
            job for job in self.results.values()
            if job.status in ["completed", "partial", "error"]
        ]

        return {
            "pending_jobs": len(pending_jobs),
            "processing_jobs": len(processing_jobs),
            "completed_jobs": len(completed_jobs),
            "jobs_pending": [
                self._format_job_info(job, "queue") 
                for job in pending_jobs
            ],
            "jobs_processing": [
                self._format_job_info(job, "processing")
                for job in processing_jobs
            ],
            "jobs_finished": [
                self._format_job_info(job, "finished")
                for job in completed_jobs
            ]
        }

queue_service = QueueService()
