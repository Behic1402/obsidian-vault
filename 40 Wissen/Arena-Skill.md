---
tags:
  - wissen
  - claude
  - skill
aliases:
  - Arena
  - /arena
erstellt: 2026-10-31
aktualisiert: 2026-10-31
---

# Arena-Skill

Claude-Code-Skill von Jakeschincariol (MIT): `/arena` lässt bis zu 100 Sub-Agenten dieselbe Aufgabe mit je einer anderen Strategie lösen und in einem K.-o.-Turnier gegeneinander antreten. Zurück kommt die eine überlebende Lösung. Fasst keine Projektdateien an (schreibt nur in `.arena/`).

- Repo: https://github.com/Jakeschincariol/arena-skill
- Installiert am 2026-10-31 nach `~/.claude/skills/arena` und dauerhaft als Projekt-Skill im Vault: `.claude/skills/arena` (wird mit dem Vault in jeder Sitzung geladen).
- Nutzung: `/arena`, `/arena --quick <Aufgabe>` (16 Agenten, ~91 Aufrufe), Standard 100 Agenten (~595 Aufrufe).
- Ablauf: Spawn → Attack → Defend → Judge pro Runde, bis einer übrig ist.

Siehe [[Über mich]].
