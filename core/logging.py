import logging
from pathlib import Path
from core.config import settings

def setup_logging() -> logging.Logger:
    """
    Configura y retorna el logger principal de la aplicación.
    Crea el directorio de logs si no existe.
    """
    # Crear directorio de logs si no existe
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(exist_ok=True)
    
    # Configurar formato del log
    formatter = logging.Formatter(settings.LOG_FORMAT)
    
    # Configurar handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configurar handler para archivo
    file_handler = logging.FileHandler(settings.LOG_FILE)
    file_handler.setFormatter(formatter)
    
    # Configurar logger principal
    logger = logging.getLogger("api")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Evitar duplicación de handlers
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    # Evitar propagación a root logger
    logger.propagate = False
    
    return logger

# Crear instancia global del logger
logger = setup_logging()

def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger específico para un módulo.
    Args:
        name: Nombre del módulo que solicita el logger
    Returns:
        Logger configurado para el módulo
    """
    module_logger = logging.getLogger(f"api.{name}")
    module_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    return module_logger