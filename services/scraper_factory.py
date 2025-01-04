from typing import Union
from models.requests import ScraperModel
from scrappers.scrapper import BaseScraper
from scrappers.scrapper_optimized import OptimizedScraper
from scrappers.scrapper_ultra_optimized import UltraOptimizedScraper

class ScraperFactory:
    def __init__(self):
        self._scrapers = {
            ScraperModel.BASE: BaseScraper,
            ScraperModel.OPTIMIZED: OptimizedScraper,
            ScraperModel.ULTRA: UltraOptimizedScraper
        }

    def get_scraper(
        self, 
        model: ScraperModel
    ) -> Union[BaseScraper, OptimizedScraper, UltraOptimizedScraper]:
        scraper_class = self._scrapers.get(model)
        if not scraper_class:
            raise ValueError(f"Modelo de scraper no válido: {model}")
        return scraper_class()