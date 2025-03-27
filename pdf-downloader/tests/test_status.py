import pytest
from pathlib import Path
import pandas as pd
from src.status_tracker import StatusTracker

# Test data
TEST_RESULTS = [
    {
        'br_number': 'BR50041',
        'status': 'success',
        'primary_url': 'http://test1.com',
        'alternative_url': None,
        'error_message': '',
        'timestamp': '2025-03-27 20:00:00'
    },
    {
        'br_number': 'BR50042',
        'status': 'failed',
        'primary_url': 'http://test2.com',
        'alternative_url': 'http://alt2.com',
        'error_message': 'Network error',
        'timestamp': '2025-03-27 20:00:01'
    },
    {
        'br_number': 'BR50043',
        'status': 'success_alternative',
        'primary_url': 'http://test3.com',
        'alternative_url': 'http://alt3.com',
        'error_message': '',
        'timestamp': '2025-03-27 20:00:02'
    }
]

@pytest.fixture
def tmp_report_dir(tmp_path):
    """Opretter en midlertidig rapport mappe"""
    report_dir = tmp_path / "reports"
    report_dir.mkdir()
    return str(report_dir)

@pytest.fixture
def status_tracker(tmp_report_dir):
    """Opretter en StatusTracker instance"""
    return StatusTracker(tmp_report_dir)

def test_update_batch(status_tracker):
    """Test at batch updates fungerer korrekt"""
    status_tracker.update_batch(TEST_RESULTS)
    
    # Verificér at alle resultater blev tilføjet
    assert len(status_tracker.results) == len(TEST_RESULTS)
    
    # Tjek specifikke værdier
    assert status_tracker.results[0]['br_number'] == 'BR50041'
    assert status_tracker.results[0]['status'] == 'success'
    
    assert status_tracker.results[1]['br_number'] == 'BR50042'
    assert status_tracker.results[1]['error_message'] == 'Network error'

def test_generate_report(status_tracker, tmp_report_dir):
    """Test at rapport generering fungerer korrekt"""
    status_tracker.update_batch(TEST_RESULTS)
    status_tracker.generate_report()
    
    # Find den genererede rapport fil
    report_files = list(Path(tmp_report_dir).glob('download_status_*.xlsx'))
    assert len(report_files) == 1
    
    # Læs og verificér rapport indhold
    report_df = pd.read_excel(report_files[0])
    
    assert len(report_df) == len(TEST_RESULTS)
    assert all(col in report_df.columns for col in ['BR Nummer', 'Status', 'Primær URL', 'Alternativ URL', 'Fejlbesked', 'Tidspunkt'])
    
    # Tjek specifikke værdier
    assert report_df.iloc[0]['BR Nummer'] == 'BR50041'
    assert report_df.iloc[0]['Status'] == 'success'
    assert pd.isna(report_df.iloc[0]['Fejlbesked'])
    
    assert report_df.iloc[1]['BR Nummer'] == 'BR50042'
    assert report_df.iloc[1]['Status'] == 'failed'
    assert report_df.iloc[1]['Fejlbesked'] == 'Network error'

def test_empty_results(status_tracker, tmp_report_dir):
    """Test håndtering af tom resultatliste"""
    status_tracker.update_batch([])
    status_tracker.generate_report()
    
    # Find den genererede rapport fil
    report_files = list(Path(tmp_report_dir).glob('download_status_*.xlsx'))
    assert len(report_files) == 1
    
    # Verificér at rapporten er tom men har korrekte kolonner
    report_df = pd.read_excel(report_files[0])
    assert len(report_df) == 0
    assert all(col in report_df.columns for col in ['BR Nummer', 'Status', 'Primær URL', 'Alternativ URL', 'Fejlbesked', 'Tidspunkt'])

def test_multiple_batches(status_tracker):
    """Test håndtering af multiple batch updates"""
    # Første batch
    status_tracker.update_batch(TEST_RESULTS[:2])
    assert len(status_tracker.results) == 2
    
    # Anden batch
    status_tracker.update_batch(TEST_RESULTS[2:])
    assert len(status_tracker.results) == 3
    
    # Verificér rækkefølge
    assert status_tracker.results[0]['br_number'] == 'BR50041'
    assert status_tracker.results[2]['br_number'] == 'BR50043'
