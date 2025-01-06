from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from routers import scraping

load_dotenv()

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

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(scraping.router) 

@app.get("/")
async def root():
    try:
        # Verificar variables de entorno
        if not os.getenv("GOOGLE_CREDENTIALS_JSON"):
            raise HTTPException(status_code=500, detail="Google credentials not configured")
        if not os.getenv("GOOGLE_SPREADSHEET_ID"):
            raise HTTPException(status_code=500, detail="Spreadsheet ID not configured")
            
        return {"message": "API is running, check /docs for more information"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))