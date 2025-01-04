import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def notify_job_completion(job_id: str, filename: str, webhook_url: str) -> bool:
    """
    Notifica la finalización de un job vía webhook
    
    Args:
        job_id (str): ID del trabajo completado
        filename (str): Nombre del archivo generado
        webhook_url (str): URL del webhook para notificar
    
    Returns:
        bool: True si la notificación fue exitosa
    """
    payload = {
        "email": "jpramirez5@uc.cl",  # Email fijo para todas las notificaciones
        "link": f"https://xepelin.com/"
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        logger.info(f"Notificación enviada para job {job_id} al webhook {webhook_url}")
        return True
    except Exception as e:
        logger.error(f"Error al enviar notificación para job {job_id}: {e}")
        return False 