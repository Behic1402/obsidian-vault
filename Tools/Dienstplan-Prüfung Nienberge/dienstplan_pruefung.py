#!/usr/bin/env python3
"""Monatliche Dienstplan-Prüfung Nienberge.

Aufruf:
  python3 dienstplan_pruefung.py --monat 2026-12 --out Pruefung_2026-12.xlsx  woche1.pdf woche2.pdf ...
  optional: --notdienst 2026-11-30   (oder: --notdienst keine)   --sondertage 12-24,12-31
"""
import argparse, json, sys, os, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apocollect_parser import parse_pdf
from analysis import analyze, SONDERTAGE_DEFAULT
from excel_report import write_report

MONATE = ["", "Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdfs", nargs="+")
    ap.add_argument("--monat", required=True, help="Prüfmonat JJJJ-MM")
    ap.add_argument("--out", required=True)
    ap.add_argument("--notdienst", default=None, help="Notdiensttermine JJJJ-MM-TT,... oder 'keine'; weggelassen = Termine unbekannt (offen)")
    ap.add_argument("--sondertage", default=",".join(SONDERTAGE_DEFAULT))
    a = ap.parse_args()
    weeks = [parse_pdf(p) for p in a.pdfs]
    nd = None if a.notdienst is None else [x for x in a.notdienst.split(",") if x and x != "keine"]
    A = analyze(weeks, notdienst=nd, sondertage=[x for x in a.sondertage.split(",") if x], monat=a.monat)
    y, m = a.monat.split("-")
    titel = f"{MONATE[int(m)]} {y}"
    kws = ", ".join(f"KW {w['kw']}" for w in A["weeks"])
    exp = ", ".join(sorted({f"{e[8:]}.{e[5:7]}.{e[:4]}" for e in A["exportdaten"]}))
    write_report(A, a.out, titel, f"Quelle: ApoCollect-Wochenexporte {kws} · Export vom {exp} · erstellt am {dt.date.today().strftime('%d.%m.%Y')}")
    print("geschrieben:", a.out)

if __name__ == "__main__":
    main()
