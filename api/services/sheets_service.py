import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any
from api.core.logging import logger
from api.models.jobs import ScrapingJob
from pathlib import Path
import time
from tenacity import retry, stop_after_attempt, wait_exponential
import asyncio
from concurrent.futures import ThreadPoolExecutor

class GoogleSheetsService:
    def __init__(self):
        self.client = self._setup_client()
        self.spreadsheet_id = '1wlaiJhF07N0GAHYUi2Iq0wtd3uY_w4xHbbDbqX1FTMk'
        self._executor = ThreadPoolExecutor(max_workers=3)

    def _setup_client(self) -> gspread.Client:
        """Inicializa el cliente de Google Sheets con las credenciales"""
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        
        credentials_path = Path('api/xepelin-parte-2-c6ef5d54450c.json')
        credentials = Credentials.from_service_account_file(
            str(credentials_path),
            scopes=scopes
        )
        
        return gspread.authorize(credentials)

    def _get_spreadsheet(self) -> gspread.Spreadsheet:
        """Obtiene la hoja de cálculo por ID"""
        try:
            return self.client.open_by_key(self.spreadsheet_id)
        except gspread.SpreadsheetNotFound:
            raise Exception(f"No se encontró la hoja de cálculo con ID: {self.spreadsheet_id}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def _batch_update(self, worksheet: gspread.Worksheet, values: List[List[str]]):
        """
        Actualiza múltiples filas de una vez
        """
        if values:
            worksheet.append_rows(values)
            time.sleep(1)

    async def save_job_results(self, job: ScrapingJob) -> bool:
        """
        Guarda los resultados del job en Google Sheets de manera asíncrona
        
        Args:
            job: Instancia de ScrapingJob con los resultados
        Returns:
            bool: True si fue exitoso, False si hubo error
        """
        try:
            loop = asyncio.get_running_loop()
            
            # Obtener spreadsheet en thread separado
            spreadsheet = await loop.run_in_executor(
                self._executor, 
                self._get_spreadsheet
            )
            
            timestamp = int(time.time())
            worksheet_title = f"xepelin_{job.model}_{job.category}_{timestamp}"

            # Crear worksheet en thread separado
            try:
                worksheet = await loop.run_in_executor(
                    self._executor,
                    lambda: spreadsheet.add_worksheet(
                        title=worksheet_title,
                        rows=len(job.results) + 1,
                        cols=6
                    )
                )
            except gspread.exceptions.APIError as e:
                logger.error(f"Error al crear la hoja: {str(e)}")
                return False

            # Preparar todos los datos en una lista
            all_rows = [
                ['Titular', 'Categoría', 'Autor', 'Cargo', 'Tiempo de Lectura', 'URL']
            ]

            if job.results:
                for article in job.results:
                    row = [
                        article['Titular'],
                        article['Categoría'],
                        article['Autor'],
                        article['Cargo'],
                        article['Tiempo de Lectura'],
                        article['URL']
                    ]
                    all_rows.append(row)

            # Hacer el batch update en thread separado
            await loop.run_in_executor(
                self._executor,
                lambda: self._batch_update(worksheet, all_rows)
            )

            logger.info(f"Resultados del job guardados en la hoja: {worksheet_title}")
            return True

        except Exception as e:
            logger.error(f"Error al guardar en Google Sheets: {str(e)}")
            return False

    def __del__(self):
        """Cleanup del executor al destruir la instancia"""
        self._executor.shutdown(wait=False)

# Crear instancia singleton del servicio
sheets_service = GoogleSheetsService() 