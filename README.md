# PDF Downloader

Et Python-baseret værktøj til at downloade PDF-filer fra URLs i Excel-filer. Værktøjet er designet til at håndtere store mængder af URLs effektivt med asynkron nedlasting og robust fejlhåndtering.

## Features

- Asynkron nedlasting af PDF-filer
- Håndtering af både primære og alternative URLs
- Automatisk status tracking og rapportering
- Batch processing for effektiv håndtering af store datasæt
- Detaljerede fejlrapporter
- Konfigurerbar nedlastningsgrænse

## Installation

1. Klon repository'et:
```bash
git clone [repository-url]
cd pdf-downloader
```

2. Opret et virtuelt miljø og aktiver det:
```bash
python -m venv venv
# På Windows:
venv\Scripts\activate
# På Unix eller MacOS:
source venv/bin/activate
```

3. Installer afhængigheder:
```bash
pip install -r requirements.txt
```

## Brug

### Basis brug

```bash
python main.py --excel "sti/til/excel/fil.xlsx" --output "sti/til/output" --report "sti/til/reports"
```

### Avancerede muligheder

```bash
python main.py --excel "sti/til/excel/fil.xlsx" \
               --output "sti/til/output" \
               --report "sti/til/reports" \
               --max-concurrent 10 \
               --limit 10 \
               --timeout 30
```

### Parametre

- `--excel`: Sti til Excel-filen med URLs
- `--output`: Mappe hvor PDF-filerne skal gemmes
- `--report`: Mappe hvor status rapporter skal gemmes
- `--max-concurrent`: Maksimalt antal samtidige downloads (standard: 10)
- `--limit`: Maksimalt antal succesfulde downloads (standard: 10)
- `--timeout`: Timeout i sekunder for hver download (standard: 30)


