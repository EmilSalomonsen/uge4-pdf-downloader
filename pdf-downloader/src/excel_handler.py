import pandas as pd
from typing import List, Dict, Any
import logging
from pathlib import Path

class ExcelHandler:
    """
    Håndterer læsning og validering af Excel filer med PDF URLs.
    
    Attributes:
        excel_file_path (str): Sti til Excel filen
        required_columns (List[str]): Liste af påkrævede kolonner
    """
    
    def __init__(self, excel_file_path: str):
        """
        Initialiserer ExcelHandler.
        
        Args:
            excel_file_path (str): Sti til Excel filen
        """
        self.excel_file_path = excel_file_path
        self.required_columns = ['BRnum', 'Pdf_URL', 'Report Html Address']
        self.df = None
        self._read_excel()
        
    def _read_excel(self) -> None:
        """
        Læser Excel filen og validerer grundlæggende struktur.
        
        Raises:
            FileNotFoundError: Hvis Excel filen ikke findes
            ValueError: Hvis filen ikke kan læses som Excel
        """
        try:
            self.df = pd.read_excel(self.excel_file_path)
            logging.info(f"Successfully read Excel file: {self.excel_file_path}")
            self._validate_columns()
        except FileNotFoundError:
            logging.error(f"Excel file not found: {self.excel_file_path}")
            raise
        except Exception as e:
            logging.error(f"Error reading Excel file: {e}")
            raise ValueError(f"Could not read Excel file: {e}")

    def _validate_columns(self) -> None:
        """
        Validerer at alle påkrævede kolonner findes i Excel filen.
        
        Raises:
            ValueError: Hvis påkrævede kolonner mangler
        """
        missing_columns = [col for col in self.required_columns if col not in self.df.columns]
        
        if missing_columns:
            error_msg = f"Missing required columns: {', '.join(missing_columns)}"
            logging.error(error_msg)
            raise ValueError(error_msg)
        
        return True

    def get_urls(self) -> List[Dict[str, str]]:
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
        if self.df is None:
            self._read_excel()

        urls = []
        for _, row in self.df.iterrows():
            primary_url = row['Pdf_URL']
            alternative_url = row['Report Html Address']
            br_number = row['BRnum']

            if pd.isna(primary_url) and pd.isna(alternative_url):
                continue

            url_info = {
                'primary_url': str(primary_url) if not pd.isna(primary_url) else None,
                'alternative_url': str(alternative_url) if not pd.isna(alternative_url) else None,
                'br_number': str(br_number)
            }
            urls.append(url_info)

        if not urls:
            raise ValueError("Ingen gyldige URLs fundet i Excel filen")

        logging.info(f"Found {len(urls)} valid URLs to process")
        return urls

    def generate_metadata(self, download_results: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Genererer metadata i samme format som Metadata2006_2016.xlsx.
        
        Args:
            download_results (List[Dict]): Liste af download resultater
            
        Returns:
            pd.DataFrame: DataFrame med metadata i samme format som Metadata2006_2016
        """
        if self.df is None:
            self._read_excel()

        # Opret en kopi af original data
        metadata_df = self.df.copy()
        
        # Tilføj download status kolonne (AT)
        metadata_df['Download Status'] = 'Ikke downloadet'  # Default status
        
        # Opdater status baseret på download resultater
        for result in download_results:
            br_number = result['br_number']
            success = result.get('success', False)
            if success:
                metadata_df.loc[metadata_df['BRnum'] == br_number, 'Download Status'] = 'Downloadet'
        
        return metadata_df

    def save_metadata(self, metadata_df: pd.DataFrame, output_path: str) -> None:
        """
        Gemmer metadata til en ny Excel fil.
        
        Args:
            metadata_df (pd.DataFrame): DataFrame med metadata
            output_path (str): Sti hvor metadata skal gemmes
        """
        try:
            metadata_df.to_excel(output_path, index=False)
            logging.info(f"Saved metadata to: {output_path}")
        except Exception as e:
            logging.error(f"Error saving metadata: {e}")
            raise

    def _validate_data(self) -> None:
        """
        Udfører detaljeret validering af data.
        """
        # Tjek for duplikerede BR numre
        duplicates = self.df['BRnum'].duplicated()
        if duplicates.any():
            logging.warning(f"Found {duplicates.sum()} duplicate BR numbers")
        
        # Tjek for tomme URLs
        empty_urls = self.df['Pdf_URL'].isna().sum()
        if empty_urls > 0:
            logging.warning(f"Found {empty_urls} rows with missing primary URLs")