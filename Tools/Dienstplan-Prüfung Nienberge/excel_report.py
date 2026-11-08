"""Schreibt die farblich bewertete Excel-Prüfdatei."""
import datetime as dt, collections
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter as CL
from analysis import *

# Farben (nur als Zellhintergrund; keine Farbnamen in den Ergebniszellen)
RED, YEL, LGR, DGR, PINK, GREY, NEUT, HEAD, BAND = "F4A6A6", "FFE699", "C6E7B8", "6FBF73", "F7C6E0", "BFBFBF", "F2F2F2", "1F3864", "D9E1F2"
def fill(c): return PatternFill("solid", start_color=c, end_color=c)
thin = Side(style="thin", color="BBBBBB"); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
WRAP = Alignment(wrap_text=True, vertical="top"); CEN = Alignment(horizontal="center", vertical="center", wrap_text=True)
BOLD = Font(bold=True); WHITE = Font(bold=True, color="FFFFFF")


def tot_color(ist, soll):
    d = ist - soll
    return RED if d < 0 else YEL if d == 0 else LGR if d == 1 else DGR if d == 2 else PINK


def app_color(ist, soll):
    if soll == 0: return NEUT
    return RED if ist == 0 else LGR if ist == 1 else DGR if ist == 2 else PINK


def short(n):
    if "," not in n: return n
    a, b = [x.strip() for x in n.split(",", 1)]
    return f"{a} {b[0]}."


def setw(ws, widths):
    for i, w in enumerate(widths, 1): ws.column_dimensions[CL(i)].width = w


def head(ws, row, cols, color=HEAD):
    for i, c in enumerate(cols, 1):
        x = ws.cell(row, i, c); x.fill = fill(color); x.font = WHITE; x.alignment = CEN; x.border = BOX


def put(ws, r, c, v, fillc=None, bold=False, wrap=True, align=None):
    x = ws.cell(r, c, v)
    x.border = BOX; x.alignment = align or (WRAP if wrap else Alignment(vertical="top"))
    if fillc: x.fill = fill(fillc)
    if bold: x.font = BOLD
    return x


def banner(ws, r, text, ncols, color=BAND, bold=True, size=11):
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncols)
    x = ws.cell(r, 1, text); x.fill = fill(color); x.font = Font(bold=bold, size=size); x.alignment = Alignment(vertical="center", wrap_text=True)


def rng(a, b): return f"{fmt(a)}–{fmt(b)}"
def mm(lo, hi): return f"{lo}" if lo == hi else f"{lo}–{hi}"


def put_date(ws, r, c, d, im_monat, fillc=None):
    x = put(ws, r, c, dstr(d), fillc)
    if not im_monat:
        x.font = Font(italic=True, color="7F7F7F")
    return x


def block_hint(r, d):
    parts = []
    if r["bestaetigt_gesamt"] or r["bestaetigt_app"]:
        parts.append("Unterbesetzung bestätigt (siehe Detail)")
    if r["unsicher_gesamt"] or r["unsicher_app"]:
        parts.append("nicht eindeutig: Soll nur mit unsicher anrechenbarer Person (überbrückte Pause, anderer Bereich) erreichbar")
    for x in r.get("pause", []):
        pn = ", ".join(f"{short(p['name'])} {fmt(p['start'])}" for p in x["pausen"])
        zus = "gestaffelt rechnerisch möglich" if x.get("staffelbar", True) else "auch bei freier Staffelung nicht abdeckbar"
        parts.append(f"Pausenabstimmung erforderlich: {rng(x['a'], x['b'])} {x['kind']} nur {x['ist']} (Soll {x['soll']}), wenn alle zur Richtzeit pausieren ({pn}); {zus}")
    if r.get("ueber_max"):
        parts.append(f"Mangel: bis zu {r['ueber_max']} Personen, Samstag genau 3 (mind. und max. 3) – Überbesetzung")
    if "ziel_text" in r:
        if r.get("ziel_abw"): parts.append(r["ziel_text"] + " – Zielzusammensetzung weicht ab")
        elif r.get("ziel_ok") and r.get("ziel_ueber"): parts.append(r["ziel_text"] + " – Zusammensetzung über dem Ziel")
        elif r.get("ziel_ok"): parts.append(r["ziel_text"] + " – Ziel erfüllt")
        else: parts.append(r["ziel_text"] + " – Zielzusammensetzung nicht beurteilbar, solange Mindestzahl nicht erfüllt")
    if r["tmax"] > r["tmin"] and r["tmin"] >= r["tsoll"] and not parts:
        pass
    return "\n".join(parts)


