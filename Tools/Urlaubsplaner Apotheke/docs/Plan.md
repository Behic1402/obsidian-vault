---
tags:
  - projekt
  - apotheke
  - plan
erstellt: 2026-10-31
---

# Urlaubsplaner Apotheke Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eine offline lauffähige HTML-Datei, die Abwesenheiten gegen die Mindestbesetzung einer Apotheke prüft (W1–W8, getrennte Rollierung Apotheker/PTA).

**Architecture:** Reine Logik-Funktionen in `src/logik.js` (UMD: Node + Browser), Stammdaten als Seed in `src/daten.js`, UI in `src/app.js` + `src/style.css`; `build.js` fügt alles zu einer Datei `urlaubsplaner.html` zusammen. Daten im Browser (localStorage) plus JSON/Excel-Export.

**Tech Stack:** Vanilla JS (ES2019), Node ≥18 (`node --test` für Tests), SheetJS (eingebettet, offline), Playwright (vorinstalliert) nur für den Browser-Smoketest.

**Spec:** `Tools/Urlaubsplaner Apotheke/docs/Spec.md` (Projektordner: `Tools/Urlaubsplaner Apotheke/`)

## Global Constraints

- Alle Pfade relativ zu `Tools/Urlaubsplaner Apotheke/`.
- Sprache der Oberfläche und Kommentare: Deutsch. Datumsformat intern ISO `YYYY-MM-DD`, Anzeige `TT.MM.JJJJ`.
- Wochentage intern `Mo,Di,Mi,Do,Fr,Sa,So`. Wochen laufen Mo–So. Datumsarithmetik nur über Tageszahlen (UTC), nie lokale Zeit.
- Rollierungsstart: `2026-12-28` = W1. Feiertagssamstage (Seed): `2027-05-01`, `2027-12-25`, `2028-01-01`.
- Apotheker-Rollwoche = `((wochenSeitStart − feiertagswochenDavor) mod 8) + 1`; PTA-Rollwoche = `(wochenSeitStart mod 8) + 1`. Gruppen: `Apotheker`, `PTA` (PTA-Praktikant und PhiP gehören zu PTA).
- Zeitblöcke Mo–Fr: 08:00–08:30, 08:30–12:00, 12:00–15:00, 15:00–18:00, 18:00–18:30, 18:30–19:00; Sa: 09:00–13:00, 13:00–13:30.
- Regeln (Min. Personen / Min. Approbierte): Mo–Fr 2/1, 4/1, 2/1, 3/1, 2/1, 1/1 (nur approbiert); Sa 3/1, 1/1 (nur approbiert). Unbekannte Regel = Status `Regel fehlt`, nie geraten.
- Anwesend = aktiv, zählt Mindestbesetzung, Standardplan-Eintrag der gültigen Rollwoche mit `ort='Filiale'` der den Block um > 0 Minuten überlappt, keine Abwesenheit an dem Datum. Homeoffice/Labor/frei zählen nie.
- Status je Block: `OK`, `Unterbesetzt`, `Kein Apotheker`, `Regel fehlt`, `Feiertag` (nicht bewertet). Bei beidem (zu wenig Personen UND kein Apotheker) werden beide Status einzeln ausgegeben (`personalStatus`, `apothekerStatus`).
- Keine echten Abwesenheiten/Mitarbeiterdaten außer Seed-Stammdaten ins Repo. Keine Build-Tools außer Node-Skript, keine Netzwerkzugriffe zur Laufzeit.

## Review Focus

- Woche über den Jahreswechsel (28.12.2026–03.01.2027) und KW53: Rollwoche und Jahresübersicht dürfen nicht nach KW-Nummer, sondern nach Datum zuordnen.
- Person mit `aktiv=nein` oder Abwesenheit ohne Standardplan-Eintrag an dem Tag: darf weder anwesend noch „abwesend" erscheinen.
- Feiertag Mo–Fr in der Woche: Tag wird als `Feiertag` markiert, nicht als Unterbesetzung gemeldet.
- Datum vor dem Rollierungsstart (z. B. 2026-06-01): Hinweis statt falscher Rollwoche.
- Doppelte/überlappende Abwesenheiten und unbekannte Namen beim Import: werden dedupliziert bzw. gemeldet, nicht still verworfen.

