---
tags:
  - wissen
  - obsidian
aliases:
  - Graph View
  - Graph-Ansicht
erstellt: 2026-10-26
aktualisiert: 2026-10-26
---

# Obsidian Graph-Ansicht

Die Graph-Ansicht zeigt alle Notizen als Punkte und die `[[Wikilinks]]` zwischen ihnen als Linien.

## Öffnen
- Linke Seitenleiste: Symbol **„Graph-Ansicht öffnen“** (drei verbundene Punkte)
- Oder `Strg/Cmd + G`
- Oder Befehlspalette (`Strg/Cmd + P`) → „Graph-Ansicht: Graph-Ansicht öffnen“
- Lokaler Graph (nur Verbindungen der aktuellen Notiz): Befehlspalette → „Lokalen Graphen öffnen“

## Neben eine Notiz legen (geteilte Ansicht)
- Den Graph-Tab mit der Maus an den rechten Rand ziehen, oder Rechtsklick auf den Tab → „Rechts teilen“.

## Wie der Look entsteht
- **Großer Mittelpunkt:** eine Übersichtsnotiz (MOC, z. B. `_Index`), die auf viele Notizen verlinkt.
- **Farbige Gruppen:** Zahnrad oben rechts im Graph → **Gruppen** → „Neue Gruppe“, Suchfilter eintragen (z. B. `path:"20 Projekte"` oder `tag:#wissen`), Farbe wählen.
- **Lose Punkte am Rand:** Notizen ohne Links („Waisen“). Ausblenden unter Filter → „Waisen“ aus.
- **Anzeige:** Zahnrad → Anzeige → Knotengröße, Linienstärke, Pfeile. Unter Kräfte → Abstoßung, Linkabstand.

## Voraussetzung
- Der Graph wird erst dicht, wenn es viele Notizen mit vielen Wikilinks gibt.
