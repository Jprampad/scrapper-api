import sys
from pathlib import Path

# Añadir el directorio raíz al path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from core.config import settings
import requests
from bs4 import BeautifulSoup
import pandas as pd
import unicodedata
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging
from typing import List, Dict, Optional
import asyncio
import aiohttp
from functools import lru_cache
import uvloop
from aiohttp import ClientTimeout
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

class UltraOptimizedScraper:
    def __init__(self):
        self.partial_results = []
        self.should_stop = False
        self.start_time = None
        self.timeout = settings.MAX_TIMEOUT
        self.url_cache = set()
        self.results_cache = {}
        self.category_urls = {
            'pymes': 'pymes',
            'corporativos': 'corporativos',
            'casos de exito': 'empresarios-exitosos',
            'educacion financiera': 'educacion-financiera',
            'xepelin': 'noticias',
            'emprendedores': 'emprendedores'
        }
        self.setup_driver()

    def setup_driver(self):
        """Configura el driver de Chrome con las opciones necesarias"""
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        chrome_options.page_load_strategy = 'eager'
        self.chrome_options = chrome_options

    def check_timeout(self) -> bool:
        """Verifica si se ha excedido el tiempo máximo"""
        if self.start_time and time.time() - self.start_time >= self.timeout:
            self.should_stop = True
            return True
        return False

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normaliza el texto eliminando acentos y convirtiendo a minúsculas"""
        return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII').lower()

    def get_category_url(self, category: str) -> Optional[str]:
        """Obtiene la URL correspondiente a una categoría"""
        normalized_category = self.normalize_text(category)
        url_suffix = self.category_urls.get(normalized_category)
        return f"https://xepelin.com/blog/{url_suffix}" if url_suffix else None

    async def get_article_details(self, session: aiohttp.ClientSession, url: str, semaphore: asyncio.Semaphore) -> Optional[Dict]:
        if url in self.url_cache:
            return self.results_cache.get(url)
        
        async with semaphore:
            try:
                timeout = ClientTimeout(total=10)
                async with session.get(url, timeout=timeout) as response:
                    if response.status != 200:
                        return None
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    
                    data = {
                        'Titular': soup.find('h1', {'class': 'ArticleSingle_title__0DNjm'}).text.strip(),
                        'Categoría': soup.find('a', {'class': 'text-primary-main'}).text.strip(),
                        'URL': url
                    }
                    
                    author_section = soup.find('div', {'class': 'flex gap-2'})
                    if author_section:
                        author_info = author_section.text.strip().split('|')
                        data.update({
                            'Autor': author_info[0].strip(),
                            'Cargo': author_info[1].strip() if len(author_info) > 1 else ''
                        })
                    
                    reading_time = soup.find('div', {'class': 'Text_body__snVk8'})
                    if reading_time:
                        data['Tiempo de Lectura'] = reading_time.text.strip()
                    
                    self.url_cache.add(url)
                    self.results_cache[url] = data
                    return data
                    
            except Exception as e:
                logger.error(f"Error procesando {url}: {e}")
                return None

    async def process_articles(self, urls: List[str]) -> List[Dict]:
        semaphore = asyncio.Semaphore(10)
        connector = aiohttp.TCPConnector(limit=None, ttl_dns_cache=300)
        timeout = ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = []
            for url in urls:
                task = asyncio.create_task(self.get_article_details(session, url, semaphore))
                def callback(task):
                    try:
                        if not task.cancelled() and task.exception() is None:
                            result = task.result()
                            if result:
                                self.partial_results.append(result)
                    except Exception:
                        pass
                
                task.add_done_callback(callback)
                tasks.append(task)
                
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                valid_results = [r for r in results 
                               if r is not None 
                               and isinstance(r, dict) 
                               and not isinstance(r, Exception)]
                return valid_results
            except asyncio.CancelledError:
                logger.info(f"Proceso cancelado. Retornando {len(self.partial_results)} resultados parciales")
                return [r for r in self.partial_results if r is not None]
            finally:
                for task in tasks:
                    if not task.done():
                        task.cancel()

    def get_all_articles(self, url: str) -> Optional[str]:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        chrome_options.page_load_strategy = 'eager'
        
        service = Service(ChromeDriverManager().install())
        
        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_script_timeout(5)
            driver.implicitly_wait(3)
            
            driver.get(url)
            time.sleep(2)
            
            last_height = driver.execute_script("return document.body.scrollHeight")
            
            while True:
                try:
                    load_more = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Cargar más')]"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView(); arguments[0].click();", load_more)
                    
                    time.sleep(0.5)
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                    
                except TimeoutException:
                    break
                    
            return driver.page_source
            
        finally:
            if 'driver' in locals():
                driver.quit()

    async def process_category(self, category: str) -> List[Dict]:
        logger.info(f"\nIniciando procesamiento de categoría: {category}")
        url = self.get_category_url(category)
        if not url:
            return []
        
        try:
            loop = asyncio.get_event_loop()
            page_source = await loop.run_in_executor(None, self.get_all_articles, url)
            
            if not page_source:
                return []
            
            soup = BeautifulSoup(page_source, 'lxml')
            article_cards = soup.find_all('div', {'class': 'BlogArticle_box__JyD1X'})
            logger.info(f"Encontrados {len(article_cards)} artículos en {category}")
            
            urls = [
                f"https://xepelin.com{card.find('a')['href']}" 
                if not card.find('a')['href'].startswith('http') 
                else card.find('a')['href']
                for card in article_cards
            ]
            
            return await self.process_articles(urls)
            
        except Exception as e:
            logger.error(f"Error en categoría {category}: {e}")
            return []

    async def scrape_async(self, category: str) -> Optional[List[Dict]]:
        self.partial_results = []
        self.should_stop = False
        
        try:
            if self.normalize_text(category) == "todas las categorias":
                categories = list(self.category_urls.keys())
                tasks = [self.process_category(cat) for cat in categories]
                try:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    all_articles = []
                    for result in results:
                        if isinstance(result, list):
                            all_articles.extend(result)
                    return all_articles if all_articles else self.partial_results
                except asyncio.TimeoutError:
                    logger.info(f"Timeout en todas las categorías. Retornando {len(self.partial_results)} resultados parciales")
                    return self.partial_results
            else:
                try:
                    results = await self.process_category(category)
                    return results if results else self.partial_results
                except asyncio.TimeoutError:
                    self.should_stop = True
                    logger.info(f"Timeout en categoría {category}. Retornando {len(self.partial_results)} resultados parciales")
                    return self.partial_results
        except Exception as e:
            self.is_partial = True
            logger.error(f"Error en scraping: {e}")
            return self.partial_results

    def scrape(self, category: str) -> Optional[List[Dict]]:
        try:
            uvloop.install()
        except Exception:
            logger.warning("uvloop no disponible, usando el loop por defecto")
        
        try:
            return asyncio.run(self.scrape_async(category))
        except asyncio.TimeoutError:
            logger.info(f"Timeout en scrape. Retornando {len(self.partial_results)} resultados parciales")
            return self.partial_results

def scrape_xepelin_blog(category: str) -> Optional[List[Dict]]:
    scraper = UltraOptimizedScraper()
    return scraper.scrape(category)

if __name__ == "__main__":
    import argparse
    import json
    from datetime import datetime
    
    # Configurar el logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Crear el parser de argumentos
    parser = argparse.ArgumentParser(description='Ejecutar web scraping ultra optimizado de Xepelin Blog')
    parser.add_argument(
        '-c', '--category', 
        type=str, 
        default='casos de exito',
        choices=['todas', 'pymes', 'corporativos', 'casos de exito', 
                'educacion financiera', 'xepelin', 'emprendedores'],
        help='Categoría a scrapear (usa "todas" para todas las categorías)'
    )
    parser.add_argument(
        '-t', '--timeout', 
        type=int, 
        default=settings.MAX_TIMEOUT,
        help=f'Tiempo máximo de ejecución en segundos (default: {settings.MAX_TIMEOUT})'
    )

    args = parser.parse_args()

    try:
        # Iniciar el scraper y registrar tiempo de inicio
        start_time = time.time()
        scraper = UltraOptimizedScraper()
        scraper.timeout = args.timeout
        
        # Convertir 'todas' a 'todas las categorias' para mantener compatibilidad
        category = 'todas las categorias' if args.category == 'todas' else args.category
        
        # Ejecutar el scraping
        logger.info(f"Iniciando scraping ultra optimizado para categoría: {category}")
        results = scraper.scrape(category)
        
        # Calcular tiempo de ejecución
        execution_time = time.time() - start_time
        
        # Preparar los resultados
        if results:
            # Crear estructura del JSON
            output_data = {
                "metadata": {
                    "fecha_ejecucion": datetime.now().isoformat(),
                    "categoria": args.category,
                    "total_articulos": len(results),
                    "tiempo_ejecucion": {
                        "segundos": round(execution_time, 2),
                        "formato_legible": f"{int(execution_time // 60)} minutos {int(execution_time % 60)} segundos"
                    }
                },
                "articulos": results
            }

            # Si se procesaron todas las categorías, agregar estadísticas
            if args.category == 'todas':
                category_counts = {}
                for article in results:
                    cat = article['Categoría']
                    category_counts[cat] = category_counts.get(cat, 0) + 1
                output_data["metadata"]["estadisticas_categorias"] = category_counts
                
                # Mostrar estadísticas en consola
                logger.info("\nDesglose por categoría:")
                for cat, count in category_counts.items():
                    logger.info(f"{cat}: {count} artículos")

            # Guardar resultados en JSON
            category_name = args.category.replace(' ', '_')
            filename = f"xepelin_articles_{category_name}_{int(time.time())}.json"
            filepath = f"../outputs/{filename}"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Resultados guardados en {filename}")
            logger.info(f"Total de artículos encontrados: {len(results)}")
            logger.info(f"Tiempo de ejecución: {output_data['metadata']['tiempo_ejecucion']['formato_legible']}")
        else:
            logger.warning("No se encontraron resultados")

    except KeyboardInterrupt:
        logger.info("Scraping interrumpido por el usuario")
    except Exception as e:
        logger.error(f"Error durante el scraping: {e}")