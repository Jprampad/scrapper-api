import logging
from datetime import datetime
import sys

class CustomFormatter(logging.Formatter):
    """Formateador personalizado para los logs"""
    
    def formatTime(self, record, datefmt=None):
        """Sobreescribe el formato de tiempo para usar datetime"""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def format(self, record):
        """Formato personalizado para cada línea de log"""
        record.message = record.getMessage()
        
        # Formato base: timestamp - level - message
        log_format = "%(asctime)s - %(levelname)s - %(message)s"
        
        formatter = logging.Formatter(log_format)
        formatter.formatTime = self.formatTime
        
        return formatter.format(record)

def setup_logger(name: str = "xepelin_scraper") -> logging.Logger:
    """
    Configura y retorna un logger con formato personalizado
    
    Args:
        name: Nombre del logger
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Evitar duplicación de handlers
    if not logger.handlers:
        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(CustomFormatter())
        logger.addHandler(console_handler)
    
    # Evitar propagación a root logger
    logger.propagate = False
    
    return logger

# Crear instancia global del logger
logger = setup_logger()