import pandas as pd
from typing import List, Dict
import logging
from pathlib import Path

class ExcelHandler:
    """
    Håndterer læsning og validering af Excel filer med PDF URLs.
    
    Attributes:
        file_path (str): Sti til Excel filen
        required_columns (List[str]): Liste af påkrævede kolonner
    """
    
    def __init__(self, file_path: str):
        """
        Initialiserer ExcelHandler.
        
        Args:
            file_path (str): Sti til Excel filen
        """
        self.file_path = Path(file_path)
        self.data = None
        self.required_columns = ['Pdf_URL', 'BRnum']  # Minimum påkrævede kolonner
        self._read_excel()
        
    def _read_excel(self) -> None:
        """
        Læser Excel filen og validerer grundlæggende struktur.
        
        Raises:
            FileNotFoundError: Hvis Excel filen ikke findes
            ValueError: Hvis filen ikke kan læses som Excel
        """
        try:
            self.data = pd.read_excel(self.file_path)
            logging.info(f"Successfully read Excel file: {self.file_path}")
        except FileNotFoundError:
            logging.error(f"Excel file not found: {self.file_path}")
            raise
        except Exception as e:
            logging.error(f"Error reading Excel file: {e}")
            raise ValueError(f"Could not read Excel file: {e}")

    def validate_columns(self) -> bool:
        """
        Validerer at alle påkrævede kolonner findes i Excel filen.
        
        Returns:
            bool: True hvis alle påkrævede kolonner findes
        
        Raises:
            ValueError: Hvis påkrævede kolonner mangler
        """
        missing_columns = [col for col in self.required_columns if col not in self.data.columns]
        
        if missing_columns:
            error_msg = f"Missing required columns: {', '.join(missing_columns)}"
            logging.error(error_msg)
            raise ValueError(error_msg)
        
        return True

    def get_urls(self) -> List[Dict]:
        """
        Henter URL data fra Excel filen.
        
        Returns:
            List[Dict]: Liste af dictionaries med URL information:
                {
                    'br_number': str,
                    'primary_url': str,
                    'alternative_url': str (optional)
                }
        """
        self.validate_columns()
        
        # Fjern rækker uden primær URL
        valid_data = self.data.dropna(subset=['Pdf_URL'])
        
        urls = []
        for _, row in valid_data.iterrows():
            url_info = {
                'br_number': str(row['BRnum']),
                'primary_url': str(row['Pdf_URL']),
                'alternative_url': str(row.get('Report HTML address', ''))  # Alternativ URL hvis tilgængelig
            }
            urls.append(url_info)
            
        logging.info(f"Found {len(urls)} valid URLs to process")
        return urls

    def _validate_data(self) -> None:
        """
        Udfører detaljeret validering af data.
        Kan udvides med flere valideringer efter behov.
        """
        # Tjek for duplikerede BR numre
        duplicates = self.data['BRnum'].duplicated()
        if duplicates.any():
            logging.warning(f"Found {duplicates.sum()} duplicate BR numbers")
        
        # Tjek for tomme URLs
        empty_urls = self.data['Pdf_URL'].isna().sum()
        if empty_urls > 0:
            logging.warning(f"Found {empty_urls} rows with missing primary URLs")