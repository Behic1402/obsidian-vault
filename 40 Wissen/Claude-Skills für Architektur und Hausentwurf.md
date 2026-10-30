---
tags:
  - wissen
  - claude-skills
  - architektur
  - hausbau
aliases:
  - Architektur-Skills
  - Hausentwurf-Skills
erstellt: 2026-10-30
aktualisiert: 2026-10-30
---

# Claude-Skills für Architektur und Hausentwurf

Recherche vom 2026-10-30 für [[Hausentwurf]]. Verwandt: [[Claude-Skills für HOAI und TGA]], [[Claude Skills Übersicht]], [[Eigene Claude-Skills TGA]].

## 1. Grundrisse zeichnen (läuft auch in der Cloud)
- **floor-plan** aus `markdown-viewer/skills` – Grundrisse und Möblierungspläne als draw.io-XML mit Wand-, Tür-, Fenster- und Möbelsymbolen. Installation: `npx skills add markdown-viewer/skills --skill floor-plan`
- Gleiches Repo: `architecture`, `canvas`, `mermaid` für Raumprogramm-/Funktionsdiagramme.
- Grenze: 2D-Skizze ohne Normprüfung, nicht maßstäblich wie CAD.

## 2. 3D / BIM über MCP-Server (braucht lokalen Rechner + Software)
| Werkzeug | Repo | Nutzen |
|---|---|---|
| **ifcmcp** (offiziell IfcOpenShell) | `IfcOpenShell/IfcOpenShell` → `src/ifcmcp` | IFC-Modell neu anlegen, bearbeiten, Grundriss plotten, 3D rendern, Kollisionen, Mengen. `pip install 'ifcmcp[mcp]'` |
| **Bonsai MCP** | `JotaDeRodriguez/Bonsai_mcp` | Blender + Bonsai BIM, IFC abfragen/bearbeiten |
| **BlenderMCP** | `ahujasid/blender-mcp` | Freies 3D-Modellieren, Visualisierung |
| **SketchUp MCP** | `mhyrr/sketchup-mcp` | Schnelle Massenmodelle |
| **FreeCAD MCP** | `spkane/freecad-mcp` | Parametrisches CAD (BIM-Workbench) |
| **Rhino MCP** | McNeel-Plugin für Rhino 8 (Repo nicht geprüft) | Entwurf/Grasshopper |
| **Revit MCP** | `revit-mcp` (Repo nicht geprüft) | Nur mit Revit-Lizenz |

Empfehlung: **FreeCAD oder Blender/Bonsai + ifcmcp** – kostenlos, IFC-Export für Fachplaner (TGA!).

## 3. Architektur-Plugin
- **Architecture Studio** (`AlpacaLabsLLC/skills-for-architects`), 61 Skills, 8 Agenten. `claude plugin marketplace add AlpacaLabsLLC/skills-for-architects`
- Stark US/NYC-lastig (Zoning, NYC-Behörden). Brauchbar für Hausbau DE: environmental-analysis (Sonne, Klima, Topografie), epd-research/-compare (Baustoffe, CO₂), spec-writer, product-research, skill-maker.
- Kein Grundriss- oder Massing-Skill enthalten.

## 4. Deutsches Baurecht
- `Klotzkette/claude-fuer-deutsches-recht` → Skill **bauantrag** (Bauantrag, Bauvorbescheid, Nachbarbeteiligung, Unterlagen, LBO, Fristen).
- `borghei/ai-skills-german-law` → **baugenehmigungsverfahren**.
- Erklären Verfahren, prüfen aber keinen Entwurf gegen B-Plan.

## 5. Grundriss-Generatoren (keine Skills, nur Ideenquelle)
- `sarvanithin/Buildify` – EFH-Grundrisse aus Raumwunsch, US-Code (IRC).
- `Dropio12/archigen` – Kanada, Export IFC/DXF/SVG.
- `poolpet/floorplan6` – Wohnungsaufteilung, OR-Tools, ArchiCAD.

## Lücke → eigener Skill „hausentwurf-de"
Nichts gefunden, das einen deutschen EFH-Entwurf prüft. Inhalt eines eigenen Skills:
- B-Plan-Werte: GRZ/GFZ (BauNVO), Geschosse, Baugrenzen, Dachform
- Abstandsflächen BauO NRW § 6: 0,4 H, mind. 3 m; Wohngebäude GK 1/2 mit max. 3 oberirdischen Geschossen: 3 m genügen; B-Plan/Satzung kann abweichen
- Wohnfläche nach WoFlV, Flächen nach DIN 277
- Stellflächen/Bewegungsflächen (DIN 18011, DIN 18040-2 optional)
- GEG / KfW-Standard als Randbedingung
- Ausgabe: Raumprogramm → draw.io-Grundriss → IFC über ifcmcp

> [!warning] Bauantrag
> In NRW muss den Bauantrag ein bauvorlageberechtigter Entwurfsverfasser (Architekt/berechtigter Ingenieur) unterschreiben. Claude-Entwürfe sind Vorplanung/Ideen.

## Quellen
- https://github.com/markdown-viewer/skills
- https://github.com/AlpacaLabsLLC/skills-for-architects
- https://github.com/IfcOpenShell/IfcOpenShell (src/ifcmcp)
- https://github.com/JotaDeRodriguez/Bonsai_mcp
- https://snyk.io/de/articles/6-mcp-servers-for-using-ai-to-generate-3d-models/
- https://lobehub.com/mcp/spkane-freecad-mcp
- https://claudskills.com/skills/bauantrag/
- https://github.com/ahujasid/blender-mcp
- https://github.com/mhyrr/sketchup-mcp
- https://github.com/Klotzkette/claude-fuer-deutsches-recht
- https://www.skills.sh/borghei/ai-skills-german-law/baugenehmigungsverfahren

Geprüft durch unabhängigen Agenten: markdown-viewer, Architecture Studio, ifcmcp, blender-mcp, sketchup-mcp, Klotzkette. Übrige nur aus Suchergebnissen.