---

### Task 1: Datums- und Rollierungslogik

**Files:**
- Create: `src/logik.js`, `tests/logik.test.js`, `package.json` (`{"private":true,"scripts":{"test":"node --test tests/"}}`)

**Interfaces:**
- Produces (alle in `module.exports` / `window.Logik`): `dayNum(iso:string):number`, `isoFromDayNum(n:number):string`, `wochentag(iso):'Mo'|'Di'|...|'So'`, `montagVon(iso):string`, `isoKW(iso):{jahr:number,kw:number}`, `rollwoche(iso:string, gruppe:'Apotheker'|'PTA', rollierung:{start:string,feiertagssamstage:string[]}):number|null` (null vor Start).

- [ ] **Step 1: Failing tests** in `tests/logik.test.js`: `rollwoche('2026-12-28','PTA',R)===1`; `rollwoche('2027-01-04','PTA',R)===2`; `rollwoche('2027-02-22','PTA',R)===1` (8 Wochen später); `rollwoche('2027-06-06' ...)` mit R.feiertagssamstage=['2027-05-01'] liefert für Woche des 26.04.2027 (enthält den 01.05.): PTA `W` und Apotheker `W` gleich, für die Folgewoche 03.05.2027 PTA `W+1` aber Apotheker `W`; danach bleibt Apotheker dauerhaft eine Woche hinter PTA bis zum nächsten Feiertagssamstag; `rollwoche('2026-06-01','PTA',R)===null`; `isoKW('2026-12-31')` → `{jahr:2026,kw:53}`; `isoKW('2027-01-01')` → `{jahr:2026,kw:53}`; `wochentag('2026-12-28')==='Mo'`; `montagVon('2027-01-03')==='2026-12-28'`.
- [ ] **Step 2:** `npm test` → FAIL (Modul fehlt).
- [ ] **Step 3: Implement** die Funktionen aus Interfaces in `src/logik.js` (UMD-Wrapper). Tageszahlen via `Date.UTC(y,m-1,d)/86400000`. Apotheker: `feiertagswochenDavor` = Anzahl Feiertagssamstage, deren Montag strikt vor dem Montag der Zielwoche liegt.
- [ ] **Step 4:** `npm test` → PASS.
- [ ] **Step 5: Commit** `feat: Datums- und Rollierungslogik`.

### Task 2: Seed-Daten (Personal, Standardplan W1–W8, Regeln, Feiertage)

**Files:**
- Create: `src/daten.js`, `tests/daten.test.js`

**Interfaces:**
- Consumes: Task 1 `Logik`.
- Produces: `Daten.seed():Datenmodell` mit `personal:[{name,rolle,approbiert:boolean,rollgruppe,aktiv,zaehlt,anspruch:number|null,hinweis}]`, `standardplan:[{name,wochen:number[],tag,von:'HH:MM',bis:'HH:MM',ort:'Filiale'|'Homeoffice'|'Labor',unbestaetigt?:boolean}]`, `bloecke:[{tagTyp:'MoFr'|'Sa',von,bis}]`, `regeln:[{tag,von,bis,minP,minA,nurAppr}]` (tag `Mo..Sa`, je Block einzeln ausgeschrieben), `rollierung:{start,feiertagssamstage}`, `feiertage:[{datum,name}]` (NRW 2027/2028 inkl. 01.01., Karfreitag 26.03.2027, Ostermontag 29.03.2027, 01.05., Himmelfahrt 06.05.2027, Pfingstmontag 17.05.2027, Fronleichnam 27.05.2027, 03.10. (Sonntag 2027), 01.11.2027, 25./26.12.; 2028 entsprechend nach Ostern 16.04.2028), `abwesenheiten:[]`.
- Personal: Tomke, Katja, Malte, Maren (Apotheker/in, approbiert); Marion I., Marion B., Jutta, Anja, Rama (PTA); Nick (PTA-Praktikant, PTA-Gruppe); PhiP (`aktiv=false`, ohne Plan). `Tomke` im Namen ohne „(Ich)".

