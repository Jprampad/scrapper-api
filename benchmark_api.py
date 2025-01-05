import requests
import time
import csv
from datetime import datetime
import json
import asyncio
import pandas as pd

API_URL = "http://localhost:8000/scraping"
WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/11217441/bfemddr"
CATEGORIES = ["todas las categorias"]
MODELS = ["base"]

async def wait_for_completion(job_id: str, timeout: int = 1500) -> dict:
    """Espera a que el job se complete y retorna los resultados"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = requests.get(f"{API_URL}/status/{job_id}")
        data = response.json()
        
        if data["status"] in ["completed", "partial", "error"]:
            return data
        
        await asyncio.sleep(2)
    
    raise TimeoutError(f"Job {job_id} no completó en {timeout} segundos")

async def run_benchmark():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = []

    for model in MODELS:
        for category in CATEGORIES:
            print(f"\nEjecutando benchmark para {model} - {category}")
            
            # Iniciar job
            response = requests.post(API_URL, json={
                "category": category,
                "model": model,
                "webhook": WEBHOOK_URL,
                "email": "jpramirez5@uc.cl"
            })
            
            if response.status_code != 200:
                print(f"Error al iniciar job: {response.json()}")
                continue
            
            job_id = response.json()["job_id"]
            print(f"Job iniciado: {job_id}")
            
            try:
                # Esperar resultados
                job_result = await wait_for_completion(job_id)
                
                result = {
                    "timestamp": timestamp,
                    "model": model,
                    "category": category,
                    "duration": round(float(job_result.get("duration", 0)), 2),
                    "articles_count": job_result.get("articles_count", 0),
                    "status": job_result.get("status", "unknown")
                }
                
                results.append(result)
                print(f"Completado: {result}")
                
            except Exception as e:
                print(f"Error en job {job_id}: {str(e)}")
                results.append({
                    "timestamp": timestamp,
                    "model": model,
                    "category": category,
                    "duration": 0,
                    "articles_count": 0,
                    "status": "error"
                })
    
    # Guardar resultados
    csv_file = f"outputs/benchmark_results_{timestamp}.csv"
    df = pd.DataFrame(results)
    df.to_csv(csv_file, index=False)
    print(f"\nResultados guardados en {csv_file}")
    
    # Crear tabla comparativa
    pivot = df.pivot_table(
        index='category',
        columns='model',
        values=['duration', 'articles_count'],
        aggfunc='mean'
    )
    
    comparison_file = f"outputs/benchmark_comparison_{timestamp}.csv"
    pivot.to_csv(comparison_file)
    print(f"Comparación guardada en {comparison_file}")
    
    # Mostrar resumen
    print("\nResumen de resultados:")
    print(pivot)

if __name__ == "__main__":
    asyncio.run(run_benchmark()) 