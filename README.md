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
  - Mantiene orden de ejecución
- 📁 Archivo: `scrapper_optimized.py`

### 3. Ultra Scraper (Asíncrono)

- ⚡ Procesamiento asíncrono con asyncio y aiohttp
- 🏃 15.7x más rápido que el base
- 🔥 Ideal para grandes volúmenes
- 📝 Características avanzadas:
  - Cache de URLs y resultados
  - Semáforos para control de concurrencia
  - Timeouts configurables
  - Manejo de errores robusto
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
| Manejo de errores     | Básico   | Medio     | Avanzado |
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
# Google Service Account Credentials
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"xepelin-parte-2","private_key_id":"c6ef5d54450cff5aba8c19fcb29d8207bdce3d9f","private_key":"-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCg4qOYxB9ceZjm\n6XjINIgMwVsbGydTCx7B4xrIjc+lZ9MQrsXsvEozekq7o001yGNJXZmiYrAS7j87\nPOocfzbuwYCO5GoDkrKKo2FDQFJPZVaBGKMdZwb80OAQTD2ykN6J2/3/M2b5m0kd\nLy1so6JnzVOwO6XU/Saewhvebv/c6yI9ZojYMf9NK0DZpmjNaDPT6bFGcFe0Nh+W\nsdgwjpLYKNwpODIxZnmxyMmMW7ecsXCcHugJFaPfxdiknUGp5CG+jXSKfAfmqJwc\ni3Zv0eMIHJIOvFc57gnaYB/v3dmNFP2OOvZzmnBcoRSOqXQgYV6GCZzjNkmyx/Ba\nRIyIUXCDAgMBAAECggEAGVaIYGtm6wgFkjxr9s/7K1Mad6LnpxcFwZB0a+iVrt2y\nqppz9oxS/VeBxJp78v/7zxasNxxm0ZxvHfPChTlt291i015a6fQlJVuE2nQbYoC5\nxnwsWFmdCp0U5Mw1HVXejoS0tIgSbDZOJggDlewRjFqUlxlVzT0PY4p7nCUMK+0m\nRJo4c0hgIqxadCrXPmRCNX+8+g41m3lStZ0mk3rBlJfhwNc+jGJS6gmZ2C1TMa9T\n6emR98Jup64ymmkp1uBNkJ4TFZOKSPuqhrKpdHJbqsREJjuiyyYCEiqsD0r174xz\nPnQcHHHcUyaJItHwuX3vjWDbJNBv4LbAgEb03UXRwQKBgQDV2jWPw3Q+YuhOGxGZ\nQjUDPuYwkgjY+h/LcaAHrUpvhv9dJo4jBaWkQjxoaGklVTL65rIaZckcbPkeTyDJ\n9ri0MDnwBGDDccLeXeDyZxeyWehN56vvi1IDWZYJnYbTbFhSKHXJWVgumE4deY9u\n5gxeTeI6jtQcB5tJ1nKqg7NLQQKBgQDAmAI7LgtQNfvva58n1dGKGcVZGZ56dNC3\nNTthAmu721NtwTKpjS5XmmtVOnB1zj72c/irB7PL/NRvN3GSsk93s8MmLvWiBhr9\n/KSiPa98KgILBRPTvWvqUrAQS6SJ7bu4QpQ22UB9PkT+g66fwxobIoDiO336MxO3\n8CJDvA2ewwKBgQChQ70yXXUyeomuJLF/vjKV8P/LTsTHQs9pLpU8VMyWD9pQV3vG\nI0MG/D/riBkKYxZfqEpUp78h5XdzCL60Lo6Yqul1+wcxO391CpxQj7eJ8kzBOtwo\ndwpwpkUDmTwMAV8VDZfNL8fU01vM1Fd6jJZ1IwxflkeTn5TV+JZdyZUSQQKBgQC4\nZ1OLknSmomnNPkCvhZ0SG8bHny4MlhjZspBePFEnF8N0DU4S5ej/XA11F3Vids32\nb+gi6kcPA8/rhSyrhytrs6UgxEnQjwP9OI/yABosSpSWNJBdZrsTK4UEtUigAA6D\nSMxdD/sdcCfjgfYLZmVyocDB3LCshYdV0QkdzctEvQKBgQDFT3c00x5heKdWysMu\n5WzGV6BzrbP7R3EIuv5qYN1f9zV1pIzkgiAzhcQgl9JaR09hcOy8kQGFLg1Ptlla\n00pus3rbxZrMC+IHstYLVhoxW59h+RassCop3gGUTRHyJads6JZybSOO6U4sIStv\nuKsnvczt4TqunuLQNdGEu7/3Tg==\n-----END PRIVATE KEY-----\n","client_email":"xepelin-parte-2-177@xepelin-parte-2.iam.gserviceaccount.com","client_id":"112856121094952099784","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/xepelin-parte-2-177%40xepelin-parte-2.iam.gserviceaccount.com","universe_domain":"googleapis.com"}

# Google Sheets Configuration
GOOGLE_SPREADSHEET_ID=1wlaiJhF07N0GAHYUi2Iq0wtd3uY_w4xHbbDbqX1FTMk

# Google Sheets Service Configuration
GOOGLE_SHEETS_MAX_WORKERS=3

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