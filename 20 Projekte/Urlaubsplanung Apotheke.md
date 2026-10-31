---
tags:
  - projekt
  - apotheke
status: aktiv
aliases:
  - Urlaubsplaner Apotheke
erstellt: 2026-10-31
aktualisiert: 2026-10-31
---

# Urlaubsplanung Apotheke

Zurück zu [[20 Projekte]] · [[Über mich]]

## Ziel
Tool für die Arbeit in der Apotheke (Filiale): Urlaube/Abwesenheiten eintragen und automatisch prüfen, ob die **Mindestbesetzung** je Wochentag/Zeitblock eingehalten ist (Personen gesamt + approbierte Personen). Vorbild: Personio-Urlaubsplanung, aber nur für Behic als Pflegende:r, das Team sieht nur ein.

## Entscheidungen (2026-10-31)
- Nutzung: Behic pflegt allein, Team sieht nur ein.
- Funktionen: Monats-/Jahreskalender, Resturlaub-Berechnung, Mindestbesetzung-Warnung, Abwesenheitsarten (Urlaub/Krank/Fortbildung/Sonstiges).
- Behic möchte ein **„ganzes Tool"** (nicht nur eine Tabelle).
- Bestehende Grundlage: Excel `KOPIE_NEUurlaubsplanung_komplett_neu_mit_rollierung_fix.xlsx` (Blätter: Urlaubsplanung Vorlage, Regeln, Standardplan, Abwesenheiten, Wochenplan_Check, Jahresübersicht). Datei liegt Claude bisher **nicht** vor. Übergabe aus ChatGPT liegt vor.

## Fachlogik (aus Übergabe-Datei)
- 8 Rollwochen W1–W8, **Start Montag 28.12.2026 = W1**.
- Zwei getrennte Rollierungen: **PTA/PTA-Praktikant/PhiP** (starr) und **Apotheker** (Feiertagssamstage werden übersprungen, PTA-Rhythmus bleibt unberührt). Feiertagssamstage als transparente Hilfstabelle, keine Vollautomatik. NRW-Feiertage prüfen.
- Stammdaten „Personal": Name, Rolle, Approbiert, Rollgruppe, Aktiv, Zählt Mindestbesetzung, Hinweis. **Aktiv-Schalter** für alle: inaktive verschwinden aus Prüfung, Standardplan bleibt.
- Status je Zeitblock: OK / Unterbesetzt / Kein Apotheker.
- Zeitblöcke Mo–Fr: 08:00–08:30, 08:30–12:00, 12:00–15:00, 15:00–18:00, 18:00–18:30, 18:30–19:00. Sa: 09:00–13:00, 13:00–13:30.
- Abwesenheit robust über **Datum + Name** (nicht KW), Jahresübersicht jahresgenau.
- Mindestbesetzung Beispiele: Mo 08:30–12:00 mind. 4 Personen, davon 1 approbiert; Sa 09:00–13:00 mind. 3, davon 1 approbiert; Sa 13:00–13:30 mind. 1 approbiert.

## Team (Rollen, Stand Übergabe)
- Apotheker: Maren (4-Wochen-Rhythmus), Katja (4-Wochen), Malte (8-Wochen), Tomke (8-Wochen; „Büro" = Homeoffice, zählt nicht zur Filialbesetzung) → [[Tomke Knop]]
- PTA: Marion B. (fixe Woche), Jutta (fixe Woche), Marion I. (Sa in W1/3/5/7), Anja (2-Wochen-Rhythmus), Rama (Labor zählt nicht; Sa in W4/W8)
- PTA-Praktikant: Nick (nicht approbiert, zählt mit)
- PhiP 2027: noch unbekannt, vorbereitet mit Aktiv = nein
- Detaillierte W1–W8-Matrix und Arbeitszeiten stehen in der Übergabe-Datei (Behic hat sie freigegeben).

## Regeln Mindestbesetzung (von Behic, 2026-10-31)
Mo–Fr: 08:00–08:30 2/1 · 08:30–12:00 4/1 · 12:00–15:00 2/1 · 15:00–18:00 3/1 · 18:00–18:30 2/1 · 18:30–19:00 1 (approbiert). Sa: 09:00–13:00 3/1 · 13:00–13:30 1 (approbiert). (Personen/davon approbiert.)

## Entscheidungen Tool
- Form: Web-App (eine HTML-Datei) mit Excel-Export, Daten lokal, Spec: `Tools/Urlaubsplaner Apotheke/docs/Spec.md`.
- Hauptzweck: schnell prüfen, ob beantragter Urlaub zu Unterbesetzung führt.
- Apotheker-Rollierung: Feiertagssamstag verschiebt nur Apotheker (eine Woche Verzug), PTA starr.

## Stand (2026-10-31)
Web-App gebaut: `Tools/Urlaubsplaner Apotheke/urlaubsplaner.html` (eine Datei, offline, Daten nur lokal im Browser). Quellcode, Tests, Spec und Plan im selben Ordner. Zwei unabhängige Prüfungen bestanden (9 Funde behoben). Bedienung: Woche wählen → Ampel je Zeitblock; Abwesenheit eintragen → sofortige Warnung; Excel-Abwesenheiten per Import einlesen.

## Hinweis aus Prüfung
Aus der freigegebenen Matrix folgt: Samstage in W2/W6 haben nur Maren und Anja (2 statt 3 Personen) → immer „Unterbesetzt". Mit Behic klären.

## Offen
- [x] Uhrzeiten der Apotheker (aus Excel-Vorlage übernommen)
- [x] Excel-Datei erhalten (2026-10-31)
- [ ] Urlaubsanspruch pro Person (für Resturlaub)
- [ ] Bundesland bestätigen (Übergabe nennt NRW)
