import requests
from bs4 import BeautifulSoup
import pandas as pd
import unicodedata
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
from typing import List, Dict, Optional
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))  # Agregar directorio raíz al path
from config import MAX_TIMEOUT

logger = logging.getLogger(__name__)

class BaseScraper:
    def __init__(self):
        self.partial_results = []
        self.should_stop = False
        self.start_time = None
        self.timeout = MAX_TIMEOUT
        self.category_urls = {
            'pymes': 'pymes',
            'corporativos': 'corporativos',
            'casos de exito': 'empresarios-exitosos',
            'educacion financiera': 'educacion-financiera',
            'xepelin': 'noticias',
            'emprendedores': 'emprendedores'
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.setup_driver()

    def check_timeout(self) -> bool:
        """Verifica si se ha excedido el tiempo máximo"""
        if self.start_time and time.time() - self.start_time >= self.timeout:
            self.should_stop = True
            return True
        return False

    def setup_driver(self):
        """Configura el driver de Chrome con las opciones necesarias"""
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument(f'user-agent={self.headers["User-Agent"]}')
        self.chrome_options = chrome_options

    def normalize_text(self, text: str) -> str:
        """Normaliza el texto eliminando acentos y convirtiendo a minúsculas"""
        normalized = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
        return normalized.lower()

    def get_category_url(self, category: str) -> Optional[str]:
        """Obtiene la URL correspondiente a una categoría"""
        normalized_category = self.normalize_text(category)
        for cat, url_suffix in self.category_urls.items():
            if cat == normalized_category:
                return f"https://xepelin.com/blog/{url_suffix}"
        return None

    def get_all_articles(self, url: str) -> Optional[str]:
        """Obtiene el contenido HTML de todos los artículos de una página"""
        driver = None
        try:
            if self.check_timeout():
                return None

            logger.info(f"Accediendo a: {url}")
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.implicitly_wait(5) 
            driver.get(url)
            time.sleep(2) 
            
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1) 

            articles_loaded = 0
            last_height = driver.execute_script("return document.body.scrollHeight")

            while not self.check_timeout(): 
                try:
                    # Apreta el botón de "Cargar más" para obtener todos los artículos
                    load_more = WebDriverWait(driver, 5).until( 
                        EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Cargar más')]"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView();", load_more)
                    load_more.click()
                    articles_loaded += 1
                    
                    time.sleep(1)
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height

                except TimeoutException:
                    logger.info("No hay más artículos para cargar")
                    break
                except Exception as e:
                    logger.error(f"Error al cargar más artículos: {str(e)}")
                    break

            return driver.page_source

        except Exception as e:
            logger.error(f"Error en get_all_articles: {str(e)}")
            return None
        finally:
            if driver:
                driver.quit()

    def get_article_details(self, url: str) -> Optional[Dict]:
        """Obtiene los detalles de un artículo específico"""
        if self.check_timeout():
            return None
            
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Datos del artículo
            title = soup.find('h1', {'class': 'ArticleSingle_title__0DNjm'}).text.strip()
            category = soup.find('a', {'class': 'text-primary-main'}).text.strip()
            reading_time = soup.find('div', {'class': 'Text_body__snVk8'}).text.strip()
            
            # Datos del autor
            author_section = soup.find('div', {'class': 'flex gap-2'})
            author_info = author_section.text.strip().split('|')

            article_data = {
                'Titular': title,
                'Categoría': category,
                'URL': url,
                'Autor': author_info[0].strip(),
                'Cargo': author_info[1].strip(),
                'Tiempo de Lectura': reading_time
            }

            self.partial_results.append(article_data)
            return article_data

        except Exception as e:
            logger.error(f"Error obteniendo detalles del artículo {url}: {e}")
            return None

    def process_category(self, category: str) -> List[Dict]:
        """Procesa una categoría específica"""
        if self.check_timeout():
            return self.partial_results

        url = self.get_category_url(category)
        if not url:
            logger.error(f"URL no encontrada para la categoría: {category}")
            return self.partial_results

        try:
            page_source = self.get_all_articles(url)
            if not page_source:
                return self.partial_results

            soup = BeautifulSoup(page_source, 'html.parser')
            article_cards = soup.find_all('div', {'class': 'BlogArticle_box__JyD1X'})
            logger.info(f"Encontrados {len(article_cards)} artículos en {category}")

            for i, card in enumerate(article_cards, 1):
                if self.check_timeout():
                    logger.info(f"Timeout alcanzado después de procesar {i-1} artículos")
                    return self.partial_results

                try:
                    article_url = card.find('a')['href']
                    if not article_url.startswith('http'):
                        article_url = f"https://xepelin.com{article_url}"
                    
                    article_data = self.get_article_details(article_url)
                    if article_data:
                        logger.info(f"Artículo {i}/{len(article_cards)} procesado")

                except Exception as e:
                    logger.error(f"Error procesando artículo {i} de {category}: {e}")

            return self.partial_results

        except Exception as e:
            logger.error(f"Error procesando categoría {category}: {e}")
            return self.partial_results

    def scrape(self, category: str = None) -> List[Dict]:
        """Método principal para iniciar el scraping"""
        self.partial_results = []  # Reset results
        self.should_stop = False
        self.start_time = time.time()  # Iniciar el temporizador
        
        try:
            if category and self.normalize_text(category) == "todas las categorias":
                for cat in self.category_urls.keys():
                    if self.check_timeout(): 
                        break
                    logger.info(f"Procesando categoría: {cat}")
                    self.process_category(cat)
            else:
                self.process_category(category)

            return self.partial_results

        except Exception as e:
            logger.error(f"Error en scraping: {e}")
            return self.partial_results

if __name__ == "__main__":
    import argparse
    
    # Configurar el logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Crear el parser de argumentos
    parser = argparse.ArgumentParser(description='Ejecutar web scraping de Xepelin Blog')
    parser.add_argument(
        '--category', 
        type=str, 
        default='casos de exito',
        choices=['todas las categorias', 'pymes', 'corporativos', 'casos de exito', 
                'educacion financiera', 'xepelin', 'emprendedores'],
        help='Categoría a scrapear'
    )
    parser.add_argument(
        '--timeout', 
        type=int, 
        default=MAX_TIMEOUT,
        help=f'Tiempo máximo de ejecución en segundos (default: {MAX_TIMEOUT})'
    )

    args = parser.parse_args()

    try:
        # Iniciar el scraper
        scraper = BaseScraper()
        scraper.timeout = args.timeout
        
        # Ejecutar el scraping
        logger.info(f"Iniciando scraping para categoría: {args.category}")
        results = scraper.scrape(args.category)
        
        # Guardar resultados en un DataFrame
        if results:
            df = pd.DataFrame(results)
            filename = f"xepelin_articles_{int(time.time())}.csv"
            df.to_csv(f"../outputs/{filename}", index=False)
            logger.info(f"Resultados guardados en {filename}")
            logger.info(f"Total de artículos encontrados: {len(results)}")
        else:
            logger.warning("No se encontraron resultados")

    except KeyboardInterrupt:
        logger.info("Scraping interrumpido por el usuario")
    except Exception as e:
        logger.error(f"Error durante el scraping: {e}")
