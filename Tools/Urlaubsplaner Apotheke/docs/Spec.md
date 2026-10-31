---
tags:
  - projekt
  - apotheke
  - spec
erstellt: 2026-10-31
aktualisiert: 2026-10-31
---

# Spec: Urlaubsplaner Apotheke (Web-App)

Projektnotiz: [[Urlaubsplanung Apotheke]]

## 1. Ziel
Eine einzelne HTML-Datei (`urlaubsplaner.html`), die offline im Browser läuft. Behic pflegt Abwesenheiten und Stammdaten, die App prüft die **Mindestbesetzung** je Tag/Zeitblock und zeigt Kalender, Jahresübersicht und Resturlaub. Das Team sieht den Plan per Export (PDF/Excel/Ausdruck). Keine Mitarbeiterdaten im Netz.

## 2. Nicht-Ziele
Keine Logins, kein Server, keine Mehrbenutzer-Bearbeitung, keine Zeiterfassung, keine Urlaubsanträge durch Mitarbeiter, keine Feiertags-Vollautomatik für Rollierung.

## 3. Daten (alles in einem JSON-Objekt, localStorage + Export/Import)
- `personal[]`: name, rolle (Apotheker/in, PTA, PTA-Praktikant, PhiP), approbiert, rollgruppe (Apotheker|PTA), aktiv, zaehltMindestbesetzung, urlaubsanspruchTage (Zahl, leer = unbekannt), hinweis.
- `standardplan[]`: personName, rollwoche (1–8), wochentag (Mo–Sa), von, bis, ort (`Filiale` | `Homeoffice` | `Labor`). Nur `Filiale` zählt für die Besetzung.
- `bloecke[]`: tagTyp (Mo–Fr | Sa), von, bis. Standard: Mo–Fr 08:00–08:30, 08:30–12:00, 12:00–15:00, 15:00–18:00, 18:00–18:30, 18:30–19:00; Sa 09:00–13:00, 13:00–13:30. Editierbar.
- `regeln[]`: wochentag, block, minPersonen, minApprobierte, `nurApprobiert` (alle Anwesenden müssen approbiert sein). Fehlende Regeln werden als „Regel fehlt" angezeigt, nie geraten. **Vorbefüllt laut Behic (2026-10-31):**
  - Mo–Fr 08:00–08:30: 2 Personen, 1 approbiert
  - Mo–Fr 08:30–12:00: 4 Personen, 1 approbiert
  - Mo–Fr 12:00–15:00: 2 Personen, 1 approbiert
  - Mo–Fr 15:00–18:00: 3 Personen, 1 approbiert
  - Mo–Fr 18:00–18:30: 2 Personen, 1 approbiert
  - Mo–Fr 18:30–19:00: 1 Person, muss approbiert sein
  - Sa 09:00–13:00: 3 Personen, 1 approbiert (Ziel: 1 Apotheker + 2 PTA/PhiP/Praktikant)
  - Sa 13:00–13:30: 1 Person, muss approbiert sein
- `abwesenheiten[]`: datum (ISO), name, art (Urlaub|Krank|Fortbildung|Sonstiges), genehmigt (ja/nein), notiz. Pro Tag und Person ein Eintrag; Zeiträume werden beim Eintragen auf Tage aufgelöst.
- `rollierung`: startdatum `2026-12-28` (= W1) und `feiertagssamstage[]` (vorbefüllt: 2027-05-01, 2027-12-25, 2028-01-01).
- `feiertage[]`: Datum + Name (NRW), vorbefüllt für 2027 und 2028, editierbar. Feiertage Mo–Fr sind in den Quelldaten nicht geregelt; sie werden im Kalender markiert und beim Resturlaub nicht gezählt, die Besetzungsregeln bleiben unverändert.

## 4. Rollierung
- **PTA-Gruppe** (PTA, PTA-Praktikant, PhiP): Rollwoche = ((Montag der Woche − Startdatum) / 7) mod 8 + 1. Feiertagssamstage haben keinen Einfluss.
- **Apotheker-Gruppe**: gleiche Berechnung, aber jede Woche, die einen Feiertagssamstag enthält, pausiert den Zähler für die **Folgewoche** (die Folgewoche trägt dieselbe Rollwoche wie die Feiertagswoche). Der Samstag der Feiertagswoche entfällt als Apothekerdienst.
- Datumsarithmetik rein auf Kalendertagen (UTC-Mittag), um Zeitumstellung zu vermeiden. Wochen laufen Mo–So; Vorjahres-/Folgejahres-Wochen werden über das Datum, nicht über KW-Nummern, zugeordnet.
- Vor dem Startdatum: Hinweis „vor Rollierungsbeginn", keine Berechnung.

## 5. Besetzungsprüfung
Für ein Datum und einen Block gilt eine Person als **anwesend**, wenn sie `aktiv = ja` und `zaehltMindestbesetzung = ja` hat, laut Standardplan der für ihre Rollgruppe gültigen Rollwoche eine Zeit mit `ort = Filiale` hat, die den Block **überlappt** (Annahme: Überlappung > 0 Minuten), und an diesem Datum keine Abwesenheit eingetragen ist. Ist ein Feiertag eingetragen, wird die Prüfung für diesen Tag als „Feiertag" markiert und nicht bewertet.
Status je Block: `OK`, `Unterbesetzt` (Ist < Min. Personen), `Kein Apotheker` (Ist Approbierte < Min. Approbierte), `Regel fehlt`. Ausgabe: Soll/Ist Personen, Soll/Ist Approbierte, Namen Anwesende, Namen Abwesende.
Abwesende sind Personen, die laut Standardplan gearbeitet hätten und eine Abwesenheit haben.

