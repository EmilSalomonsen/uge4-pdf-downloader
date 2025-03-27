import pytest
import pandas as pd
from pathlib import Path
import os
from src.excel_handler import ExcelHandler

# Test data
TEST_DATA = {
    'BRnum': ['BR50041', 'BR50042', 'BR50043'],
    'Pdf_URL': ['http://test1.com', 'http://test2.com', None],
    'Report Html Address': [None, 'http://alt2.com', 'http://alt3.com']
}

@pytest.fixture
def test_excel_file(tmp_path):
    """Opretter en test Excel fil med kendt indhold"""
    df = pd.DataFrame(TEST_DATA)
    file_path = tmp_path / "test.xlsx"
    df.to_excel(file_path, index=False)
    return str(file_path)

@pytest.fixture
def excel_handler(test_excel_file):
    """Opretter en ExcelHandler instance med test data"""
    return ExcelHandler(test_excel_file)

def test_excel_file_not_found():
    """Test at der raises FileNotFoundError når filen ikke findes"""
    with pytest.raises(FileNotFoundError):
        ExcelHandler("ikke_eksisterende_fil.xlsx")

def test_validate_columns_missing_columns(tmp_path):
    """Test at der raises ValueError når påkrævede kolonner mangler"""
    # Opret Excel fil uden påkrævede kolonner
    df = pd.DataFrame({'NotRequired': [1, 2, 3]})
    file_path = tmp_path / "invalid.xlsx"
    df.to_excel(file_path, index=False)
    
    with pytest.raises(ValueError):
        ExcelHandler(str(file_path))

def test_get_urls(excel_handler):
    """Test at URLs bliver korrekt ekstraheret"""
    urls = excel_handler.get_urls()
    assert len(urls) == 3
    
    # Test første række
    assert urls[0]['br_number'] == 'BR50041'
    assert urls[0]['primary_url'] == 'http://test1.com'
    assert urls[0]['alternative_url'] is None
    
    # Test anden række
    assert urls[1]['br_number'] == 'BR50042'
    assert urls[1]['primary_url'] == 'http://test2.com'
    assert urls[1]['alternative_url'] == 'http://alt2.com'

def test_generate_metadata(excel_handler):
    """Test at metadata bliver korrekt genereret"""
    download_results = [
        {
            'br_number': 'BR50041',
            'status': 'success',
            'primary_url': 'http://test1.com',
            'alternative_url': None
        },
        {
            'br_number': 'BR50042',
            'status': 'failed',
            'primary_url': 'http://test2.com',
            'alternative_url': 'http://alt2.com'
        }
    ]
    
    metadata_df = excel_handler.generate_metadata(download_results)
    
    # Verificér at kun processerede rækker er inkluderet
    assert len(metadata_df) == 2
    
    # Tjek download status
    status_series = metadata_df.set_index('BRnum')['Download Status']
    assert status_series['BR50041'] == 'Downloadet'
    assert status_series['BR50042'] == 'Ikke downloadet'

def test_save_metadata(excel_handler, tmp_path):
    """Test at metadata kan gemmes korrekt"""
    output_path = tmp_path / "metadata_output.xlsx"
    
    # Generer nogle test metadata
    download_results = [{
        'br_number': 'BR50041',
        'status': 'success',
        'primary_url': 'http://test1.com',
        'alternative_url': None
    }]
    
    metadata_df = excel_handler.generate_metadata(download_results)
    excel_handler.save_metadata(metadata_df, str(output_path))
    
    # Verificér at filen blev oprettet
    assert output_path.exists()
    
    # Verificér indholdet
    saved_df = pd.read_excel(output_path)
    assert 'Download Status' in saved_df.columns
    assert len(saved_df) == 1