def write_report(A, path, titel, quelle_text):
    wb = Workbook()
    ws0 = wb.active; ws0.title = "Übersicht"
    wsW = wb.create_sheet("Wochenübersicht")
    wsK = wb.create_sheet("KBO-Labor-Notdienst")
    wsD = wb.create_sheet("Detail Engpässe")
    wsC = wb.create_sheet("Prüfkandidaten")
    wsR = wb.create_sheet("Raster 15 Min")
    wsS = wb.create_sheet("Dienste bereinigt")
    N = A["N"]
    notd = A.get("notdienst", {})
    # -------- Wochenübersicht
    ncol = 9
    setw(wsW, [9, 12, 6, 24, 9, 12, 17, 12, 70])
    wsW.merge_cells("A1:I1"); wsW["A1"] = f"Dienstplan-Prüfung Nienberge – {titel}"; wsW["A1"].font = Font(bold=True, size=14)
    wsW.merge_cells("A2:I2"); wsW["A2"] = "Besetzung ohne Abzug flexibler Mittagspausen"; wsW["A2"].font = Font(bold=True, size=12, color="C00000")
    wsW.merge_cells("A3:I3"); wsW["A3"] = ("Ist = Minimum–Maximum innerhalb des Zeitblocks (gleiche Werte: eine Zahl). Gefärbt wird nach dem Minimum. "
                                          "Nur anrechenbare Personen in Nienberge (JZN, PBO, KBO, Labor); nicht approbierte Laborpersonen zählen im Labor nicht mit.")
    wsW["A3"].alignment = WRAP; wsW.row_dimensions[3].height = 30
    head(wsW, 5, ["Woche", "Datum", "Tag", "Zeitblock", "Gesamt Soll", "Gesamt Ist (Min–Max)", "Appro. Soll", "Appro. Ist (Min–Max)", "Hinweise"])
    wsW.freeze_panes = "A6"
    r = 6; cur_kw = None
    weeks = {w["kw"]: w for w in A["weeks"]}
    for day in A["tage"]:
        d = day["datum"]
        if day["status"] == "sonntag" and not any(s["datum"] == d.isoformat() for s in N["shifts"]):
            continue
        if day["kw"] != cur_kw:
            cur_kw = day["kw"]; w = weeks[cur_kw]
            plan = "Soll-Zeiten (Plan); kursiv grau = Tag außerhalb des Prüfmonats" if w["plan"] else "Achtung: kann Ist-Zeiten enthalten (Plan und Ist gemischt)"
            exp = w["export"]; expd = f"{exp[8:]}.{exp[5:7]}.{exp[:4]}" if exp else "?"
            banner(wsW, r, f"KW {cur_kw}  ·  {dstr(w['von'])} – {dstr(w['bis'])}  ·  {plan}  ·  Export vom {expd}", ncol, BAND, True, 12)
            r += 1
        lab = f"{day['wd']}"
        mon_note = "" if day["im_monat"] else "\n(außerhalb Prüfmonat)"
        if day["status"] in ("sonder", "feiertag", "sonntag"):
            put(wsW, r, 1, f"KW {day['kw']}"); put_date(wsW, r, 2, d, day["im_monat"]); put(wsW, r, 3, lab)
            wsW.merge_cells(start_row=r, start_column=4, end_row=r, end_column=9)
            if day["status"] == "sonder":
                txt = "Sonderregel (24.12./31.12.): nur 08:00–13:00 geöffnet, immer genau 3 Personen – manuell zu prüfen, hier nicht bewertet."; col = NEUT
            elif day["status"] == "feiertag":
                has = any(s['datum'] == d.isoformat() for s in N['shifts'])
                txt = "Feiertag – Apotheke geschlossen, nicht geprüft (entfällt)." + (" ACHTUNG, Dienste eingetragen: " + ", ".join(sorted({s['name'] for s in N['shifts'] if s['datum'] == d.isoformat()})) if has else "")
                col = GREY if has else NEUT
            else:
                txt = "Sonntag mit eingetragenen Diensten – keine Öffnungszeit definiert, nicht bewertet."; col = GREY
            put(wsW, r, 4, txt, col)
            wsW.row_dimensions[r].height = 32
            r += 1; continue
        r0 = r
        for blk in day["blocks"]:
            tc = tot_color(blk["tmin"], blk["tsoll"])
            ac = app_color(blk["amin"], blk["asoll"])
            put(wsW, r, 1, f"KW {day['kw']}"); put_date(wsW, r, 2, d, day["im_monat"]); put(wsW, r, 3, lab)
            put(wsW, r, 4, blk["label"]); put(wsW, r, 5, blk["tsoll"], align=CEN)
            put(wsW, r, 6, mm(blk["tmin"], blk["tmax"]), tc, align=CEN)
            if blk["asoll"] == 0:
                put(wsW, r, 7, "nicht erforderlich", NEUT, align=CEN)
                put(wsW, r, 8, mm(blk["amin"], blk["amax"]), NEUT, align=CEN)
            else:
                put(wsW, r, 7, blk["asoll"], align=CEN); put(wsW, r, 8, mm(blk["amin"], blk["amax"]), ac, align=CEN)
            h = block_hint(blk, d)
            put(wsW, r, 9, h)
            if h: wsW.row_dimensions[r].height = max(15, 15 * (h.count("\n") + 1 + len(h) // 90))
            r += 1
        if day.get("typ") == "wd" or True:
            pass
    wsW.sheet_view.zoomScale = 90
    # -------- KBO / Labor / Notdienst
    setw(wsK, [9, 12, 6, 30, 30, 30, 30, 30, 50])
    wsK.merge_cells("A1:I1"); wsK["A1"] = f"KBO, Labor und Notdienst – {titel}"; wsK["A1"].font = Font(bold=True, size=14)
    wsK.merge_cells("A2:I2"); wsK["A2"] = ("KBO: Zuordnung zum Prüfzeitpunkt (Mo–Fr 10:00 und 16:00, Sa 10:00; nur Bereichszuordnung KBO, keine Überbrückung). "
                                           "Labor Mo/Mi/Fr: je eine approbierte und eine nicht approbierte Person im Tagesverlauf. Notdienst: 09:00 bis 09:00 Folgetag durchgehend approbiert.")
    wsK["A2"].alignment = WRAP; wsK.row_dimensions[2].height = 34
    head(wsK, 4, ["Woche", "Datum", "Tag", "KBO 10:00", "KBO 16:00", "Labor nicht approbiert", "Labor approbiert", "Notdienst", "Hinweise"])
    wsK.freeze_panes = "A5"
    r = 5; cur_kw = None
    for day in A["tage"]:
        d = day["datum"]
        if day["status"] == "sonntag" and not any(s["datum"] == d.isoformat() for s in N["shifts"]): continue
        if day["kw"] != cur_kw:
            cur_kw = day["kw"]; w = weeks[cur_kw]
            banner(wsK, r, f"KW {cur_kw}  ·  {dstr(w['von'])} – {dstr(w['bis'])}", 9, BAND, True, 12); r += 1
        put(wsK, r, 1, f"KW {day['kw']}"); put_date(wsK, r, 2, d, day["im_monat"]); put(wsK, r, 3, day["wd"])
        hint = []
        if day["status"] != "pruefen":
            txt, col = (("manuell zu prüfen (Sonderregel)", NEUT) if day["status"] == "sonder" else ("entfällt (Feiertag, geschlossen)", NEUT) if day["status"] == "feiertag" else ("Sonntag – nicht bewertet", GREY))
            for c in range(4, 9):
                if c == 8 and day["status"] == "sonder":
                    put(wsK, r, c, "offen – Termine fehlen" if not A["notdienst_bekannt"] else "entfällt", GREY if not A["notdienst_bekannt"] else NEUT)
                else:
                    put(wsK, r, c, txt, col)
            if A["notdienst_termine"] == [] and day["status"] != "sonder": pass
            put(wsK, r, 9, ""); r += 1; continue
        # KBO
        for ci, k in enumerate(("10:00", "16:00")):
            c = 4 + ci
            if k not in day["kbo"]:
                put(wsK, r, c, "entfällt", NEUT); continue
            pers, br = day["kbo"][k]
            if pers:
                put(wsK, r, c, "\n".join(f"{short(n)} {fmt(a)}–{fmt(b)}" for n, a, b, be in pers), "A9D18E")
                # Pausenrichtzeit überlappt Prüfzeitpunkt?
                m = A["models"][d][0]
                tt = tmin(k)
                if all(any(p["name"] == n and p["start"] <= tt < p["start"] + p["dur"] and p["quelle"] == "P" for p in m.pauses) for n, a, b, be in pers):
                    hint.append(f"KBO {k}: Pausenrichtzeit der eingetragenen Person überlappt den Prüfzeitpunkt")
            elif br:
                put(wsK, r, c, f"nicht eindeutig prüfbar: nur durch überbrückte Pause ({', '.join(short(x) for x in br)})", GREY)
            else:
                put(wsK, r, c, "nicht erfüllt: keine KBO-Zuordnung", RED)
        # Labor
        app, nap, unk = day["lab"]
        if d.weekday() in LAB_DAYS:
            put(wsK, r, 6, fmt_people_short(nap) if nap else ("nicht eindeutig prüfbar: Berufsgruppe unklar – " + fmt_people_short(unk) if unk else "nicht erfüllt: keine nicht approbierte Laborperson"),
                "A9D18E" if nap else (GREY if unk else RED))
            put(wsK, r, 7, fmt_people_short(app) if app else "nicht erfüllt: keine approbierte Laborperson", "A9D18E" if app else RED)
        else:
            put(wsK, r, 6, "entfällt" + (f" (eingetragen: {fmt_people_short(nap)})" if nap else ""), NEUT)
            put(wsK, r, 7, "entfällt" + (f" (eingetragen: {fmt_people_short(app)})" if app else ""), NEUT)
        # Notdienst
        if not A["notdienst_bekannt"]:
            put(wsK, r, 8, "offen – Termine fehlen", GREY)
        elif d in A["notdienst_termine"]:
            nd = notd[d]
            if nd["missing_day"]: put(wsK, r, 8, "nicht eindeutig prüfbar: Folgetag nicht im Export", GREY)
            elif nd["gaps"]: put(wsK, r, 8, "nicht erfüllt: Lücke " + ", ".join(rng(a, b) for a, b in nd["gaps"]), RED)
            else:
                ps = []
                for n, a, b in sorted(nd["persons"], key=lambda x: x[1]): ps.append(f"{short(n)} {fmt(a % M)}–" + ("23:59" if b == M else fmt(b % M if b % M else M)))
                put(wsK, r, 8, "durchgehend gedeckt\n" + "\n".join(ps), "A9D18E")
        else:
            put(wsK, r, 8, "entfällt", NEUT)
        put(wsK, r, 9, "\n".join(hint))
        r += 1
    # -------- Detail Engpässe
    setw(wsD, [12, 6, 20, 24, 14, 12, 8, 52, 70])
    wsD.merge_cells("A1:I1"); wsD["A1"] = "Detailübersicht der Engpässe und Hinweise"; wsD["A1"].font = Font(bold=True, size=14)
    r = 3
    banner(wsD, r, "1 · Bestätigte Unterbesetzungen (Besetzung ohne Abzug flexibler Mittagspausen)", 9, "F4A6A6", True, 12); r += 1
    head(wsD, r, ["Datum", "Tag", "Zeitraum", "Zeitblock", "Art", "Ist", "Soll", "Anrechenbar anwesend", "Erklärung (nicht mitgezählt)"]); r += 1
    conf = [b for b in A["befunde"] if b["art"] == "bestätigt"]
    for b in conf:
        put(wsD, r, 1, dstr(b["datum"])); put(wsD, r, 2, WD[b["datum"].weekday()]); put(wsD, r, 3, rng(b["von"], b["bis"])); put(wsD, r, 4, b["block"])
        put(wsD, r, 5, b["kind"]); put(wsD, r, 6, b["ist"], RED, align=CEN); put(wsD, r, 7, b["soll"], align=CEN)
        put(wsD, r, 8, "\n".join(b["zaehlt"]) or "niemand"); put(wsD, r, 9, "\n".join(b["nicht"]) or "keine weiteren Dienste im Zeitraum")
        r += 1
    if not conf:
        put(wsD, r, 1, "keine"); r += 1
    r += 1
    # Zusatzprüfungen nicht erfüllt
    banner(wsD, r, "1b · Nicht erfüllte Zusatzprüfungen (KBO, Labor)", 9, "F4A6A6", True, 12); r += 1
    head(wsD, r, ["Datum", "Tag", "Prüfung", "Ergebnis", "", "", "", "", ""]); wsD.merge_cells(start_row=r, start_column=4, end_row=r, end_column=9); r += 1
    zus = 0
    for day in A["tage"]:
        if day["status"] != "pruefen": continue
        d = day["datum"]
        for k in KBO_TIMES.get(day["typ"], []):
            pers, br = day["kbo"][k]
            if not pers:
                put(wsD, r, 1, dstr(d)); put(wsD, r, 2, day["wd"]); put(wsD, r, 3, f"KBO {k}")
                wsD.merge_cells(start_row=r, start_column=4, end_row=r, end_column=9); put(wsD, r, 4, "nicht eindeutig prüfbar (nur Pausenüberbrückung)" if br else "keine Person dem KBO zugeordnet", GREY if br else RED); zus += 1; r += 1
        if d.weekday() in LAB_DAYS:
            app, nap, unk = day["lab"]
            if not nap:
                put(wsD, r, 1, dstr(d)); put(wsD, r, 2, day["wd"]); put(wsD, r, 3, "Labor nicht approbiert"); wsD.merge_cells(start_row=r, start_column=4, end_row=r, end_column=9); put(wsD, r, 4, "keine nicht approbierte Laborperson" if not unk else "Berufsgruppe unklar", RED if not unk else GREY); zus += 1; r += 1
            if not app:
                put(wsD, r, 1, dstr(d)); put(wsD, r, 2, day["wd"]); put(wsD, r, 3, "Labor approbiert"); wsD.merge_cells(start_row=r, start_column=4, end_row=r, end_column=9); put(wsD, r, 4, "keine approbierte Laborperson", RED); zus += 1; r += 1
    if not zus: put(wsD, r, 1, "keine"); r += 1
    r += 1
    banner(wsD, r, "1c · Samstag: genau 3 Personen (mind. und max. 3) – Überbesetzung ist ein Mangel", 9, "F4A6A6", True, 12); r += 1
    head(wsD, r, ["Datum", "Tag", "Zeitraum", "Zeitblock", "Art", "Ist", "Soll (max.)", "Anrechenbar anwesend", ""]); r += 1
    for u in A["ueber"]:
        put(wsD, r, 1, dstr(u["datum"])); put(wsD, r, 2, WD[u["datum"].weekday()]); put(wsD, r, 3, rng(u["von"], u["bis"])); put(wsD, r, 4, u["block"])
        put(wsD, r, 5, "Überbesetzung"); put(wsD, r, 6, u["ist"], RED, align=CEN); put(wsD, r, 7, 3, align=CEN); put(wsD, r, 8, "\n".join(u["personen"])); r += 1
    if not A["ueber"]: put(wsD, r, 1, "keine"); r += 1
    r += 1
    banner(wsD, r, "2 · Hinweise zur flexiblen Pausenverteilung – „Pausenabstimmung erforderlich“ (keine feste Unterbesetzung; rot markierte Zeilen = auch bei freier Staffelung nicht abdeckbar)", 9, "FFE699", True, 12); r += 1
    wsD.merge_cells(start_row=r, start_column=1, end_row=r, end_column=9)
    wsD.cell(r, 1, "Rechnerisches Szenario für die Gesamtbesetzung: alle eingetragenen Pausen (Dauer laut Export) liegen genau zur Richtzeit bzw. an der Dienstlücke. Die tatsächlichen Pausen werden täglich gestaffelt; das Szenario zeigt nur, wo abgestimmt werden muss. Approbierte in Pause bleiben in der Apotheke und zählen für die Mindestzahl Approbierte weiter (Entscheidung Behic).").alignment = WRAP
    wsD.row_dimensions[r].height = 30; r += 1
    head(wsD, r, ["Datum", "Tag", "Zeitraum", "Zeitblock", "Art", "Ist bei Pausen", "Soll", "Besetzung ohne Pausenabzug (Min im Zeitraum)", "Pausen in diesem Zeitraum (Richtzeit, Dauer)"]); r += 1
    for d, x in A["pausen"]:
        put(wsD, r, 1, dstr(d)); put(wsD, r, 2, WD[d.weekday()]); put(wsD, r, 3, rng(x["a"], x["b"])); put(wsD, r, 4, x["label"]); put(wsD, r, 5, x["kind"])
        put(wsD, r, 6, x["ist"], YEL, align=CEN); put(wsD, r, 7, x["soll"], align=CEN); put(wsD, r, 8, f"Ohne Pausenabzug min. {x['ohne']}; " + ("gestaffelt rechnerisch möglich (Annahme: Pause frei im Dienst, ±2 h um Richtzeit)" if x.get("staffelbar", True) else "AUCH bei freier Staffelung der Pausen innerhalb der Dienste nicht abdeckbar – Klärung nötig"), None if x.get("staffelbar", True) else RED)
        put(wsD, r, 9, "; ".join(f"{short(p['name'])} {fmt(p['start'])} ({p['dur']} min{', Lücke' if p['quelle'] == 'Lücke' else ''})" for p in x["pausen"])); r += 1
    if not A["pausen"]: put(wsD, r, 1, "keine"); r += 1
    r += 1
    banner(wsD, r, "3 · Datenpflegehinweise (kein Besetzungsmangel)", 9, "D9E1F2", True, 12); r += 1
    head(wsD, r, ["Datum", "", "Art", "", "Person", "", "", "Hinweis", ""]); r += 1
    seen = set()
    for typ, person, datum, txt in A["daten"]:
        key = (typ, person, datum, txt)
        if key in seen: continue
        seen.add(key)
        put(wsD, r, 1, datum); put(wsD, r, 3, typ); put(wsD, r, 5, person); wsD.merge_cells(start_row=r, start_column=8, end_row=r, end_column=9); put(wsD, r, 8, txt)
        wsD.row_dimensions[r].height = 30 if len(txt) > 70 else 16; r += 1
    r += 1
    banner(wsD, r, "4 · Offene Prüfungen (fehlende oder unklare Angaben)", 9, GREY, True, 12); r += 1
    head(wsD, r, ["Datum", "", "Thema", "", "", "", "", "Beschreibung", "Betroffen"]); r += 1
    offen = list(A["offen"])
    if not A["notdienst_bekannt"]:
        offen.insert(0, ("gesamter Zeitraum", "Notdienstprüfung offen – Termine fehlen", ""))
    offen.insert(1 if not A["notdienst_bekannt"] else 0, ("24.12. und 31.12.", "Sonderregel (08:00–13:00, immer 3 Personen): vorerst manuelle Prüfung, hier nicht bewertet", ""))
    for b in A["befunde"]:
        if b["art"] == "offen":
            offen.append((dstr(b["datum"]), f"Nicht eindeutig: {rng(b['von'], b['bis'])} {b['kind']} {b['ist']} (Soll {b['soll']}), Soll nur mit unsicher anrechenbarer Person erreichbar", "; ".join(b["nicht"])))
    for dd, txt, who in offen:
        put(wsD, r, 1, dd); wsD.merge_cells(start_row=r, start_column=3, end_row=r, end_column=8); put(wsD, r, 3, txt, GREY); put(wsD, r, 9, who)
        wsD.row_dimensions[r].height = 30 if len(txt) > 90 else 16; r += 1
    # -------- Prüfkandidaten
    setw(wsC, [12, 6, 24, 18, 44, 22, 26, 26, 52])
    wsC.merge_cells("A1:I1"); wsC["A1"] = "Prüfkandidaten für Überstundenabbau oder zusätzliche Freistellung"; wsC["A1"].font = Font(bold=True, size=14)
    wsC.merge_cells("A2:I2")
    wsC["A2"] = ("Nur Prüfkandidaten, keine Zusage. Rechnerisch geprüft: Gesamt- und Approbiertenbesetzung je Zeitblock, Auf-/Abschließen, KBO 10/16 Uhr, Labor Mo/Mi/Fr (Berufsgruppe der Person berücksichtigt). "
                 "Nicht berücksichtigt: Notdienst (Tage mit Notdienst werden ausgelassen), tatsächliche Pausenstaffelung, persönliche Umstände. Eine rosa Gesamtbesetzung allein bedeutet nicht, dass jede Person frei bekommen kann. "
                 "Gezeigt werden Tage ohne bestätigte Unterbesetzung, ohne unsichere Anrechnung, ohne Notdienst (Notdienstdatum und Folgetag) und mit erfüllten Zusatzprüfungen. An Notdiensttagen werden keine Kürzungen vorgeschlagen. Abschnitte über Mitternacht ohne bekannten Notdienst werden ebenfalls ausgelassen.")
    wsC["A2"].alignment = WRAP; wsC.row_dimensions[2].height = 62
    head(wsC, 4, ["Datum", "Tag", "Person", "Berufsgruppe", "Dienst (Bereich)", "Ganzer Dienst", "Später beginnen möglich bis", "Früher enden möglich ab", "Hinweise"])
    wsC.freeze_panes = "A5"
    r = 5
    for k in A["kandidaten"]:
        d = k["datum"]
        put_date(wsC, r, 1, d, (A["monat"] is None or d.strftime("%Y-%m") == A["monat"])); put(wsC, r, 2, WD[d.weekday()]); put(wsC, r, 3, short(k["name"]))
        put(wsC, r, 4, k["gruppe"]); put(wsC, r, 5, k["dienste"])
        notes = []
        if k["ganz"]:
            put(wsC, r, 6, "rechnerisch möglich", "A9D18E"); put(wsC, r, 7, "–", NEUT); put(wsC, r, 8, "–", NEUT)
            if k["pause_neu"]: notes.append("danach Pausenabstimmung zusätzlich erforderlich")
        else:
            put(wsC, r, 6, "nicht möglich", RED)
            notes.append("Ganzer Dienst nicht möglich: " + k["ganz_grund"].split("; ")[0])
            if k["start_bis"] and k["start_bis"] - k["orig_start"] >= 60:
                put(wsC, r, 7, f"{fmt(k['start_bis'])} (statt {fmt(k['orig_start'])})", LGR)
                if k["rest_start"] < 60: notes.append(f"Später beginnen: danach nur noch {k['rest_start']} min Dienst im ersten Abschnitt")
            else: put(wsC, r, 7, "–", NEUT)
            if k["ende_ab"] and k["orig_ende"] - k["ende_ab"] >= 60:
                put(wsC, r, 8, f"{fmt(k['ende_ab'])} (statt {fmt(k['orig_ende'] if k['orig_ende'] < M else M)})", LGR)
                if k["rest_end"] < 60: notes.append(f"Früher enden: davor nur noch {k['rest_end']} min Dienst im letzten Abschnitt")
            else: put(wsC, r, 8, "–", NEUT)
            notes.append("Teilzeiträume sind Reserve nur in einem einzelnen Abschnitt, keine Freistellung des ganzen Dienstes.")
        put(wsC, r, 9, "\n".join(notes))
        wsC.row_dimensions[r].height = 15 * (1 + sum(1 + len(n) // 55 for n in notes)); r += 1
    # -------- Raster 15 Min
    slots = list(range(tmin("07:45"), tmin("19:00"), 15))
    wsR.column_dimensions["A"].width = 12; wsR.column_dimensions["B"].width = 5; wsR.column_dimensions["C"].width = 11
    for i in range(len(slots)): wsR.column_dimensions[CL(4 + i)].width = 4.6
    wsR.merge_cells(start_row=1, start_column=1, end_row=1, end_column=30); wsR["A1"] = "Raster je 15 Minuten (Minimum im Zeitfenster) – Besetzung ohne Abzug flexibler Mittagspausen"; wsR["A1"].font = Font(bold=True, size=13)
    wsR.merge_cells(start_row=2, start_column=1, end_row=2, end_column=30); wsR["A2"] = "Zusatzblatt zur schnellen Sichtung. Farben wie in der Wochenübersicht. Zelle = niedrigste Anzahl anrechenbarer Personen in den 15 Minuten ab der Spaltenzeit."
    head(wsR, 4, ["Datum", "Tag", "Zeile"] + [fmt(s) for s in slots])
    wsR.freeze_panes = "D5"
    for i in range(len(slots)): wsR.cell(4, 4 + i).alignment = Alignment(text_rotation=90, horizontal="center")
    wsR.row_dimensions[4].height = 38
    r = 5
    for day in A["tage"]:
        if day["status"] != "pruefen": continue
        cnt = day["cnt"]
        for ri, (lab, key, idx) in enumerate((("Gesamt", "tot", 0), ("Approbierte", "app", 1))):
            put(wsR, r, 1, dstr(day["datum"]) if ri == 0 else "", bold=True); put(wsR, r, 2, day["wd"] if ri == 0 else ""); put(wsR, r, 3, lab)
            for si, s in enumerate(slots):
                blk = next((b for b in day["blocks"] if b["a"] <= s < b["b"]), None)
                v = int(cnt[key][s:s + 15].min())
                if blk is None:
                    put(wsR, r, 4 + si, "", NEUT, align=CEN)
                else:
                    soll = blk["tsoll"] if idx == 0 else blk["asoll"]
                    col = tot_color(v, soll) if idx == 0 else app_color(v, soll)
                    put(wsR, r, 4 + si, v, col, align=CEN)
            r += 1
    # -------- Dienste bereinigt
    setw(wsS, [12, 6, 24, 18, 18, 8, 8, 10, 28, 14, 30, 18])
    wsS.merge_cells("A1:L1"); wsS["A1"] = "Dienste (bereinigt, doppelte Darstellungen zusammengeführt) – Datengrundlage der Prüfung"; wsS["A1"].font = Font(bold=True, size=13)
    head(wsS, 3, ["Datum", "Tag", "Person", "Berufsbezeichnung (Export)", "Wertung", "von", "bis", "Bereich", "Tätigkeit", "Pause (Richtzeit)", "Zählt in Nienberge?", "Quelle (Bereichsabschnitt)"])
    wsS.freeze_panes = "A4"; wsS.auto_filter.ref = "A3:L3"
    r = 4
    items = []
    mon = A["monat"]
    for s in N["shifts"]:
        if mon and s["datum"][:7] > mon: continue
        items.append((s["datum"], s["name"], s["von"], s))
    for (nm, datum), txts in N["abwesend"].items():
        if mon and datum[:7] > mon: continue
        items.append((datum, nm, "99", {"abs": sorted(txts)}))
    items.sort(key=lambda x: (x[0], x[1], x[2]))
    for datum, nm, _, s in items:
        d = D(datum); rol = N["personen"][nm]["rolle"]; g = group_of(nm, rol)
        put(wsS, r, 1, dstr(d)); put(wsS, r, 2, WD[d.weekday()]); put(wsS, r, 3, nm); put(wsS, r, 4, rol or "– (fehlt)")
        put(wsS, r, 5, {"approbiert": "approbiert", "nicht_approbiert": "nicht approbiert", "unklar": "unklar"}[g])
        if "abs" in s:
            put(wsS, r, 6, ""); put(wsS, r, 7, ""); put(wsS, r, 8, "–"); put(wsS, r, 9, "Abwesenheit: " + ", ".join(s["abs"])); put(wsS, r, 10, ""); put(wsS, r, 11, "nein", NEUT); put(wsS, r, 12, "")
        else:
            be = ",".join(sorted(s["bereiche"])) or "?"
            z = "ja"
            if be in ("JZY", "JZV", "JZA"): z = "nein (anderer Standort)"
            elif be == "Lab" and g != "approbiert": z = "nein (Labor, nicht approbiert)"
            put(wsS, r, 6, s["von"]); put(wsS, r, 7, s["bis"]); put(wsS, r, 8, be); put(wsS, r, 9, " / ".join(sorted(s["taetigkeiten"])) or ("; ".join(sorted(s["zusatz"])) if s["zusatz"] else ""))
            put(wsS, r, 10, f"{s['pause_min']} min ({s['pause_start']})" if s["pause_min"] else ""); put(wsS, r, 11, z, None if z == "ja" else NEUT)
            put(wsS, r, 12, ", ".join(sorted(s["quellen"])))
        r += 1
    # -------- Übersicht (zuletzt, braucht Kennzahlen)
    write_overview(wb, ws0, A, titel, quelle_text)
    for ws in wb.worksheets:
        ws.sheet_properties.tabColor = {"Übersicht": "1F3864", "Wochenübersicht": "2E75B6", "KBO-Labor-Notdienst": "2E75B6", "Detail Engpässe": "C00000", "Prüfkandidaten": "70AD47"}.get(ws.title, "7F7F7F")
        ws.sheet_view.showGridLines = False
        ws.page_setup.orientation = "landscape"; ws.page_setup.paperSize = ws.PAPERSIZE_A4
        ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.print_options.horizontalCentered = True
        ws.page_margins.left = ws.page_margins.right = 0.4
    wsW.print_title_rows = "5:5"; wsK.print_title_rows = "4:4"; wsC.print_title_rows = "4:4"
    wb.save(path)


def fmt_people_short(lst):
    return "\n".join(f"{short(n)} {fmt(a)}–{fmt(b)}" for n, a, b in lst)


def write_overview(wb, ws, A, titel, quelle_text):
    setw(ws, [30, 18, 18, 18, 60])
    ws["A1"] = f"Dienstplan-Prüfung Jahreszeiten Apotheke Nienberge – {titel}"; ws["A1"].font = Font(bold=True, size=16)
    ws["A2"] = quelle_text; ws["A2"].alignment = WRAP; ws.merge_cells("A2:E2"); ws.row_dimensions[2].height = 32
    ws["A3"] = "Besetzung ohne Abzug flexibler Mittagspausen"; ws["A3"].font = Font(bold=True, size=12, color="C00000"); ws.merge_cells("A3:E3")
    r = 5
    banner(ws, r, "Kurzfazit", 5, BAND, True, 12); r += 1
    conf = [b for b in A["befunde"] if b["art"] == "bestätigt"]
    days_conf = sorted({b["datum"] for b in conf})
    ys = collections.Counter(); pk = collections.Counter(); tage_n = 0
    for day in A["tage"]:
        if day["status"] != "pruefen": continue
        tage_n += 1
        for b in day["blocks"]:
            if b["tmin"] == b["tsoll"]: ys[b["label"]] += 1
            if b["tmin"] - b["tsoll"] >= 3: pk[b["label"]] += 1
    kbo_rot = lab_rot = 0
    for day in A["tage"]:
        if day["status"] != "pruefen": continue
        for k in KBO_TIMES.get(day["typ"], []):
            if not day["kbo"][k][0] and not day["kbo"][k][1]: kbo_rot += 1
        if day["datum"].weekday() in LAB_DAYS:
            app, nap, unk = day["lab"]
            if not app: lab_rot += 1
            if not nap and not unk: lab_rot += 1
    lines = [
        f"Geprüft wurden {tage_n} Öffnungstage aus {len(A['weeks'])} Wochen (Prüfmonat plus Wochenrest davor, kursiv grau). Nicht bewertet: 24.12. und 31.12. (manuell), Feiertage 25.12. und 26.12. (geschlossen), Tage nach dem Prüfmonat (Januar, Planung wird noch angepasst).",
        f"Bestätigte Unterbesetzungen: {len({(b['datum'], b['von'], b['bis']) for b in conf})} Zeitspannen ({len(conf)} Befunde, Gesamt und Approbierte getrennt gezählt) an {len(days_conf)} Tagen: " + "; ".join(f"{b['datum'].strftime('%d.%m.')} {rng(b['von'], b['bis'])} ({b['kind']} {b['ist']}/{b['soll']})" for b in conf[:12]) + (" …" if len(conf) > 12 else "") + ".",
        f"Nicht erfüllte Zusatzprüfungen: KBO-Prüfzeitpunkte {kbo_rot}×, Labor-Pflicht {lab_rot}× (Details: Blatt „Detail Engpässe“, Abschnitt 1b).",
        f"Pausenabstimmung erforderlich an {len({d for d, x in A['pausen']})} Tagen (Richtzeit-Pausen würden gleichzeitig unter das Soll fallen; keine feste Unterbesetzung)." + (" Nicht abdeckbar auch bei freier Staffelung: " + ", ".join(sorted({d.strftime('%d.%m.') for d, x in A['pausen'] if not x.get('staffelbar', True)})) + "." if any(not x.get("staffelbar", True) for d, x in A["pausen"]) else ""),
        "Zeiträume ohne Personalreserve (Gesamtbesetzung genau Soll), häufigste Zeitblöcke: " + ", ".join(f"{k} ({v}×)" for k, v in ys.most_common(4)) + ".",
        ("Notdienst: " + ", ".join(dstr(x) for x in A["notdienst_termine"]) + " – 09:00 bis 09:00 Folgetag lückenlos mit Approbierten besetzt (Blatt KBO-Labor-Notdienst)." if A["notdienst_bekannt"] and A["notdienst_termine"] and all(not A.get("notdienst", {}).get(x, {"gaps": [1]})["gaps"] for x in A["notdienst_termine"]) else "Notdienst: Prüfergebnis siehe Blatt KBO-Labor-Notdienst." if A["notdienst_bekannt"] else "Notdienstprüfung offen – Termine fehlen."),
        "Erhöhte Personalreserve (Gesamtbesetzung ≥ Soll + 3): " + (", ".join(f"{k} ({v}×)" for k, v in pk.most_common(4)) if pk else "keine") + ". Konkrete Freistellungsmöglichkeiten: Blatt „Prüfkandidaten“.",
    ]
    for t in lines:
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5); x = ws.cell(r, 1, "•  " + t); x.alignment = WRAP
        ws.row_dimensions[r].height = 16 * (1 + len(t) // 120); r += 1
    r += 1
    banner(ws, r, "Offene Fragen", 5, GREY, True, 12); r += 1
    qs = (["Notdienstprüfung offen – Termine fehlen."] if not A["notdienst_bekannt"] else []) + [
          "Notdienste 2027: Termine werden später mitgeteilt (letzter Notdienst 2026 war 30.11. auf 01.12.).",
          "24.12. und 31.12.: Sonderregel (08:00–13:00, immer 3 Personen) wird von dir manuell geprüft."]
    qs += [f"{o[0]}: {o[1]}" for o in A["offen"] if "Mitternacht" in o[1]][:2]
    qs += [f"{x[2]}: {x[3]}" for x in A["daten"] if x[0] == "Hinweis Mittagspause"][:3]
    for t in qs:
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5); x = ws.cell(r, 1, "•  " + t); x.alignment = WRAP; ws.row_dimensions[r].height = 16 * (1 + len(t) // 120); r += 1
    r += 1
    banner(ws, r, "Legende", 5, BAND, True, 12); r += 1
    def leg(color, text, r):
        put(ws, r, 1, "", color); ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=5); put(ws, r, 2, text)
    ws.cell(r, 1, "Gesamtpersonal (Ist-Minimum im Zeitblock)").font = BOLD; r += 1
    for c, t in ((RED, "unter Mindestzahl"), (YEL, "Mindestzahl genau erfüllt (keine Reserve)"), (LGR, "eine Person zusätzlich"), (DGR, "zwei Personen zusätzlich"), (PINK, "drei oder mehr Personen zusätzlich")):
        leg(c, t, r); r += 1
    ws.cell(r, 1, "Approbierte (Zeitblöcke mit mind. 1 erforderlich)").font = BOLD; r += 1
    for c, t in ((RED, "0 approbierte Personen"), (LGR, "1"), (DGR, "2"), (PINK, "3 oder mehr"), (NEUT, "nicht erforderlich (z. B. Aufschließen) bzw. entfällt")):
        leg(c, t, r); r += 1
    ws.cell(r, 1, "Zusatzprüfungen (KBO, Labor, Notdienst)").font = BOLD; r += 1
    for c, t in (("A9D18E", "erfüllt"), (RED, "nicht erfüllt"), (GREY, "nicht eindeutig prüfbar (fehlende/unklare Angaben, offen)"), (NEUT, "entfällt / manuell zu prüfen (Sonderregel)")):
        leg(c, t, r); r += 1
    r += 1
    banner(ws, r, "Prüfgrundlagen und Annahmen", 5, BAND, True, 12); r += 1
    ann = ["Geprüft werden nur die exportierten Dienste (Soll-/Ist-Zeiten laut ApoCollect); es wurden keine Dienste ergänzt, verändert oder gerundet.",
           "Zählt nur in Nienberge: JZN, PBO, KBO, Labor. Nicht: JZY, JZV, JZA (Zentrale/Homeoffice/Büro). Bereichskürzel im Dienst hat Vorrang; ohne Kürzel gilt der Standard des Abschnitts (Hauptbereich = JZN, 3b = KBO, 3c = Labor).",
           "Doppelte Darstellungen derselben Dienste (Haupt-, KBO-, Laborabschnitt) sind zusammengeführt; jede Person zählt je Minute höchstens einmal.",
           "Nick Große („Auszubildende/r“) gilt als PTA-Praktikant (nicht approbiert). Dienstende um 12:00 bedeutet: ab 12:00 nicht mehr anwesend.",
           "Überbrückt werden nur eindeutig erkennbare Mittagspausen: genau 60 Minuten Lücke zwischen zwei Diensten derselben Person (Beginn 11:00–15:00). Andere Lücken werden nicht überbrückt. Pausen mit „P: x min (hh:mm)“ werden in der Hauptübersicht nicht abgezogen. Bei Bereichswechsel mit unsicherer Anrechnung wird das gekennzeichnet. Eine approbierte Person in Pause bleibt in der Apotheke und zählt weiter für die Mindestzahl Approbierte.",
           "Samstag 09:00–13:00: genau 3 Personen (mind. und max. 3); mehr gilt als Mangel (Überbesetzung). Feiertage laut Export: Apotheke geschlossen, nicht geprüft. Tage nach dem Prüfmonat werden vorerst nicht geprüft.",
           "Abschnitte „bis 23:59“ und „ab 00:00“ (Mitternachtsgrenze des Exports) gelten als lückenlos.",
           "Die Pausenprüfung ist ein rechnerisches Szenario (alle Pausen zur Richtzeit) und leitet daraus keine feste Unterbesetzung ab.",
           "Prüfmonat und Wochenreste: Der Prüfmonat und der Wochenrest davor (kursiv grau) werden geprüft; Tage nach dem Prüfmonat werden vorerst nicht geprüft."]
    for t in ann:
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5); x = ws.cell(r, 1, "•  " + t); x.alignment = WRAP; ws.row_dimensions[r].height = 16 * (1 + len(t) // 120); r += 1
    r += 1
    banner(ws, r, "Optimierungsvorschläge zur Prüfdatei (Regeln bleiben unverändert)", 5, BAND, True, 12); r += 1
    opt = ["Blatt „Raster 15 Min“: zeigt je Tag die Besetzung in 15-Minuten-Schritten, Engpässe fallen sofort ins Auge (ist bereits enthalten).",
           "Blatt „Dienste bereinigt“ macht jede Wertung nachvollziehbar und ist filterbar (ist bereits enthalten).",
           "Vorschlag: In ApoCollect Bereichskürzel in jedem Dienst vergeben, auch JZN; und Mittagspausen einheitlich als „P: 60 min (hh:mm)“ führen. Das reduziert unsichere Überbrückungen.",
           "Vorschlag: Notdienst als eigene Tätigkeit/Kürzel im Export führen, dann kann die Notdienstprüfung ohne separate Terminliste laufen.",
           "Vorschlag: Prüfung jeweils für den Monat samt angrenzender Wochenreste laufen lassen und die Datei pro Monat im Vault ablegen, damit Vormonate vergleichbar bleiben."]
    for t in opt:
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5); x = ws.cell(r, 1, "•  " + t); x.alignment = WRAP; ws.row_dimensions[r].height = 16 * (1 + len(t) // 120); r += 1
