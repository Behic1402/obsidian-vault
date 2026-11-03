---
tags:
  - projekt
  - bau
  - tga
aliases:
  - Kranblick
  - Baustellen-Dashboard
erstellt: 2026-11-01
aktualisiert: 2026-11-01
---

# Kranblick-Tool (Baustellen-Dashboard mit TGA-Gewerken)

> [!info] Idee
> Behic will ein Tool wie im TikTok-Video von @_robintamba_ ("Unternehmenssoftware wird durch KI zum Spiel"), zusätzlich mit **TGA-Gewerken**.

## Was das Video-Tool zeigt (Analyse, 2026-11-01)
- Name im Video: **Kranblick**. Ein Projekt-Dashboard mit **isometrischer 3D-Stadtansicht** der Baustellen (Projekte Rhein-Main, 3 Baustellen BV-01..03).
- Oben KPI-Kacheln: Baufortschritt %, Handwerker vor Ort, Offene Vergaben, Terminlage (z. B. +3 Arbeitstage / im Verzug).
- Klick auf Baustelle → 3D-Gebäude mit Gerüst/Kran, Etagen (OG 1–6), Wohnungen (Whg 2.1 …), Status je Wohnung (z. B. "Elektro roh 57 %").
- Unten Leiste **Bauablauf** je Wohnung: Elektro → SHK → Fenster → Putz → Estrich → Fliesen → Maler → Boden → Türen → Reinigung.
- Panel **Gewerk vergeben**: 1 Gewerk wählen, 2 Umfang (Etagen), 3 Angebote (Preisspiegel mit Bewertung, Pünktlichkeit, Mängelquote, Empfehlung), 4 Taktplan & Prüfung (Etagen in Taktfolge, Vorlauf 2 Wochen, Warnungen), Button "Auftrag erteilen".
- Rechts Listen: Etagen, Gewerke, Mängel, Aufträge. Suche über Baustellen, Etagen, Wohnungen, Firmen, Mängel. Rolle: Bauleitung.
- Im Video wird es offenbar mit Claude/KI-Agent gebaut (Seitenleiste "Agent Host").

## Gewünschte Erweiterung
- TGA-Gewerke (HLSK, Elektro, MSR/GA usw.) einbauen. DIN 276 KG 400, Untergruppen noch prüfen (410–480).

## Status (2026-11-01)
- **Version 1 gebaut** und von unabhängigen Prüfern abgenommen. Repo: `Behic1402/kranblick-tga` (privat), Branch `claude/trusting-cori-6r02jc`.
- Vite + React + TypeScript + three.js, läuft lokal im Browser (`npm install`, `npm run dev`), Daten im Browser-Speicher, Export/Import als JSON, Beispielprojekt mit erfundenen Daten.
- Enthalten: 3D-Übersicht, Gebäudeansicht, KPI-Kacheln, Bauablauf-Leiste mit Statuswechsel, Vergabe-Assistent (Preisspiegel, Taktplan, Vorlauf-Warnung), Prüfpunkte, Mängelliste, Suche, Baustellen-Umschalter.
- TGA-Gewerke: Heizung/Sanitär, Lüftung/Kälte, Elektro, MSR/Gebäudeautomation. KG-Nummern sind als „ungeprüft" beschriftet, bis sie an der DIN 276 abgeglichen sind.
- Bekannte Lücken gegenüber dem Video: stilisiertes 3D (ca. 60 % Nähe), keine Handwerker-Kolonnen, keine Benachrichtigungen, kein Nutzerprofil, kein Login, kein IFC/BIM.
- Offene Entscheidung: Branch in `main` übernehmen (kein Pull Request angelegt).
- Verwandt: [[Kranblick-TGA Spezifikation]], [[Eigene Claude-Skills TGA]]
- Regel von Behic: Ergebnisse werden erst geliefert, nachdem ein separater Prüferagent ohne Vorwissen sie gegen die Anforderungen geprüft hat.

## Nächste Ausbaustufe: Revit-Modell (2026-11-03)
- Behic will ein Revit-Modell (.rvt) in das Tool laden. Entschieden: **Weg über IFC, lokal im Browser** (Revit exportiert IFC, Bibliothek `web-ifc`), kein Upload zu Autodesk.
- Idee: IFC-Etagen werden zu Etagen, Räume zu Zonen, TGA-Bauteile werden den vier Gewerken zugeordnet; Status, Vergabe und Mängel hängen dann am echten Modell.
- Status: Brainstorming läuft (Blindspot-Fragen), noch nichts gebaut. Direkt .rvt lesen geht im Browser nicht (geschlossenes Format).

