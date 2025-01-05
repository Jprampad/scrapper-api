from typing import Set
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):

    MAX_TIMEOUT: int = 1000   

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