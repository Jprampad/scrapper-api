from fastapi import FastAPI
from routers import scraping
from core.logging import setup_logging

# Configurar logging
setup_logging()

app = FastAPI(
    title="Xepelin Blog Scraper API",
    description="API para extraer artículos del blog de Xepelin",
    version="1.0.0",
    # Deshabilitar redirecciones automáticas
    redirect_slashes=False
)

# Registrar routers
app.include_router(scraping.router) 