# Kravspecifikation - PDF Downloader

## Grundlæggende Information
| Felt | Værdi |
|------|--------|
| **Navn** | Emil |
| **Opgave** | PDF Downloader |
| **Kodesprog** | Python |
| **Estimeret tid** | 24-30 timer |

## Krav/Prioriteter
De vigtigste elementer i softwaren:
- Downloade PDF rapporter fra en liste med URL's
- Alternativ URL Fallback
- Rapport generering
- Registrering af downloadstatus for hver rapport

## Frameworks/Libraries
- pandas (Excel håndtering)
- aiohttp (async downloads)
- tqdm (progress bars)
- logging (log håndtering)

## Feature List
1. **Data Håndtering**
   - Læse og validere Excel filer
   - Identificere og validere nødvendige kolonner (PDF URL, alternativ URL, BRNummer)

2. **Download Funktionalitet**
   - Concurrent download af PDF filer (10 ad gangen)
   - Fejlhåndtering ved download (timeout, 404 osv.)
   - Auto fallback til alternative URL's

3. **Status og Logging**
   - Status tracking og rapportering
   - Logging af alle handlinger
   - Generere statusrapport
   - Navngivning af filer efter BRNummer

## Work Breakdown Structure

| Arbejdsopgave | Start dato | Forventet slutdato | Tidsforbrug |
|---------------|------------|-------------------|-------------|
| **Projekt Setup og Design** <br> - Opsætning af GitHub repo <br> - UML diagram <br> - Projektstruktur <br> - Development environment | 17/03 | 17/03 | 2-3 timer |
| **Data Håndtering** <br> - Excel fil læsning <br> - Data struktur <br> - Data modeller <br> - Testing | 17/03 | 19/03 | 4-5 timer |
| **Download Engine** <br> - Download funktionalitet <br> - Concurrent downloads <br> - URL fallback <br> - Fejlhåndtering og retry logik <br> - Progress tracking | 19/03 | 20/03 | 8-10 timer |
| **Status Tracking** <br> - Status tracking system <br> - Status opdateringer <br> - Status rapporter | 20/03 | 20/03 | 4-5 timer |
| **Error Handling & Logging** | 20/03 | 21/03 | 3-4 timer |
| **Testing & Optimization** | 21/03 | 21/03 | 2-3 timer |
| **Documentation** <br> - README <br> - Kode dokumentation <br> - User guide <br> - Installation guide | 21/03 | 21/03 | 1-2 timer |

**Total estimeret tid:** 24-32 timer