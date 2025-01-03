from typing import Set
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Configuración general
    MAX_TIMEOUT: int = 300
    MAX_WORKERS: int = 3
    REQUEST_TIMEOUT: int = 30  # Aumentar el timeout para las peticiones HTTP
    
    # Configuración de scraping
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 1
    
    # Categorías válidas
    VALID_CATEGORIES: Set[str] = {
        "todas las categorias",
        "pymes",
        "corporativos",
        "casos de exito",
        "educacion financiera",
        "xepelin",
        "emprendedores"
    }
    
    # Configuración de logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(levelname)s - %(message)s"
    LOG_FILE: str = str(Path("logs") / "api.log")
    LOG_DIR: str = str(Path("logs"))

settings = Settings()