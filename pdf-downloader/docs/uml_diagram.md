# UML Klasse Diagram

```mermaid
classDiagram
    class ExcelHandler {
        +read_excel_file(file_path: str)
        +validate_data()
        +get_urls()
        -_validate_columns()
        -_extract_urls()
    }

    class PDFDownloader {
        +download_pdfs(urls: List[Dict])
        +set_max_concurrent(limit: int)
        +set_timeout(seconds: int)
        -_download_single(session: ClientSession, url_info: Dict)
        -_try_download(session: ClientSession, url: str)
        -_save_pdf(content: bytes, filename: Path)
        -_validate_pdf(content: bytes)
    }

    class StatusTracker {
        +update_status(br_number: str, status: str)
        +generate_report()
        +save_report()
        -_create_report_dataframe()
        -_format_status(status: str)
    }

    class Main {
        +run()
        -_setup_logging()
        -_parse_arguments()
        -_validate_paths()
    }

    Main --> ExcelHandler
    Main --> PDFDownloader
    Main --> StatusTracker
    PDFDownloader --> StatusTracker
```

## Klassernes Ansvar

### ExcelHandler
- Håndterer læsning og validering af Excel-filer
- Ekstraherer URLs og metadata
- Validerer data format og kolonner

### PDFDownloader
- Håndterer asynkron nedlasting af PDF-filer
- Implementerer retry logik og fejlhåndtering
- Validerer PDF indhold
- Håndterer concurrent downloads

### StatusTracker
- Registrerer download status
- Genererer og gemmer status rapporter
- Formaterer status data

### Main
- Koordinerer program flow
- Håndterer argument parsing
- Sætter op logging
- Validerer input/output paths
