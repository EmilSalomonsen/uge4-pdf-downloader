import aiohttp
import asyncio
import aiofiles
from pathlib import Path
import logging
from typing import List, Dict
from tqdm import tqdm
import time

class PDFDownloader:
    """
    Håndterer asynkron download af PDF filer med fejlhåndtering og status tracking.
    
    Attributes:
        output_dir (Path): Sti til output directory
        max_concurrent (int): Maksimalt antal samtidige downloads
        timeout (int): Timeout i sekunder for hver request
    """
    
    def __init__(self, output_dir: str, max_concurrent: int = 10, timeout: int = 30):
        """
        Initialiserer PDFDownloader.
        
        Args:
            output_dir (str): Sti hvor PDF filer gemmes
            max_concurrent (int): Maksimalt antal samtidige downloads
            timeout (int): Request timeout i sekunder
        """
        self.output_dir = Path(output_dir)
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def download_pdfs(self, urls: List[Dict], limit: int = None, timeout: int = None) -> List[Dict]:
        """
        Downloader alle PDFs asynkront.
        
        Args:
            urls (List[Dict]): Liste af URL information dictionaries
            limit (int, optional): Maksimalt antal succesfulde downloads
            timeout (int, optional): Override default timeout
            
        Returns:
            List[Dict]: Liste af download resultater
        """
        if timeout:
            self.timeout = timeout
            
        results = []
        tasks = []
        successful_downloads = 0
        
        # Opret aiohttp session med SSL verifikation deaktiveret for at håndtere ældre certifikater
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            with tqdm(total=min(len(urls), limit if limit else len(urls)), 
                     desc="Downloading PDFs") as pbar:
                
                # Behandl URLs i batches for at undgå at overbelaste systemet
                for i in range(0, len(urls), self.max_concurrent):
                    if limit and successful_downloads >= limit:
                        break
                        
                    # Tag næste batch af URLs
                    batch = urls[i:i + self.max_concurrent]
                    
                    # Start downloads for denne batch
                    batch_tasks = [
                        asyncio.create_task(self.download_single(session, url_info))
                        for url_info in batch
                    ]
                    
                    # Vent på at alle downloads i batchen er færdige
                    batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                    
                    # Behandl resultater
                    for result in batch_results:
                        if isinstance(result, Exception):
                            logging.error(f"Download task failed: {str(result)}")
                            continue
                            
                        results.append(result)
                        if result['status'] in ['success', 'success_alternative']:
                            successful_downloads += 1
                            if limit and successful_downloads >= limit:
                                pbar.update(1)
                                break
                                
                        pbar.update(1)
                        
        logging.info(f"Download completed. Successfully downloaded {successful_downloads} PDFs")
        return results
    
    async def download_single(self, session: aiohttp.ClientSession, url_info: Dict) -> Dict:
        """
        Downloader en enkelt PDF fil.
        
        Args:
            session (aiohttp.ClientSession): Aktiv aiohttp session
            url_info (Dict): URL information dictionary
            
        Returns:
            Dict: Download resultat
        """
        result = {
            'br_number': url_info['br_number'],
            'primary_url': url_info['primary_url'],
            'alternative_url': url_info['alternative_url'],
            'status': 'failed',
            'error_message': '',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            # Prøv primær URL
            pdf_content = await self._try_download(session, url_info['primary_url'])
            if pdf_content:
                result['status'] = 'success'
            else:
                # Prøv alternativ URL hvis tilgængelig
                if url_info['alternative_url']:
                    pdf_content = await self._try_download(session, url_info['alternative_url'])
                    if pdf_content:
                        result['status'] = 'success_alternative'
                    
            if pdf_content:
                # Gem PDF fil
                filename = self.output_dir / f"{url_info['br_number']}.pdf"
                await self._save_pdf(pdf_content, filename)
            
        except Exception as e:
            result['error_message'] = str(e)
            logging.error(f"Error downloading {url_info['br_number']}: {e}")
        
        return result
    
    async def _try_download(self, session: aiohttp.ClientSession, url: str) -> bytes:
        """
        Forsøger at downloade fra en URL.
        
        Args:
            session (aiohttp.ClientSession): Aktiv aiohttp session
            url (str): URL at downloade fra
            
        Returns:
            bytes: PDF indhold hvis success, None hvis fejl
        """
        try:
            async with session.get(url, timeout=self.timeout) as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    if 'application/pdf' in content_type:
                        return await response.read()
                    else:
                        logging.warning(f"URL returned non-PDF content: {url} (Content-Type: {content_type})")
                else:
                    logging.warning(f"URL returned status {response.status}: {url}")
                return None
        except Exception as e:
            logging.warning(f"Download failed for {url}: {e}")
            return None
    
    async def _save_pdf(self, content: bytes, filename: Path) -> None:
        """
        Gemmer PDF indhold til fil.
        
        Args:
            content (bytes): PDF indhold
            filename (Path): Sti hvor filen skal gemmes
        """
        async with aiofiles.open(filename, 'wb') as f:
            await f.write(content)