## 6. Oberfläche (Reiter)
1. **Wochenprüfung**: Woche wählen; Tabelle Tag × Block mit Ampel und Namen; Anzeige der PTA- und Apotheker-Rollwoche.
2. **Kalender**: Monats- und Jahresansicht, Farben nach Art, rote Markierung bei Unterbesetzung; Jahresübersicht Person × KW mit „U" bzw. Art-Kürzel, jahresgenau.
3. **Abwesenheiten**: Liste, Eintragen per Zeitraum, Filter; beim Speichern Warnung, welche Blöcke dadurch kippen.
4. **Personal**: Stammdaten inkl. Aktiv-Schalter, Anspruch, Resturlaub (Anspruch minus genommene Tage; gezählt werden Tage, an denen die Person laut Standardplan gearbeitet hätte, ohne Feiertage).
5. **Standardplan**: W1–W8 je Person, vorbefüllt aus der freigegebenen Übergabe-Matrix (siehe 7).
6. **Regeln & Rollierung**: Regeln, Blöcke, Startdatum, Feiertagssamstage, Feiertage.
7. **Daten**: JSON-Sicherung exportieren/importieren, Excel-Export (Wochenplan, Jahresübersicht, Abwesenheiten), PDF/Druckansicht.

## 7. Vorbefüllung aus der Übergabe
Personal und Rhythmen laut Übergabe-Datei (Maren, Katja, Malte, Tomke; Marion B., Jutta, Marion I., Anja, Rama, Nick; PhiP inaktiv ohne Plan). Tomke-„Büro" = `Homeoffice`; Ramas Laborzeiten werden nicht eingetragen (nur Samstag W4/W8). Die Zeiten bei „ca." sind Startwerte, per UI änderbar. Ramas Samstag (W4/W8): Uhrzeit nicht genannt, Startwert Sa 09:00–13:00, „unbestätigt". Nick: Mo/Di/Do 09:00–18:00, Mi 09:00–18:00 (nicht in W3/W7), Fr 10:00–18:00, Sa 09:00–13:00. Anja: Mi 09:00–13:00, Do 08:00–13:00, Fr 08:00–18:00, Sa 08:45–13:00. Marion I.: Mo 07:45–13:00, Di 08:00–13:00, Mi 08:00–18:30, Fr 08:00–13:00, Sa 08:45–13:15. Katja: Fr frei in W2/W6, Sa in W1/W5. Maren: Sa in W2/W6. Malte: Di frei W1, Sa in W4/W8. Tomke: Di Homeoffice W2/W6, Di frei W7, Sa in W3/W7.
Apotheker-Tage ohne Uhrzeiten in der Übergabe (nur Wochentage): Es werden Platzhalterzeiten verwendet (Mo–Fr 08:00–19:00, Sa 09:00–13:30) und im UI als „Zeit unbestätigt" markiert, damit Behic sie korrigiert.

## 8. Technik
Eine HTML-Datei mit eingebettetem CSS/JS, kein Build. Kern-Logik (Rollierung, Besetzung, Resturlaub) als reine Funktionen in einem getrennten Abschnitt, damit sie per Node-Skript testbar sind. Excel-Export über eine eingebettete SheetJS-Kopie (offline). Tests: Node-Skript `tests/logik.test.js` ohne Frameworks.

## 9. Teststrategie
- Rollierung: 2026-12-28 → W1, 2027-02-22 → W1 (8 Wochen später), Feiertagssamstage verschieben nur Apotheker.
- Besetzung: feste Beispielwoche mit bekannten Ergebnissen; Abwesenheit, Aktiv=nein, Homeoffice zählt nicht.
- Resturlaub: Wochenende/Feiertag/Nicht-Arbeitstag zählt nicht.
- Import/Export: Roundtrip JSON.

## 10. Annahmen / offen
- Apotheker-Rollierung bei Feiertagssamstag (Folgewoche wiederholt die Rollwoche, Apotheker liegt danach eine Woche hinter PTA): durch Behics Beschreibung („dieselbe KW kann für PTA W5, für Apotheker W4 sein") bestätigt.
- Überlappung > 0 Minuten reicht für Anwesenheit im Block.
- Urlaubsanspruch pro Person fehlt noch.
- Apotheker-Arbeitszeiten (Uhrzeiten) fehlen in der Übergabe: Platzhalter ganztägig würden Unterbesetzung verdecken; die App zeigt deshalb ein Warnbanner, solange Zeiten „unbestätigt" sind. **Behic liefert die echten Zeiten.**
- Fehlende Regel-Werte trägt Behic ein.

## 11. Primärer Zweck (Behic)
Schnell sehen, ob eine **beantragte Abwesenheit** in einer bestimmten Woche zu Unterbesetzung führt. Deshalb: Wochenprüfung ist Startseite, Woche per KW/Datum wählbar, und beim Eintragen einer Abwesenheit sofortige Auswirkungs-Warnung. Resturlaub ist nachrangig (optional).
