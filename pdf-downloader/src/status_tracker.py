import pandas as pd
from pathlib import Path
import logging
from typing import List, Dict
from datetime import datetime

class StatusTracker:
    """
    Holder styr på download status og genererer rapporter.
    
    Attributes:
        report_dir (str): Sti hvor rapporter gemmes
        results (List[Dict]): Liste af download resultater
    """
    
    def __init__(self, report_dir: str):
        """
        Initialiserer StatusTracker.
        
        Args:
            report_dir (str): Sti hvor rapporter skal gemmes
        """
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.results = []
        
    def update(self, result: Dict) -> None:
        """
        Opdaterer status med et nyt download resultat.
        
        Args:
            result (Dict): Download resultat dictionary
        """
        self.results.append(result)
        logging.info(f"Updated status for {result['br_number']}: {result['status']}")
        
    def update_batch(self, batch_results: list) -> None:
        """
        Opdaterer status med en batch af resultater.
        
        Args:
            batch_results (List[Dict]): Liste af download resultater
        """
        self.results.extend(batch_results)
        
    def generate_report(self) -> None:
        """
        Genererer en Excel rapport med download status.
        """
        if not self.results:
            logging.warning("No results to generate report from")
            # Opret en tom rapport med korrekte kolonner
            df = pd.DataFrame(columns=[
                'BR Nummer',
                'Status',
                'Primær URL',
                'Alternativ URL',
                'Fejlbesked',
                'Tidspunkt'
            ])
        else:
            # Konverter resultater til DataFrame
            df = pd.DataFrame([
                {
                    'BR Nummer': r['br_number'],
                    'Status': r['status'],
                    'Primær URL': r['primary_url'],
                    'Alternativ URL': r['alternative_url'],
                    'Fejlbesked': r['error_message'],
                    'Tidspunkt': r['timestamp']
                }
                for r in self.results
            ])
        
        # Gem rapport
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.report_dir / f'download_status_{timestamp}.xlsx'
        df.to_excel(report_path, index=False)
        logging.info(f"Status report generated: {report_path}")
        
    def get_statistics(self) -> dict:
        """
        Beregner statistik over download resultater.
        
        Returns:
            Dict: Statistik over downloads
        """
        if not self.results:
            return {
                'total': 0,
                'success': 0,
                'success_alternative': 0,
                'failed': 0
            }
            
        total = len(self.results)
        success = sum(1 for r in self.results if r['status'] == 'success')
        success_alt = sum(1 for r in self.results if r['status'] == 'success_alternative')
        failed = sum(1 for r in self.results if r['status'] == 'failed')
        
        return {
            'total': total,
            'success': success,
            'success_alternative': success_alt,
            'failed': failed
        }

    def update_status(self, br_number: str, status: str) -> None:
        """
        Alias for update method to maintain compatibility.
        """
        result = {
            'br_number': br_number,
            'status': status,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.update(result)