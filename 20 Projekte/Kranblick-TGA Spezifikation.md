---
tags:
  - projekt
  - spezifikation
  - tga
aliases:
  - Kranblick TGA Spec
erstellt: 2026-11-01
aktualisiert: 2026-11-01
---

# Kranblick TGA – Spezifikation (Entwurf zur Prüfung)

Gehört zu [[Kranblick-Tool]]. Basiert auf der Analyse des Videos von @_robintamba_ und den Entscheidungen vom 2026-11-01.

## Entscheidungen
| Thema | Entscheidung |
|---|---|
| Zweck | Eigene TGA-Projekte, Planer-/Bauleiter-Sicht, ein Nutzer |
| Darstellung | Stilisiertes isometrisches 3D (three.js), klickbar, ohne IFC/BIM |
| TGA-Gewerke | Heizung+Sanitär, Lüftung+Kälte, Elektro, MSR/Gebäudeautomation |
| Technik | Vite + React + TypeScript + react-three-fiber, lokal im Browser, kein Server, kein Login |
| Daten | Browser-Speicher (localStorage), Export/Import als JSON, Beispielprojekt mit erfundenen Zahlen |

## Muss-Funktionen (Version 1)
1. **Übersicht:** Isometrische Karte mit mehreren Baustellen, Namensschild je Baustelle (Name, % fertig, Phase). Kennzahlen-Kacheln: Baufortschritt, Handwerker vor Ort, offene Vergaben, Terminlage (Arbeitstage Verzug).
2. **Gebäudeansicht:** Gebäude aus Etagen und Zonen/Räumen generiert, drehbar, klickbar. Farbe zeigt Gewerkestatus. Seitenliste Etagen/Gewerke/Mängel/Aufträge.
3. **Bauablauf-Leiste** je Raum/Zone mit den TGA-Schritten: Rohinstallation Heizung/Sanitär, Lüftung/Kälte, Elektro, MSR/GA, Inbetriebnahme, Abnahme, Dokumentation. Status je Schritt (offen, wartet, in Arbeit, fertig, verzögert).
4. **Vergabe-Assistent:** Gewerk, Umfang (Etagen), Angebote im Preisspiegel (Preis, Bewertung, Pünktlichkeit, Mängelquote, Empfehlung), Taktplan mit Vorlauf und Warnungen, Auftrag erteilen.
5. **TGA-Prüfpunkte** je Gewerk (z. B. Druckprobe, Dichtheitsprüfung, Datenpunktliste, Funktionsprüfung, Revisionsunterlagen).
6. **Mängelliste** je Gewerk und Raum, Status offen/behoben.
7. **Suche** über Baustellen, Etagen, Räume, Firmen, Mängel.
8. **Export/Import** als JSON, Beispielprojekt nach Vorbild Bildungsquartier Annen (nur erfundene Werte).

## Nicht in Version 1
Login und mehrere Nutzer, IFC/BIM, KI-Funktionen, echte Schnittstellen zu Planungsprogrammen.

## Offene Punkte
- KG-Nummern nach DIN 276 (410 bis 480) erst anhand der Norm bestätigen, bis dahin nur als Beschriftung.
- Wohin kommt der Code? Eigenes GitHub-Repo, Name wählt Behic.

## Qualitätssicherung
Vor Lieferung prüft ein separater Agent ohne Vorwissen die fertige App gegen diese Spezifikation (Prüferagent-Regel).

## Abnahmekriterien
- App startet mit `npm run dev`, Beispielprojekt sichtbar, 3D-Ansicht dreh- und klickbar.
- Alle Muss-Funktionen 1 bis 8 bedienbar, Datenverlust beim Neuladen ausgeschlossen.
- Build ohne Fehler, Tests für Terminlage, Preisspiegel und Taktplan grün.
