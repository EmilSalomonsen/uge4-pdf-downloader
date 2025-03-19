import asyncio
import logging
import argparse
from pathlib import Path
from src.excel_handler import ExcelHandler
from src.downloader import PDFDownloader
from src.status_tracker import StatusTracker

async def main():
    parser = argparse.ArgumentParser(description='Download PDFs from Excel file URLs')
    parser.add_argument('--excel', required=True, help='Path to Excel file')
    parser.add_argument('--output', required=True, help='Output directory for PDFs')
    parser.add_argument('--report', required=True, help='Output directory for status report')
    parser.add_argument('--max-concurrent', type=int, default=10, help='Maximum concurrent downloads')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of successful downloads')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Valider at Excel filen eksisterer
        excel_path = Path(args.excel)
        if not excel_path.exists():
            raise FileNotFoundError(f"Excel file not found: {args.excel}")
        
        # Opret output og report directories hvis de ikke eksisterer
        output_dir = Path(args.output)
        report_dir = Path(args.report)
        output_dir.mkdir(parents=True, exist_ok=True)
        report_dir.mkdir(parents=True, exist_ok=True)

        logging.info(f"Starting PDF download process")
        logging.info(f"Excel file: {args.excel}")
        logging.info(f"Output directory: {args.output}")
        logging.info(f"Report directory: {args.report}")
        logging.info(f"Max concurrent downloads: {args.max_concurrent}")
        if args.limit:
            logging.info(f"Target successful downloads: {args.limit} files")
        
        # Initialiser komponenter
        excel_handler = ExcelHandler(args.excel)
        downloader = PDFDownloader(args.output, max_concurrent=args.max_concurrent)
        status_tracker = StatusTracker(args.report)
        
        # Læs alle URLs
        all_urls = excel_handler.get_urls()
        logging.info(f"Found {len(all_urls)} total URLs")
        
        results = []
        successful_downloads = 0
        batch_size = 20  # Process URLs i batches
        current_index = 0
        
        while successful_downloads < args.limit and current_index < len(all_urls):
            # Tag næste batch af URLs
            end_index = min(current_index + batch_size, len(all_urls))
            current_batch = all_urls[current_index:end_index]
            
            # Download batch
            batch_results = await downloader.download_all(current_batch)
            results.extend(batch_results)
            
            # Tæl succesfulde downloads
            batch_successful = sum(1 for r in batch_results 
                                 if r['status'] in ['success', 'success_alternative'])
            successful_downloads += batch_successful
            
            logging.info(f"Successful downloads so far: {successful_downloads}/{args.limit}")
            current_index = end_index
            
            if successful_downloads >= args.limit:
                logging.info(f"Reached target of {args.limit} successful downloads")
                break
        
        # Opdater status og generer rapport
        status_tracker.update_batch(results)
        report_path = status_tracker.generate_report()
        
        # Print summary
        summary = status_tracker.get_summary()
        print("\nDownload Summary:")
        print(f"Total attempts: {summary['total']}")
        print(f"Successfully downloaded: {summary['successful']}")
        print(f"Failed: {summary['failed']}")
        print(f"Success rate: {summary['success_rate']:.1f}%")
        print(f"\nStatus report saved to: {report_path}")
        
        logging.info("Process completed successfully")
        
    except Exception as e:
        logging.error(f"Error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())