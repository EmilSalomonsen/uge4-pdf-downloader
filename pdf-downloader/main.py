#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF Downloader - Hovedscript

Dette script koordinerer processen med at downloade PDF-rapporter fra en Excel-fil.
Det håndterer:
- Læsning af URLs fra Excel
- Asynkron nedlasting af PDFs
- Status tracking og rapportering
- Fejlhåndtering og logging
- Generering af metadata i samme format som Metadata2006_2016.xlsx

Brug:
    python main.py --excel "sti/til/excel.xlsx" --output "sti/til/output" --report "sti/til/reports"
"""

import asyncio
import argparse
import logging
from pathlib import Path
from datetime import datetime
import sys
import os

# Tilføj src mappen til Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from excel_handler import ExcelHandler
from downloader import PDFDownloader
from status_tracker import StatusTracker

def setup_logging():
    """
    Opsætter logging systemet med både fil og konsol output.
    """
    # Opret logs mappe hvis den ikke findes
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Generer timestamp for log filnavn
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'pdf_downloader_{timestamp}.log'
    
    # Konfigurer logging format
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def parse_arguments():
    """
    Parser kommandolinje argumenter.
    
    Returns:
        argparse.Namespace: Parsede argumenter
    """
    parser = argparse.ArgumentParser(description='Download PDF rapporter fra Excel fil')
    
    # Påkrævede argumenter
    parser.add_argument('--excel', required=True, help='Sti til Excel fil med URLs')
    parser.add_argument('--output', required=True, help='Mappe hvor PDFs skal gemmes')
    parser.add_argument('--report', required=True, help='Mappe hvor status rapporter skal gemmes')
    
    # Valgfrie argumenter
    parser.add_argument('--max-concurrent', type=int, default=10,
                      help='Maksimalt antal samtidige downloads (default: 10)')
    parser.add_argument('--limit', type=int, default=10,
                      help='Maksimalt antal succesfulde downloads (default: 10)')
    parser.add_argument('--timeout', type=int, default=30,
                      help='Timeout i sekunder for hver download (default: 30)')
    
    return parser.parse_args()

def validate_paths(args):
    """
    Validerer at alle angivne stier eksisterer og er tilgængelige.
    
    Args:
        args (argparse.Namespace): Parsede argumenter
        
    Raises:
        FileNotFoundError: Hvis en sti ikke findes
        PermissionError: Hvis der ikke er adgang til en sti
    """
    # Tjek Excel fil
    if not os.path.exists(args.excel):
        raise FileNotFoundError(f"Excel fil ikke fundet: {args.excel}")
    
    # Opret output mappe hvis den ikke findes
    os.makedirs(args.output, exist_ok=True)
    
    # Opret report mappe hvis den ikke findes
    os.makedirs(args.report, exist_ok=True)

async def main():
    """
    Hovedfunktion der koordinerer hele download processen.
    """
    try:
        # Opsæt logging
        setup_logging()
        logging.info("Starter PDF Downloader")
        
        # Parse og valider argumenter
        args = parse_arguments()
        validate_paths(args)
        
        # Initialiser komponenter
        excel_handler = ExcelHandler(args.excel)
        downloader = PDFDownloader(args.output, args.max_concurrent, args.timeout)
        status_tracker = StatusTracker(args.report)
        
        # Hent URLs fra Excel
        urls = excel_handler.get_urls()
        if not urls:
            logging.error("Ingen URLs fundet i Excel filen")
            return
        
        logging.info(f"Fundet {len(urls)} URLs at downloade")
        logging.info(f"Downloader maksimalt {args.limit} PDFs")
        
        # Start download process
        results = await downloader.download_pdfs(urls, limit=args.limit)
        
        # Generer og gem metadata
        metadata = excel_handler.generate_metadata(results)
        metadata_path = os.path.join(args.report, f'metadata_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
        excel_handler.save_metadata(metadata, metadata_path)
        
        # Generer status rapport
        status_tracker.update_batch(results)
        status_tracker.generate_report()
        
        # Log afslutning
        successful = sum(1 for r in results if r['status'] in ['success', 'success_alternative'])
        logging.info(f"Download process afsluttet. {successful} PDFs downloadet succesfuldt.")
        
    except Exception as e:
        logging.error(f"Fejl under kørsel: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Program afbrudt af brugeren")
    except Exception as e:
        logging.error(f"Uventet fejl: {str(e)}")
        sys.exit(1)