- [ ] **Step 1: Failing tests** `tests/daten.test.js` mit Matrix-Prüfungen: Maren hat Sa nur in W2 und W6; Katja Fr nicht in W2/W6, Sa in W1 und W5; Malte Di nicht in W1, Sa in W4 und W8; Tomke Di `Homeoffice` in W2/W6, Di fehlt in W7, Sa in W3 und W7; Marion I. Sa in W1/3/5/7; Anja Sa in W2/4/6/8; Rama Sa nur W4/W8 und kein Labor-Eintrag; Nick Mi nicht in W3/W7, Sa in W1/W3/W5/W7; Marion B. und Jutta in allen W1–W8 identisch; `regeln.length===(6*5+2)`; PhiP `aktiv===false`. Außerdem: **Gegenprobe** – für W1/W2-Beispieltage liefern die Apotheker-Zeiten dieselben Blöcke wie der alte Standardplan (Tomke Mo: 08:00–08:30,08:30–12:00,12:00–15:00,15:00–18:00; Katja Mo: alle 6 Blöcke; Malte Di: ab 08:30 bis 19:00; Maren Fr: 08:00–15:00 bis 3 Blöcke; Katja Fr: 08:30–15:00 = 2 Blöcke; Apotheker Sa: 09:00–13:00 und 13:00–13:30). Dafür `Logik.bloeckeFuer(eintrag, bloecke)` aus Task 3 nutzen → Test erst in Task 3 grün (siehe dort).
- [ ] **Step 2:** Tests laufen → FAIL.
- [ ] **Step 3: Implement** `Daten.seed()` mit den Zeiten aus Spec Abschnitt 7 (Apotheker aus der Excel-Vorlage, PTA aus der Übergabe). Ramas Samstag Startwert 09:00–13:00 `unbestaetigt:true`. Rama: Filialzeiten außer Samstag werden **nicht** eingetragen.
- [ ] **Step 4:** Matrix-Tests PASS (Gegenprobe-Test mit `test.skip` bis Task 3).
- [ ] **Step 5: Commit** `feat: Seed-Daten W1–W8`.

### Task 3: Besetzungsprüfung

**Files:**
- Modify: `src/logik.js`, `tests/logik.test.js`; Gegenprobe in `tests/daten.test.js` aktivieren.

**Interfaces:**
- Consumes: Task 1/2.
- Produces: `bloeckeFuer(eintrag:{von,bis}, bloecke:{von,bis}[]):string[]` (Block-Labels `HH:MM–HH:MM`, Überlappung > 0 Minuten); `pruefeTag(iso:string, d:Datenmodell):{datum,tag,rollApo:number|null,rollPta:number|null,feiertag:string|null,bloecke:[{label,minP,minA,nurAppr,istP,istA,personalStatus,apothekerStatus,anwesend:string[],abwesend:string[]}]}`; `pruefeWoche(iso:string, d):pruefeTag[]` (Mo–Sa, Montag der Woche); `auswirkung(neueAbw:[{datum,name}], d):[{datum,label,status}]` (Blöcke, die erst durch die neue Abwesenheit kippen); `abwesendLautPlan(name, iso, d):boolean`.

