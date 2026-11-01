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

## Status
- Brainstorming läuft, noch nichts gebaut.
- Open-Source-Vorlage zur Orientierung: Civora-Dashboard (Next.js, Tailwind, shadcn).
