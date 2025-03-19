# UML Class Diagram - PDF Downloader

```mermaid
classDiagram
    class ExcelHandler {
        -str file_path
        -DataFrame data
        +__init__(file_path: str)
        +validate_columns()
        +get_urls() List[Dict]
        -_read_excel()
        -_validate_data()
    }

    class PDFDownloader {
        -str output_dir
        -int max_concurrent
        -Session session
        +__init__(output_dir: str, max_concurrent: int)
        +download_all(urls: List[Dict]) List[DownloadResult]
        +download_single(url_info: Dict) DownloadResult
        -_try_alternative_url(url_info: Dict)
        -_save_pdf(content: bytes, filename: str)
        -_create_session()
    }

    class StatusTracker {
        -List[DownloadResult] results
        -str report_path
        +__init__(report_path: str)
        +update(result: DownloadResult)
        +generate_report()
        +export_to_excel()
        -_format_results()
    }

    class DownloadResult {
        +str br_number
        +str primary_url
        +str alternative_url
        +str status
        +str error_message
        +datetime timestamp
    }

    class Utils {
        +validate_url(url: str) bool
        +create_directory(path: str)
        +setup_logging()
        +sanitize_filename(name: str) str
    }

    PDFDownloader ..> DownloadResult
    StatusTracker ..> DownloadResult
    PDFDownloader ..> Utils
    ExcelHandler ..> Utils
    StatusTracker ..> Utils
```

Dette diagram viser:

1. **ExcelHandler**
   - Håndterer læsning og validering af Excel filer
   - Ekstraherer URL information
   - Validerer nødvendige kolonner

2. **PDFDownloader**
   - Håndterer concurrent downloads
   - Implementerer fallback til alternative URLs
   - Gemmer PDFs med korrekt navngivning

3. **StatusTracker**
   - Holder styr på download status
   - Genererer statusrapporter
   - Eksporterer resultater til Excel

4. **DownloadResult**
   - Data klasse til at holde information om hver download
   - Inkluderer status, fejlbeskeder og timestamps

5. **Utils**
   - Hjælpefunktioner der bruges på tværs af klasserne
   - URL validering, filhåndtering, logging

**Relationer:**
- PDFDownloader og StatusTracker bruger DownloadResult til at kommunikere resultater
- Alle klasser bruger Utils for fælles funktionalitet
- ExcelHandler leverer data til PDFDownloader
- StatusTracker modtager resultater fra PDFDownloader