- [ ] **Step 1: Failing tests**: (a) Standardwoche 2027-01-04 (W2/W2) ohne Abwesenheit: für jeden Block, in dem alle Regeln bekannt sind, `OK` außer erwarteten Lücken – Erwartungswerte aus der Seed-Rechnung fest im Test hinterlegen (mindestens: Mo 08:30–12:00 `istP≥4`); (b) Tomke Homeoffice-Dienstag (2027-01-05, W2): Tomke nicht in `anwesend`, nicht in `abwesend`; (c) Katja abwesend am Mo 2027-01-04 → Katja in `abwesend`, `istP` um 1 niedriger; (d) `aktiv=false` für Nick → fehlt in beiden Listen; (e) Abwesenheit für Person ohne Plan an dem Tag → in keiner Liste; (f) Feiertag 2027-05-06 → `feiertag='Christi Himmelfahrt'`, Status der Blöcke `Feiertag`; (g) Datum 2026-06-01 → `rollPta===null`, `bloecke` leer und Hinweis über `rollPta===null`; (h) fehlende Regel → `personalStatus==='Regel fehlt'`; (i) Block 18:30–19:00 mit nur nicht-approbierter Person → `apothekerStatus==='Kein Apotheker'`.
- [ ] **Step 2:** FAIL. **Step 3:** Implement; Mapping Personal→Gruppe→Rollwoche via Task 1. **Step 4:** PASS inkl. aktivierter Gegenprobe aus Task 2. **Step 5: Commit** `feat: Besetzungsprüfung`.

### Task 4: Resturlaub, Jahresübersicht, Abwesenheiten-Verwaltung

**Files:**
- Modify: `src/logik.js`, `tests/logik.test.js`

**Interfaces:**
- Produces: `addAbwesenheiten(d, {name,von,bis,art,genehmigt,notiz}):{hinzu:number,uebersprungen:number}` (löst Zeitraum in Tage auf, Dedup nach Datum+Name); `urlaubstage(name, jahr, d):number` (nur Art `Urlaub`, nur Tage, an denen die Person laut Standardplan gearbeitet hätte und kein Feiertag ist; Rollwoche je Gruppe); `resturlaub(name, jahr, d):number|null` (null wenn kein Anspruch); `jahresuebersicht(jahr:number, d):[{name, kws:{[kw:number]:string}}]` – KW und Jahr per `isoKW` des **Datums**; Kürzel aus Art (`U`,`K`,`F`,`P`,`Ü`,`S`), KW 1–53, Wochen, deren ISO-Jahr ≠ `jahr`, werden nicht angezeigt.

- [ ] **Step 1: Failing tests**: Zeitraum 2027-01-04..2027-01-08 → 5 Einträge, Wiederholung → `uebersprungen=5`; Wochenendtage im Zeitraum werden gespeichert, zählen aber nicht als Urlaubstage; `urlaubstage('Maren',2027,d)` zählt Do/Fr korrekt und Feiertag (06.05.2027, Do) nicht; Jahreswechsel: Eintrag 2027-01-01 erscheint in `jahresuebersicht(2026)` bei KW53 und **nicht** in `jahresuebersicht(2027)`; zwei Jahre mit gleicher KW vermischen sich nicht.
- [ ] **Step 2–4:** FAIL → Implement → PASS. **Step 5: Commit** `feat: Resturlaub und Jahresübersicht`.

### Task 5: Excel-Import/-Export

**Files:**
- Create: `src/excel.js`, `tests/excel.test.js`, `vendor/xlsx.full.min.js` (SheetJS, per `npm pack xlsx` bzw. `npm i --prefix /tmp/x xlsx` bezogen und kopiert; Lizenz-Datei daneben)

**Interfaces:**
- Produces: `Excel.parseAbwesenheiten(rows:any[][], d):{eintraege:[{datum,name,art,genehmigt,notiz}], unbekannteNamen:string[], ignoriert:number}` (Zeilenformat des Blatts `Abwesenheiten`: Spalten Datum, Name, Appr., Grund, KW, Tag, –, Genehmigt?; Namen auf `d.personal` abgleichen, „Tomke (Ich)" → „Tomke"; Gründe: `Urlaub`→Urlaub, `PBU`→`PBU`, `ÜS-Ausgleich`→`ÜS-Ausgleich`, `ÜS-frei*`→`ÜS-frei`, sonstige → `Sonstiges` mit Originaltext in `notiz`; Labor-Spalten ab Spalte J ignorieren); `Excel.exportWochenplan(wochenErgebnis):Workbook`, `Excel.exportJahr(uebersicht):Workbook` (SheetJS-Objekte).

