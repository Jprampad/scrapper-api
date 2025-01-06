# 🕷️ Blog Scraper API

API REST para extraer artículos del blog de forma asíncrona y escalable.

## 🚀 Características

- ✨ Scraping asíncrono de artículos
- 📊 Cola de trabajos con estado
- 📝 Exportación a Google Sheets
- 🔔 Notificaciones vía webhook
- 📱 Documentación interactiva con Swagger

## 🤖 Modelos de Scraping

### 1. Base Scraper (Secuencial)

- 🔄 Procesamiento secuencial de artículos uno por uno
- 🎯 Usa Selenium para cargar páginas dinámicamente
- ⚡ Menor consumo de recursos y memoria
- 📝 Características:
  - Procesamiento lineal
  - Sin concurrencia
  - Ideal para pocas páginas (<15 artículos)
- 📁 Archivo: `scrapper.py`

### 2. Optimized Scraper (Concurrente)

- 🔄 Procesamiento concurrente con ThreadPoolExecutor
- 🚀 2.4x más rápido que el base
- 💪 Mejor manejo de múltiples artículos
- 📝 Características:
  - Múltiples threads simultáneos
  - Pool de 5 workers
  - Ideal para volumen medio (15-100 artículos)
- 📁 Archivo: `scrapper_optimized.py`

### 3. Ultra Scraper (Asíncrono)

- ⚡ Procesamiento asíncrono con asyncio y aiohttp
- 🏃 15.7x más rápido que el base
- 🔥 Ideal para grandes volúmenes
- 📝 Características avanzadas:
  - Cache de URLs y resultados
  - Semáforos para control de concurrencia
  - Timeouts configurables
  - uvloop para mejor rendimiento
  - Ideal para grandes volúmenes (>100 artículos)
- 📁 Archivo: `scrapper_ultra_optimized.py`

## 📊 Comparativa de Rendimiento

| Característica          | Base     | Optimized | Ultra    |
|------------------------|----------|-----------|----------|
| Tipo de procesamiento  | Secuencial| Concurrente| Asíncrono|
| Velocidad relativa     | 1x       | 2.4x      | 15.7x    |
| Uso de memoria        | Bajo     | Medio     | Alto     |
| Complejidad           | Simple   | Media     | Alta     |
| Artículos recomendados| <15      | 15-100    | >100     |
| Cache                 | No       | No        | Sí       |

## 📊 Rendimiento por Modelo

La siguiente tabla muestra el tiempo de ejecución (en segundos) para cada modelo de scraping según la categoría:

| Categoría             | Artículos | Base   | Optimized | Ultra  | Mejora |
|----------------------|-----------|--------|-----------|--------|--------|
| Todas las categorías | 406       | 400.50 | 164.25    | 25.39  | 93.66% |
| Pymes                | 139       | 134.15 | 51.33     | 24.37  | 81.83% |
| Corporativos         | 114       | 110.49 | 43.93     | 20.50  | 81.45% |
| Educación Financiera | 80        | 83.18  | 30.88     | 16.16  | 80.57% |
| Emprendedores        | 32        | 42.45  | 17.69     | 10.05  | 76.33% |
| Xepelin              | 27        | 31.33  | 17.64     | 9.62   | 69.29% |
| Casos de Éxito       | 14        | 21.67  | 12.69     | 8.29   | 61.74% |

## 🛠️ Requisitos

- Python 3.9+
- pip
- virtualenv (opcional pero recomendado)

### 🚀 Request básica (solo parámetros requeridos)

curl -X POST http://127.0.0.1:8000/scraping
    -H "Content-Type: application/json"
    -d '{
          "category": "xepelin",
          "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr"
        }'

### ✨ Request completa (con parámetros opcionales)

curl -X POST http://127.0.0.1:8000/scraping
    -H "Content-Type: application/json"
    -d '{
          "category": "xepelin",
          "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr",
          "email": "jpramirez5@uc.cl",
          "model": "base"
        }'

## 🚀 Instalación y Ejecución

### Paso 1: Clonar el repositorio
``` bash
git clone https://github.com/usuario/scraper-api.git
cd scraper-api
```

### Paso 2: Crear y activar entorno virtual

En Windows:
``` bash
python -m venv venv
.\venv\Scripts\activate
```

En macOS/Linux:
``` bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar dependencias
``` bash
bash
pip install -r requirements.txt
```

### Paso 4: Configurar variables de entorno
1. Crea un archivo `.env` en la raíz del proyecto
2. Añade las siguientes variables:

``` env
Solicitar variables
DEBUG=true
```

### Paso 5: 🏃‍♂️ Ejecutar la API


Iniciar servidor de desarrollo
``` bash
uvicorn main:app --reload
```
```
La API estará disponible en:
http://localhost:8000
Documentación: http://localhost:8000/docs
```