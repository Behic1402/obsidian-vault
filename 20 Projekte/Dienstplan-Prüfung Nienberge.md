---
tags:
  - projekt
  - apotheke
  - dienstplan
status: wartet auf Dateien
aliases:
  - Monatliche Dienstplanung
  - ApoCollect-Prüfung
erstellt: 2026-11-08
aktualisiert: 2026-11-08
---

# Dienstplan-Prüfung Nienberge (ApoCollect)

Zurück zu [[20 Projekte]] · [[Über mich]] · verwandt: [[Urlaubsplanung Apotheke]]

## Auftrag (Behic, 2026-11-08)
Exportierte ApoCollect-Dienstpläne der Jahreszeiten Apotheke Nienberge gegen die Betriebsregeln prüfen und als **farblich bewertete Excel-Prüfdatei** ausgeben. **Kein neuer Dienstplan, keine Änderung von Diensten.** Es zählen nur konkret exportierte Dienste, nichts aus Standardplänen/Rollierung ergänzen.

## Grundlagen
- Öffnung: Mo–Fr 08:00–18:30, Sa 09:00–13:00.
- Approbiert = Apotheker/in. Nicht approbiert = PTA, PTA-Praktikant, PhiP. Nick Große („Auszubildende/r" im Export) = PTA-Praktikant. Andere unklare Berufsbezeichnungen nicht selbst zuordnen.
- Urlaub, Krank, Frei, Elternzeit, Überstundenabbau, Homeoffice, sonstige Abwesenheit zählen nicht. Unklares → „nicht eindeutig prüfbar", nie Besetzung unterstellen.

## Standorte/Bereiche
| Kürzel | Bedeutung | Zählt in Nienberge |
|---|---|---|
| JZN | Nienberge (Handverkauf) | ja |
| JZY / JZV | York-Center / Vital-Center | nein |
| JZA | Zentrale (Homeoffice, Fortbildung) | nein |
| PBO | Pharm. Backoffice Nienberge | ja (gesamt + approbiert) |
| KBO | Kaufm. Backoffice Nienberge | ja |
| Lab | Labor Nienberge | Approbierte ja; Nicht-Approbierte während Laborzeit nein |
- Hauptbereich „Jahreszeiten Apotheke Nienberge": Dienste ohne Kürzel können reguläre JZN-Dienste sein. Abschnittsangaben beachten.
- Bei Widerspruch gewinnt die Bereichszuordnung vor der Tätigkeit (KBO + Handverkauf = KBO). Widersprüche nur als Datenpflegehinweis, nicht als Besetzungsmangel.
- Personen erscheinen mehrfach (Haupt-, KBO-, Laborbereich) → zusammenführen, je Zeitpunkt nur einmal zählen. Alle Seiten lesen (Laborvertretung!). Keine eigene PBO-Mindestbesetzung.

## Mindestbesetzung (Gesamt / davon approbiert)
- Mo–Fr: 07:45–08:00 Aufschließen 1/0 · 08:00–08:30 2/1 · 08:30–12:00 4/1 · 12:00–15:00 2/1 · 15:00–18:00 3/1 · 18:00–18:30 2/1 · 18:30–19:00 Abschließen 1/1.
- Sa: 08:45–09:00 Aufschließen 1/0 · 09:00–13:00 3/1 · 13:00–13:30 Abschließen 1/1. Ziel: 1 Apotheker + 2 PTA/PTA-Prakt./PhiP (Zahl und Zusammensetzung getrennt prüfen).
- Prüfung durchgehend im Block (Minimum zählt), Dienstende 12:00 = ab 12:00 nicht mehr da, direkt anschließende Dienste lückenlos. Feiertage/abweichende Öffnung ohne klare Angabe → separat zur Klärung.

## KBO und Labor
- KBO: Mo–Fr 10:00 und 16:00, Sa 10:00 muss mind. 1 Person dem KBO zugeordnet sein (nur Bereichszuordnung, nur Überbrückung einer Pause belegt es nicht).
- Labor Mo/Mi/Fr: tagsüber mind. 2 verschiedene Personen, 1 approbiert + 1 nicht approbiert (PTA/Prakt./PhiP), nicht gleichzeitig nötig. Di/Do/Sa keine Pflicht, Zählregeln gelten trotzdem.

## Mittagspausen
- Beginnzeiten sind Richtwerte („P: 60 min (13:00)"), auch einstündige Lücke zwischen Abschnitten. Beide Darstellungen gleich behandeln, nie doppelt abziehen. Andere Lücken nicht automatisch als Pause.
- Hauptübersicht: **„Besetzung ohne Abzug flexibler Mittagspausen"**, eindeutige Pausen überbrücken, Unsicherheit bei Bereichswechsel kennzeichnen. Zusätzlich Hinweis „Pausenabstimmung erforderlich" bei möglichen Engpässen, keine feste Unterbesetzung allein aus Pausenrichtzeiten.

## Notdienst
Termine kommen separat. Je Termin 09:00 bis 09:00 Folgetag durchgehend mind. 1 Approbierte; lückenlose Übergaben ok; reguläre Besetzung gilt zusätzlich; keine Doppelzählung. Ohne Liste: „Notdienstprüfung offen – Termine fehlen". Termine nie erfinden.

## Soll/Ist
Zukünftige Wochen = Soll, aktuelle/vergangene evtl. Ist → Hinweis auf Mischung, nichts rekonstruieren oder runden.

## Farben (Zellhintergrund, keine Farbnamen als Text, kleine Legende)
- Gesamt: unter Min rot · genau Min gelb · +1 hellgrün · +2 dunkelgrün · +3 oder mehr rosa.
- Approbierte (bei Min ≥ 1): 0 rot · 1 hellgrün · 2 dunkelgrün · ≥3 rosa. Aufschließen: „nicht erforderlich" neutral.
- KBO/Labor/Notdienst: grün erfüllt · rot nicht erfüllt · grau nicht eindeutig prüfbar · „entfällt" neutral.
- Gesamt und Approbierte getrennt bewerten, jeweils eigenes Minimum im Block.

## Aufbau der Prüfdatei
- Wochenübersicht je Tag/Zeitblock: Datum+Wochentag, Block, Gesamt Soll, Gesamt Ist (Min–Max), Appro Soll, Appro Ist (Min–Max), Hinweise. Jede Woche klar erkennbar.
- Tägliche Zusatzübersicht: KBO 10/16 Uhr, Labor nicht approbiert, Labor approbiert, ggf. Notdienst, mit Personen und Zeiten.
- Detailblatt, getrennt: bestätigte Unterbesetzungen (Datum, Zeitraum, Ist/Soll, anrechenbare Personen, Erklärung) · Pausenhinweise · Datenpflegehinweise · offene Prüfungen. Dazu Kurzfazit (Engpässe, Zeiten ohne Reserve, erhöhte Reserven, offene Fragen).
- Prüfkandidaten für Überstundenabbau/Freistellung: Berufsgruppe, KBO, Labor, Auf-/Abschließen, Notdienst, Pausenverteilung beachten. Rosa allein heißt nicht „frei möglich"; Zeitabschnitts-Reserve von ganztägiger Freistellung unterscheiden.
- Optimierungsvorschläge zur Prüfdatei willkommen, aber die festgelegten Regeln nicht ändern.

## Nutzung (Behic, 2026-11-08)
- **Monatlicher Ablauf:** Einmal im Monat werden die 4–5 Wochenexporte (ApoCollect) für den **darauffolgenden Monat** hochgeladen und geprüft.
- Dezember 2026 dient als Beispiel/Testfall. Ziel: wiederverwendbares Werkzeug/Skill, Regeln bleiben unverändert.
- Pro Lauf zusätzlich nötig: Notdiensttermine des Monats.

## Stand
- 2026-11-08: Regeln aufgenommen. **Exportdateien fehlen noch** (nicht in der Sitzung angekommen), Notdiensttermine fehlen ebenfalls.
