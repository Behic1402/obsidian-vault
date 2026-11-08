---
name: dienstplan-pruefung
description: >-
  Monatliche Dienstplan-Prüfung für die Jahreszeiten Apotheke Nienberge.
  Liest die ApoCollect-Wochenexporte (PDF, 4-5 Wochen) eines Monats ein und
  erstellt eine farblich bewertete Excel-Prüfdatei (Mindestbesetzung je
  Zeitblock, KBO, Labor, Notdienst, Pausenabstimmung, Prüfkandidaten).
  Nutzen, wenn Behic Wochenexporte/Dienstpläne hochlädt, "Monatliche
  Dienstplanung" oder "Dienstplan prüfen" sagt.
argument-hint: "<Prüfmonat JJJJ-MM> [Notdiensttermine]"
---

# Dienstplan-Prüfung Nienberge

Regeln (verbindlich, nicht ändern): `20 Projekte/Dienstplan-Prüfung Nienberge.md`.
Werkzeug: `Tools/Dienstplan-Prüfung Nienberge/` (siehe README dort).

## Ablauf
1. Prüfmonat klären (Behic prüft den **Folgemonat**), Notdiensttermine erfragen (sonst „Notdienstprüfung offen – Termine fehlen").
2. PDFs liegen unter `/root/.claude/uploads/<session>/` (oder wo Behic sie ablegt). Nicht ins Repo kopieren (Mitarbeiterdaten).
3. Lauf:
   ```bash
   python3 -I "Tools/Dienstplan-Prüfung Nienberge/dienstplan_pruefung.py" \
     --monat 2026-12 --notdienst 2026-11-30 \
     --out <Scratchpad>/Dienstplanpruefung_2026-12.xlsx  <alle Wochen-PDFs>
   ```
4. **Prüferagent-Regel:** Vor der Lieferung prüft ein separater Agent ohne Vorwissen die Datei gegen die Originalregeln (Stichproben aus den PDF-Bildern nachrechnen, Farben, Vollständigkeit). Erst liefern, wenn alles erfüllt ist.
5. Datei an Behic senden, kurz die wichtigsten Befunde nennen. Excel/PDFs **nicht** ins Repository committen.

## Wichtige Auslegungen (mit Behic abgestimmt)
- Bereichskürzel im Dienst hat Vorrang; ohne Kürzel gilt der Abschnittsstandard (Hauptbereich JZN, 3b KBO, 3c Labor).
- Nur JZN/PBO/KBO/Lab zählen; JZY/JZV/JZA nicht. Nicht approbierte Laborpersonen zählen im Labor nicht mit.
- Nick Große („Auszubildende/r") = PTA-Praktikant. Andere unklare Berufsbezeichnungen nicht zuordnen.
- Überbrückt werden nur 60-min-Lücken (Beginn 11:00–15:00); `P: x min (hh:mm)` wird in der Hauptübersicht nicht abgezogen.
- Notdienst: `--notdienst <Termine>` (mitgeteilte Termine, `keine` = keine im Zeitraum, weglassen = offen). Dezember 2026: nur 30.11.2026 (letzter Notdienst 2026). Termine 2027 kommen später von Behic.
- Approbierte Person in Pause zählt weiter für die Mindestzahl Approbierte (Pause in den Räumen). Samstag 09–13 Uhr: genau 3 Personen (mehr = Mangel).
- Tage nach dem Prüfmonat werden vorerst nicht geprüft; Wochenrest davor wird mitgeprüft (kursiv grau). Feiertage = geschlossen, nicht prüfen.
- 24.12. und 31.12. werden vorerst nicht bewertet (Behic prüft manuell, nur 08–13 Uhr, 3 Personen).
- Feiertage laut Export: nicht bewerten, zur Klärung markieren.
