from fastapi import FastAPI
from routers import scraping

app = FastAPI(
    title="Xepelin Blog Scraper API",
    description="""
# 🤖 API para hacer scraping del blog de Xepelin

## ✨ Características

* 🔄 Scraping asíncrono de artículos del blog
* 🚀 Múltiples modelos de scraping (base, optimized, ultra)
* 📬 Notificaciones vía webhook
* 📊 Resultados exportados a Google Sheets

## 🔍 Flujo de uso

1. Inicia un trabajo de scraping con POST /scraping
2. Obtén el estado del trabajo con GET /scraping/status/{job_id}
3. Recibirás una notificación vía webhook cuando el trabajo termine

## 🛠️ Modelos disponibles

| Modelo | Descripción |
|--------|-------------|
| base | Scraping básico secuencial |
| optimized | Scraping optimizado con concurrencia |
| ultra | Scraping optimizado con funciones asíncronas |
    """,
    version="1.0.0"
)

# Registrar routers
app.include_router(scraping.router) 

@app.get("/")
async def root():
    return {"message": "API is running, check /docs for more information"}