import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any
from api.core.logging import logger
from api.models.jobs import ScrapingJob
from pathlib import Path
import time

class GoogleSheetsService:
    def __init__(self):
        self.client = self._setup_client()
        self.spreadsheet_id = '1wlaiJhF07N0GAHYUi2Iq0wtd3uY_w4xHbbDbqX1FTMk'  # ID específico de la spreadsheet

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

    def save_job_results(self, job: ScrapingJob) -> bool:
        """
        Guarda los resultados del job en Google Sheets
        
        Args:
            job: Instancia de ScrapingJob con los resultados
        Returns:
            bool: True si fue exitoso, False si hubo error
        """
        try:
            spreadsheet = self._get_spreadsheet()
            
            # Crear nombre de la hoja con el nuevo formato
            timestamp = int(time.time())
            worksheet_title = f"xepelin_{job.model}_{job.category}_{timestamp}"

            # Crear nueva hoja
            try:
                worksheet = spreadsheet.add_worksheet(
                    title=worksheet_title,
                    rows=len(job.results) + 1,  # Encabezados + filas de datos
                    cols=6
                )
            except gspread.exceptions.APIError as e:
                logger.error(f"Error al crear la hoja: {str(e)}")
                return False

            # Agregar encabezados
            headers = [
                'Titular',
                'Categoría',
                'Autor',
                'Cargo',
                'Tiempo de Lectura',
                'URL'
            ]
            worksheet.append_row(headers)

            # Agregar filas de datos
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
                    worksheet.append_row(row)

            logger.info(f"Resultados del job guardados en la hoja: {worksheet_title}")
            return True

        except Exception as e:
            logger.error(f"Error al guardar en Google Sheets: {str(e)}")
            return False

# Crear instancia singleton del servicio
sheets_service = GoogleSheetsService() 