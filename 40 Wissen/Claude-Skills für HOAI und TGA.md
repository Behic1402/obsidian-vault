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

## Nach Gewerken: Heizung, Lüftung, Sanitär, Kälte, MSR
Stand 26.10.2026, gegen die Repo-Inhalte geprüft.

### Überblick
| Gewerk | Deutsche Praxis (DIN/VDI/DVGW) | Ergänzend (international, ASHRAE) |
|---|---|---|
| Heizung (KG 420) | `building-services-tga` (felixkarevo): Heizlast DIN EN 12831, GEG-Pflichten, Brennwert, Wärmepumpe und Bivalenz, Heizkörper, Fußbodenheizung, Bauteilaktivierung; `sustainable-construction` (Lebenszyklus, Ökobilanz) | `heat-transfer-engineer`, `thermodynamics-engineer` (K-Dense); `energy-simulation` (DDC): Heiz- und Kühllast, Anlagendimensionierung, ASHRAE 90.1 |
| Lüftung (KG 430) | `building-services-tga`: DIN 1946-6, DIN EN 16798-1/-3, Geräte- und Kanalauslegung, Brandschutz von Lüftungsleitungen; `fire-protection-building` (baulicher Brandschutz); `building-physics-thermal-moisture` (Feuchte, Tauwasser); `building-acoustics` (Schallschutz) | `hvac-engineer` (K-Dense): Psychrometrie, ASHRAE 62.1 |
| Sanitär (KG 410) | `building-services-tga`: Trinkwasser DIN EN 806 / DIN 1988, Legionellen DVGW W 551, Abwasser DIN 1986-100 / DIN EN 12056, Regenwasser, Rückstau | `plumber` (Haibarakiku), nach US-Codes IPC/UPC, für deutsche Planung kaum brauchbar |
| Kälte (KG 434) | kaum: in `building-services-tga` nur Kühllast-Schnellcheck und Taupunkt an Kühlflächen | `hvac-engineer` (K-Dense): Kältekreis, COP, A2L-Kältemittel, ASHRAE 15/34 |
| MSR (KG 480) | nur am Rand: `electrical-installations` Kap. 13.5 (KNX, GA-Ebenen nach VDI 3814, auf Wohnbau zugeschnitten) | `hvac-engineer` (K-Dense): Regelstrategien nach ASHRAE Guideline 36, Datenpunktliste, BACnet/IP, Trendauswertung; `control-systems-engineer` (allgemeine Regelungstechnik, SPS) |
| Pumpen, Hydraulik | – | `pump-selection-helper`, `centrifugal-pumps`, `cavitation-analysis`, `system-integration` (Soljourner) |

### Bauüberwachung und Recht (Klotzkette)
- Koordination: `fachplaner-tga-brandschutz-tragwerk-koordination`
- LP 8: `lph8-bauueberwachung-tga-rohrleitung-druckprobe`, `lph8-bauueberwachung-krankenhaus-rein-raum`. Nur teilweise TGA: `lph8-bauueberwachung-industrieanlage-medien` (Normenkern DVGW W 400, DIN EN 1610) und `lph8-bauueberwachung-rechenzentrum-rz-klima` (trotz Titel keine Klima-Norm)
- Betrieb Heizung: `heizung-warmwasser`, `heizkostenverordnung`, `weg-waermepumpe-geg` (Mietrecht und Betrieb, für Planung nachrangig)
- Legionellen: `trinkwasser-legionellen-umsatzsteuer`, eine Berichtspflichten-Vorlage mit Bezug auf TrinkwV §§ 31 und 51, fachlich dünn
- Kältemittel: `aussenwirtschaft-f-gase-ozonstoffe` behandelt nur Einfuhrkontrolle und Quoten, keine Betreiberpflichten für Kälteanlagen

### Repos
- felixkarevo/construction-skills (MIT): `npx skills add felixkarevo/construction-skills`
- K-Dense-AI/scientific-agents (MIT, 503 Skills, US-Normen). Kopie mit Installbefehl: `npx -y skills add stanfish06/skillquarium --skill hvac-engineer --agent claude-code`
- Haibarakiku/awesome-skills (MIT mit Namensnennungspflicht): `hvac-engineer`, `plumber`, eher allgemein gehalten
- Soljourner/claude-engineering-skills (MIT, letzter Commit 07.11.2025): Pumpen und Strömung
- datadrivenconstruction/DDC (MIT): `energy-simulation`
- lionelsimai/claude-skills-collection `hvac-design-guide`: laut [Skills Directory](https://www.skillsdirectory.com/skills/lionelsimai-hvac-design-guide) nur eine allgemeine Vorlage ohne Normen oder Berechnungen, nicht empfehlenswert

### Kein Skill, aber nützliche Wissensbasis
layounizinedine-lgtm/SHK-Berichte ist eine App für Berichtshefte von Anlagenmechanikern SHK. Ihre Wissensdateien (`server/ai/wissen/heizung.js`, `lueftung.js`, `sanitaer.js`, `versorgung.js`, `gas.js`) nennen u. a. VDI 3814, DIN EN ISO 16484, VDI 2078, DIN EN 378 und F-Gase-VO. Keine Lizenzdatei, daher nur als Nachschlagequelle, nicht zum Übernehmen.

### Lücken
Kein SKILL.md für Kälte nach deutscher Praxis (VDI 2078 Kühllast, EN 378, Kälteanlagenbau) und keines für MSR/Gebäudeautomation in Nichtwohngebäuden nach VDI 3814, DIN EN ISO 16484 oder AMEV. Für KG 434 und KG 480 lohnt ein eigener Skill.

## Quellen
- [K-Dense-AI/scientific-agents](https://github.com/K-Dense-AI/scientific-agents)
- [stanfish06/skillquarium](https://github.com/stanfish06/skillquarium)
- [Haibarakiku/awesome-skills](https://github.com/Haibarakiku/awesome-skills)
- [Soljourner/claude-engineering-skills](https://github.com/Soljourner/claude-engineering-skills)
- [Klotzkette/claude-fuer-deutsches-recht](https://github.com/Klotzkette/claude-fuer-deutsches-recht)
- [felixkarevo/construction-skills](https://github.com/felixkarevo/construction-skills)
- [datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction](https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction)
- [dleerdefi/claude-code-construction](https://github.com/dleerdefi/claude-code-construction)

Siehe auch: [[Über mich]]
