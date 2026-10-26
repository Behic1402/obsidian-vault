---
tags:
  - wissen
  - claude-skills
  - hoai
  - tga
aliases:
  - HOAI-Skills
  - Skills LP 0-9
erstellt: 2026-10-26
aktualisiert: 2026-10-26
---

# Claude-Skills für HOAI und TGA (GitHub-Recherche)

> [!info] Stand 26.10.2026
> Recherche nach Skills für Ingenieursarbeit nach HOAI, LP 0 bis 9. Zahlen und Namen gegen die geklonten Repos geprüft.

> [!warning] LP 0
> Die HOAI 2021 kennt keine Leistungsphase 0. Was oft so genannt wird (Projektentwicklung, Bedarfsplanung, Zielfindung nach § 650p Abs. 2 BGB), decken unten eigene Skills ab.

## 1. Klotzkette/claude-fuer-deutsches-recht
Lizenz Apache-2.0 oder MIT, letzter Commit 23.10.2026. Eigentlich für Kanzleien, Blick daher stark auf Vertrag, Haftung und Nachweis.

### Plugin „bauwirtschaft“ (29 Skills)
Je ein Skill pro LP, ausgelegt auf das Leistungsbild Gebäude und Innenräume (§ 34, Anlage 10):

| LP | Skill |
|---|---|
| „0“ | `projektziele-und-entscheidungsrahmen-festlegen` |
| 1 | `hoai-1-grundlagen-und-planungsauftrag-klaeren` |
| 2 | `hoai-2-vorplanung-und-varianten-entwickeln` |
| 3 | `hoai-3-entwurf-und-kostenberechnung-abstimmen` |
| 4 | `hoai-4-genehmigungsplanung-und-nachforderungen-bearbeiten` |
| 5 | `hoai-5-ausfuehrungsplanung-und-details-koordinieren` |
| 6 | `hoai-6-leistungsverzeichnis-und-vergabeunterlagen-erstellen` |
| 7 | `hoai-7-angebote-werten-und-vergabe-vorbereiten` |
| 8 | `hoai-8-bauueberwachung-und-dokumentation-fuehren` |
| 9 | `hoai-9-objektbetreuung-und-maengelverfolgung-organisieren`, `uebergabe-und-gewaehrleistung-organisieren` |
| alle | `hoai-phasen-und-planstaende-abgleichen` |

Querschnitt: `leistungsverzeichnis-erstellen-und-pruefen`, `bauangebote-werten-und-vergabevorschlag-erstellen`, `nachtraege-pruefen-und-vereinbaren`, `maengel-und-abnahme-bearbeiten`, `bautagebuch-und-aufmass-fuehren`, `baurechnungen-pruefen-und-zahlung-vorbereiten`, `behinderung-und-bauzeitfolgen-dokumentieren`.

Installation: [bauwirtschaft.zip](https://github.com/Klotzkette/claude-fuer-deutsches-recht/releases/latest/download/bauwirtschaft.zip)

### Plugin „hoai-leistungsphasen-praxis“ (151 Skills)
- Phasen: `lph-01-arbeitsrouter` bis `lph-09-arbeitsrouter`, `neun-phasen-ueberblick`, `lph9-gewaehrleistungsmanagement-lph8`
- Vorphase: `zielfindungsphase-bgb-650p-650r`, `projektsteuerung-vs-hoai`
- Honorar: `honorarzone-bewertungspunkte-objektliste`, `anrechenbare-kosten-din276-baukostengruppen`
- TGA-nah: `fachplaner-tga-brandschutz-tragwerk-koordination`, `ingenieur-perspektive`, `lph8-bauueberwachung-tga-rohrleitung-druckprobe`, `lph8-bauueberwachung-elektro-erdung-blitzschutz`, `lph8-bauueberwachung-rechenzentrum-rz-klima`, `lph8-bauueberwachung-industrieanlage-medien`, `lph8-bauueberwachung-krankenhaus-rein-raum`, `lph8-bauueberwachung-wasserwerk-rohrleitung`
- Sonstiges: `nachtragsmanagement-planer`, `rechnungspruefung-architekt`, `bim-cde-planmanagement`

Installation: [hoai-leistungsphasen-praxis.zip](https://github.com/Klotzkette/claude-fuer-deutsches-recht/releases/latest/download/hoai-leistungsphasen-praxis.zip)

Schwächen: Die TGA-Skills sind schablonenhaft aufgebaut. Der Druckprobe-Skill nennt noch die EnEV statt des GEG.

## 2. felixkarevo/construction-skills
Lizenz MIT, letzter Commit 26.10.2026. 33 technische Fachskills für DACH plus ein Router.
- `building-services-tga`: sehr umfangreich (rund 1.670 Zeilen), Heizlast nach DIN EN 12831, DIN-, DVGW- und VDE-Regeln
- `cost-management-din276`: DIN 276 und HOAI-Honorar (Phasengewichte LPH 1–9, anrechenbare Kosten, Honorarzonen)
- `construction-scheduling-site`: Bauablauf, auch LPH-8-Pflichten (Bauüberwachung, Bautagebuch)
- `bim-management`: ISO 19650, VDI 2552, Modelldetaillierung je LP
- `electrical-installations` (DIN VDE 0100, DIN 18015), `fire-protection-building`, `building-physics-thermal-moisture`, `building-regulations-permits`

Kein durchgehender LP-Arbeitsablauf, dafür technische Tiefe. Installation: `npx skills add felixkarevo/construction-skills`

## 3. datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction
Lizenz MIT, 238 Skills, englisch und international: Kalkulation, Nachträge (`change-order-manager`), Cashflow, Budgetabweichung, Qualitätskontrolle. HOAI praktisch nicht abgedeckt.

## 4. dleerdefi/claude-code-construction
14 Skills, US-Praxis, kein HOAI-Bezug. Nicht relevant.

## Lücke
Kein gefundener Skill bildet das Leistungsbild Technische Ausrüstung (§ 55, Anlage 15) mit LP 1–9 inhaltlich ab. Klotzkette nennt § 55 nur als Verweis.

## Empfehlung
„bauwirtschaft“ für den LP-Ablauf, dazu `building-services-tga` und `cost-management-din276` von felixkarevo für Fachtiefe und Honorar. Daraus bei Bedarf einen eigenen Skill für Anlage 15 bauen.

## Quellen
- [Klotzkette/claude-fuer-deutsches-recht](https://github.com/Klotzkette/claude-fuer-deutsches-recht)
- [felixkarevo/construction-skills](https://github.com/felixkarevo/construction-skills)
- [datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction](https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction)
- [dleerdefi/claude-code-construction](https://github.com/dleerdefi/claude-code-construction)

Siehe auch: [[Über mich]]
