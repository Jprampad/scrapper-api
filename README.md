# 🕷️ Blog Scraper API

API REST para extraer artículos del blog de forma asíncrona y escalable construido con FastApi.

## 🚀 Características

- ✨ Scraping asíncrono de artículos
- 📊 Cola de trabajos con estado
- 📝 Exportación a Google Sheets
- 🔔 Notificaciones vía webhook
- 📱 Documentación interactiva 

## 🛠️ Requisitos

- Python 3.9+
- pip
- virtualenv (opcional pero recomendado)

### 🚀 Request básica (solo parámetros requeridos)
curl -X POST http://127.0.0.1:8000/scraping \
     -H "Content-Type: application/json" \
     -d '{
          "category": "xepelin",
          "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr"
        }'

### ✨ Request completa (con parámetros opcionales)
curl -X POST http://127.0.0.1:8000/scraping \
     -H "Content-Type: application/json" \
     -d '{
          "category": "xepelin",
          "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr",
          "email": "jpramirez5@uc.cl",    # 📧 Opcional (default: jpramirez5@uc.cl)
          "model": "base"                  # 🔧 Opcional (default: ultra)
        }'