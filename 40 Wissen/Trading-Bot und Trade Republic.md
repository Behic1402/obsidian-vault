---
tags:
  - wissen
  - trading
  - finanzen
aliases:
  - Trading-Bot
erstellt: 2026-10-29
aktualisiert: 2026-10-29
---

# Trading-Bot und Trade Republic

Idee von Behic (2026-10-29): Ein Programm soll ~1000 € auf dem Trade-Republic-Konto selbstständig investieren, Märkte beobachten, bei Bedarf verkaufen und neu investieren.

## Kurzfazit
- **Technisch machbar**, aber bei Trade Republic nur über **inoffizielle** Schnittstellen (z. B. die Python-Bibliothek `pytr`). Es gibt **keine offizielle Handels-API**.
- Inoffizielle Zugriffe können gegen die AGB verstoßen und jederzeit brechen; Login braucht Handy-PIN und 2FA.
- Sauberer: Broker mit **offizieller API** (z. B. Interactive Brokers, Trading 212 API – Verfügbarkeit/Konditionen vorher prüfen).
- Realistisch: Selbstgebaute Bots schlagen einen simplen Welt-ETF-Sparplan selten, Kosten und Steuern fressen kleine Konten auf.

## Wenn trotzdem, dann so
1. Erst **Backtest** und **Paper-Trading** (Testkonto ohne echtes Geld).
2. Harte Limits: max. Betrag pro Order, Tagesverlust-Stopp, Notaus.
3. Einfache, nachvollziehbare Regeln statt „KI entscheidet alles".
4. Anfangs nur Vorschläge per Benachrichtigung, Freigabe von Hand.
5. Steuer: Gewinne (Abgeltungsteuer) und Dokumentation beachten.

## Verweise
- [[Über mich]]