- [ ] **Step 1: Failing tests** mit synthetischen Zeilen (keine echten Daten): Excel-Serialdatum und JS-Date werden beide zu ISO; unbekannter Name landet in `unbekannteNamen`, wird nicht importiert; Dubletten werden einmal übernommen; leere Zeilen werden gezählt unter `ignoriert`.
- [ ] **Step 2–4:** FAIL → Implement → PASS. **Step 5: Commit** `feat: Excel-Import und -Export`.

### Task 6: Oberfläche und Build

**Files:**
- Create: `src/app.js`, `src/style.css`, `src/index.template.html`, `build.js`, `tests/browser.test.js` (Playwright, `node tests/browser.test.js`); Output `urlaubsplaner.html` (eingecheckt)

**Interfaces:**
- Consumes: alles aus Tasks 1–5. `build.js` liest `src/*`, `vendor/xlsx.full.min.js` und schreibt **eine** `urlaubsplaner.html` ohne externe Ressourcen.
- Produces: Reiter laut Spec 6: **Wochenprüfung (Startseite, Woche per Datum/KW wählbar, Ampel je Block, PTA- und Apotheker-Rollwoche sichtbar, Feiertag/„vor Rollierungsbeginn"-Hinweise)**, Kalender (Monat + Jahresübersicht), Abwesenheiten (Eintragen mit sofortiger `auswirkung`-Warnung, Liste, Import aus Excel, Löschen), Personal (Aktiv-Schalter, Anspruch, Resturlaub), Standardplan (editierbar je Rollwoche, Ort-Auswahl), Regeln & Rollierung (Regeln, Blöcke, Start, Feiertagssamstage, Feiertage), Daten (JSON Export/Import, Excel-Export, Druckansicht via `@media print`). Auto-Speichern in `localStorage['urlaubsplaner.v1']`; ungültiges JSON beim Import → verständliche Fehlermeldung, Daten bleiben unverändert.

- [ ] **Step 1: Failing Browser-Test** (Playwright, `file://`-URL): Seite lädt ohne Konsolenfehler; Wochenprüfung für 2027-01-04 zeigt 6 Blöcke × 5 Tage + Samstag-Blöcke; Abwesenheit für Katja am 04.01.2027 eintragen → Warnbox erscheint, falls ein Block kippt, Anzeige aktualisiert; Aktiv-Schalter Nick aus → Nick fehlt in den Namenslisten; Reload behält die Daten; JSON-Export dann Import (Roundtrip) identisch; keine Netzwerkanfragen (alle Requests `file:`).
- [ ] **Step 2:** FAIL. **Step 3:** Implement UI schlank: eine `render()`-Funktion je Reiter, kein Framework; Ampelfarben + Textstatus (nicht nur Farbe). **Step 4:** `node build.js && node tests/browser.test.js` → PASS; zusätzlich Screenshot der Wochenprüfung zur Sichtprüfung.
- [ ] **Step 5: Commit** `feat: Oberfläche und Build`.

### Task 7: Unabhängige Prüfung und Auslieferung

- [ ] **Step 1:** Prüfagent (ohne Vorwissen) bekommt nur Spec, die vom Nutzer gelieferten Regeln (Übergabe-Text) und `urlaubsplaner.html`; Auftrag: Regeln/Matrix/Rollierung/Zeitblöcke einzeln gegenprüfen, Review-Focus-Fälle ausprobieren, Abweichungen listen.
- [ ] **Step 2:** Abweichungen beheben, bis keine mehr offen sind; `npm test` und Browser-Test erneut grün.
- [ ] **Step 3:** Vault-Notiz `Urlaubsplanung Apotheke` aktualisieren (Status, Ort der Datei, Bedienhinweis); Commit + Push; `urlaubsplaner.html` dem Nutzer zusenden.
