---
tags:
  - projekt
  - ki
  - voice
aliases:
  - JARVIS Voice Assistant
erstellt: 2026-11-01
aktualisiert: 2026-11-01
---

# JARVIS – Voice-AI-Assistent

Zurück zu [[20 Projekte]]

Behic hat am 2026-11-01 die `CLAUDE.md` des Repos „JARVIS" geteilt (Sprachassistent für macOS, steuert Claude Code per Stimme).

## Kernfakten
- Voice-first, läuft lokal auf dem Mac; Gehirn = langlebiger `claude -p`-Prozess (Sonnet) über das Claude-Abo, keine API-Aufrufe.
- Backend: FastAPI (`server.py`); Frontend: Vite + TypeScript + Three.js (Orb); Kommunikation per WebSocket.
- TTS: Fish Audio (API-Key nötig, kein Fallback). Mikrofon nur in Chrome.
- Jede Claude-Code-Ausführung ist ein „Run" (SQLite, `/dashboard`); Runs enden immer in einem Endzustand.
- Persönlichkeit: britischer Butler, trockener Witz, 1–2 Sätze pro Antwort.
- Langzeitgedächtnis = Markdown-Dateien (`jarvis_memory.py`).

## Setup-Kurzfassung
`.env` kopieren → Claude Code installieren/einloggen → Fish-Key → `pip install -r requirements.txt` → Playwright Chromium → `npm install` im Frontend → SSL-Zertifikate erzeugen (Pflicht!) → `python server.py --host 127.0.0.1` → `npm run dev` → Chrome auf `http://localhost:5173`.

## Offen
- Ziel/Stand von Behic mit JARVIS noch unklar (nur Datei geteilt, keine Aufgabe genannt).
