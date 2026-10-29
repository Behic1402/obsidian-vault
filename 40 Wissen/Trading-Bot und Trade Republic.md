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

## Broker mit offizieller API (Stand Wissen 2026, vor Nutzung prüfen)
- **Interactive Brokers (IBKR)**: ausgereifte offizielle API (TWS API, Web API), Paper-Trading-Konto, für Deutsche verfügbar, günstige Gebühren. Nachteil: komplexer; deutsche Steuer wird nicht automatisch abgeführt, Erklärung selbst in der Steuererklärung.
- **Trading 212**: öffentliche API (Beta), einfacher; Umfang und Verfügbarkeit für Deutschland prüfen.
- **Alpaca**: API-first, Paper-Trading, aber US-Aktien; Zugang für Kunden aus Deutschland prüfen.
- **Krypto** (Kraken, Binance, Bitpanda): gute APIs, aber ganz anderes Risikoprofil.
- Ohne offizielle API (wie Trade Republic): Scalable, DEGIRO, flatex, comdirect u. a.

## Verweise
- [[Über mich]]
