import pytest
import aiohttp
from pathlib import Path
import asyncio
from src.downloader import PDFDownloader

class MockResponse:
    def __init__(self, status, content=None, content_type='application/pdf'):
        self.status = status
        self._content = content if content else b'%PDF-test'
        self.headers = {'content-type': content_type}
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc, tb):
        pass
        
    async def read(self):
        return self._content

async def mock_success(url, **kwargs):
    return MockResponse(200)
    
async def mock_failure(url, **kwargs):
    return MockResponse(404)
    
async def mock_non_pdf(url, **kwargs):
    return MockResponse(200, content_type='text/html')
    
async def mock_network_error(url, **kwargs):
    raise aiohttp.ClientError("Network error")

@pytest.fixture
def tmp_output_dir(tmp_path):
    output_dir = tmp_path / "pdfs"
    output_dir.mkdir()
    return str(output_dir)

@pytest.fixture
def downloader(tmp_output_dir):
    return PDFDownloader(output_dir=tmp_output_dir, max_concurrent=2)

@pytest.mark.asyncio
async def test_download_valid_pdf(downloader, mocker):
    # Mock aiohttp.ClientSession.get
    mocker.patch('aiohttp.ClientSession.get', side_effect=mock_success)
    
    urls = [{
        'br_number': '12345',
        'primary_url': 'http://example.com/test.pdf',
        'alternative_url': None
    }]
    
    results = await downloader.download_pdfs(urls)
    
    assert len(results) == 1
    assert results[0]['status'] == 'success'
    assert (Path(downloader.output_dir) / '12345.pdf').exists()

@pytest.mark.asyncio
async def test_download_invalid_primary_valid_alternative(downloader, mocker):
    # Mock aiohttp.ClientSession.get to fail for primary but succeed for alternative
    async def mock_get(url, **kwargs):
        if 'example.com' in url:  # primary URL
            return await mock_failure(url, **kwargs)
        else:  # alternative URL
            return await mock_success(url, **kwargs)
    
    mocker.patch('aiohttp.ClientSession.get', side_effect=mock_get)
    
    urls = [{
        'br_number': '12345',
        'primary_url': 'http://example.com/test.pdf',
        'alternative_url': 'http://backup.com/test.pdf'
    }]
    
    results = await downloader.download_pdfs(urls)
    
    assert len(results) == 1
    assert results[0]['status'] == 'success_alternative'
    assert (Path(downloader.output_dir) / '12345.pdf').exists()

@pytest.mark.asyncio
async def test_download_non_pdf_content(downloader, mocker):
    mocker.patch('aiohttp.ClientSession.get', side_effect=mock_non_pdf)
    
    urls = [{
        'br_number': '12345',
        'primary_url': 'http://example.com/test.html',
        'alternative_url': None
    }]
    
    results = await downloader.download_pdfs(urls)
    
    assert len(results) == 1
    assert results[0]['status'] == 'failed'
    assert not (Path(downloader.output_dir) / '12345.pdf').exists()

@pytest.mark.asyncio
async def test_download_network_error(downloader, mocker):
    mocker.patch('aiohttp.ClientSession.get', side_effect=mock_network_error)
    
    urls = [{
        'br_number': '12345',
        'primary_url': 'http://example.com/test.pdf',
        'alternative_url': None
    }]
    
    results = await downloader.download_pdfs(urls)
    
    assert len(results) == 1
    assert results[0]['status'] == 'failed'
    assert 'Network error' in results[0]['error_message']
    assert not (Path(downloader.output_dir) / '12345.pdf').exists()

@pytest.mark.asyncio
async def test_concurrent_downloads(downloader, mocker):
    mocker.patch('aiohttp.ClientSession.get', side_effect=mock_success)
    
    # Create 6 test URLs
    urls = [
        {
            'br_number': f'1234{i}',
            'primary_url': f'http://example.com/test{i}.pdf',
            'alternative_url': None
        }
        for i in range(6)
    ]
    
    # Set limit to 5
    results = await downloader.download_pdfs(urls, limit=5)
    
    assert len(results) == 5  # Should only download 5 files
    assert all(r['status'] == 'success' for r in results)
    
    # Check that exactly 5 files were created
    pdf_files = list(Path(downloader.output_dir).glob('*.pdf'))
    assert len(pdf_files) == 5
