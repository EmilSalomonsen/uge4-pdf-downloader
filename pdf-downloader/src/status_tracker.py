import pandas as pd
from pathlib import Path
import logging
from typing import List, Dict
from datetime import datetime

class StatusTracker:
    """
    Holder styr på status for PDF downloads og genererer rapporter.
    
    Attributes:
        results (List[Dict]): Liste af download resultater
        report_path (Path): Sti hvor rapport skal gemmes
    """
    
    def __init__(self, report_path: str):
        """
        Initialiserer StatusTracker.
        
        Args:
            report_path (str): Sti hvor statusrapport skal gemmes
        """
        self.report_path = Path(report_path)
        self.results = []
        self.report_path.mkdir(parents=True, exist_ok=True)
        
    def update(self, result: Dict) -> None:
        """
        Opdaterer status med et nyt download resultat.
        
        Args:
            result (Dict): Download resultat dictionary
        """
        self.results.append(result)
        logging.info(f"Updated status for {result['br_number']}: {result['status']}")
        
    def update_batch(self, results: List[Dict]) -> None:
        """
        Opdaterer status med en batch af resultater.
        
        Args:
            results (List[Dict]): Liste af download resultater
        """
        self.results.extend(results)
        success_count = sum(1 for r in results if r['status'] in ['success', 'success_alternative'])
        logging.info(f"Batch update: {success_count}/{len(results)} successful downloads")
    
    def generate_report(self) -> Path:
        """
        Genererer Excel rapport med download status.
        
        Returns:
            Path: Sti til den genererede rapport
        """
        if not self.results:
            logging.warning("No results to generate report from")
            return None
            
        # Konverter resultater til DataFrame
        df = pd.DataFrame(self.results)
        
        # Simplificer status til kun "Downloadet" eller "Ikke downloadet"
        df['download_status'] = 'Ikke downloadet'  # Default værdi
        success_mask = df['status'].isin(['success', 'success_alternative'])
        df.loc[success_mask, 'download_status'] = 'Downloadet'
        
        # Organiser kolonner - kun de nødvendige kolonner som kunden ønsker
        columns = [
            'br_number',
            'download_status',
            'primary_url',
            'alternative_url',
            'timestamp'
        ]
        
        df = df[columns]
        
        # Omdøb kolonner til dansk
        column_names = {
            'br_number': 'BR Nummer',
            'download_status': 'Status',
            'primary_url': 'Primær URL',
            'alternative_url': 'Alternativ URL',
            'timestamp': 'Tidspunkt'
        }
        df = df.rename(columns=column_names)
        
        # Gem rapport
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = self.report_path / f"download_status_{timestamp}.xlsx"
        df.to_excel(report_filename, index=False)
        
        # Log statistik
        total = len(df)
        successful = (df['Status'] == 'Downloadet').sum()
        logging.info(f"Report generated: {successful}/{total} files downloaded successfully")
        logging.info(f"Report saved to: {report_filename}")
        
        return report_filename
    
    def get_summary(self) -> Dict:
        """
        Returnerer opsummering af download status.
        
        Returns:
            Dict: Status opsummering
        """
        if not self.results:
            return {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'success_rate': 0
            }
            
        total = len(self.results)
        successful = sum(1 for r in self.results if r['status'] in ['success', 'success_alternative'])
        
        return {
            'total': total,
            'successful': successful,
            'failed': total - successful,
            'success_rate': (successful / total) * 100 if total > 0 else 0
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