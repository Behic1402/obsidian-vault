---
tags:
  - projekt
  - apotheke
erstellt: 2026-10-31
---
# Urlaubsplaner Apotheke

**Benutzen:** `urlaubsplaner.html` per Doppelklick im Browser öffnen (offline, Daten bleiben nur in diesem Browser). Regelmäßig im Reiter „Daten“ eine JSON-Sicherung speichern.

1. Reiter **Abwesenheiten → Import aus Excel**: alte Datei wählen (Blatt „Abwesenheiten“).
2. Reiter **Wochenprüfung**: Woche wählen, Ampel je Zeitblock.
3. Neue Abwesenheit eintragen: Warnung erscheint sofort.
4. Anspruch je Person im Reiter **Personal** eintragen (für Resturlaub).

**Entwickeln:** `npm test` (Logik), `node build.js` (baut die HTML), `node tests/browser.smoke.js` (Browser-Test). Spec/Plan: `docs/`.

Bekannt: Block-Zeiten sind nicht in der App editierbar (nur Regeln). Feiertage 2026–2028 NRW vorbefüllt.
