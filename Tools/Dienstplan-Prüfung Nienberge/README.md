---
tags:
  - projekt
  - apotheke
  - dienstplan
erstellt: 2026-11-08
aktualisiert: 2026-11-08
---
# Dienstplan-Prüfung Nienberge (Werkzeug)

Projektnotiz mit allen Regeln: [[Dienstplan-Prüfung Nienberge]]

**Monatlicher Lauf** (Python 3, `pdfplumber`, `openpyxl`, `numpy`):

```bash
python3 dienstplan_pruefung.py --monat 2026-12 --out Dienstplanpruefung_2026-12.xlsx  KW49.pdf KW50.pdf ...
# optional: --notdienst 2026-12-05,2026-12-19   --sondertage 12-24,12-31
```

| Datei | Aufgabe |
|---|---|
| `apocollect_parser.py` | liest die Wochen-PDFs positionsbasiert (Person x Tag, Bereichsabschnitte) |
| `normalize.py` | Bereich je Dienstabschnitt, Duplikate zusammenführen, Berufsgruppen |
| `engine.py` | Minutenmodell, Mindestbesetzung, Überbrückung, Pausenszenario |
| `analysis.py` | Befunde, KBO/Labor/Notdienst, Prüfkandidaten |
| `excel_report.py` | Excel mit Farben, Legende, Detailblättern |

**Datenschutz:** Exporte (PDF) und Ergebnisdateien enthalten Mitarbeiterdaten und gehören nicht ins Repository.
