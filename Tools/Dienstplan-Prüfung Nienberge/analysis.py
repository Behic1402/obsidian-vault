"""Auswertung: Wochen/Tage/Blöcke, bestätigte Unterbesetzungen, KBO/Labor/Notdienst, Pausen, Prüfkandidaten."""
import datetime as dt, collections, copy
import numpy as np
from normalize import normalize, tmin, fmt, group_of
from engine import *

WD = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
SONDERTAGE_DEFAULT = ["12-24", "12-31"]     # MM-TT: manuell geprüft (Heiligabend/Silvester, nur 08–13 Uhr, 3 Personen)


def D(s): return dt.date.fromisoformat(s)
def dstr(d): return d.strftime("%d.%m.%Y")


def spans(mask, off=0):
    out = []; i = 0; n = len(mask)
    while i < n:
        if mask[i]:
            j = i
            while j < n and mask[j]: j += 1
            out.append((off + i, off + j)); i = j
        else:
            i += 1
    return out


def role_label(N, name):
    r = N["personen"][name]["rolle"]
    g = group_of(name, r)
    return (r or "ohne Berufsbezeichnung")


def analyze(weeks, notdienst=(), sondertage=SONDERTAGE_DEFAULT, monat=None):
    weeks = sorted(weeks, key=lambda w: w["von"][6:] + w["von"][3:5] + w["von"][:2])
    N = normalize(weeks)
    A = {"N": N, "weeks": [], "tage": [], "befunde": [], "pausen": [], "daten": [], "offen": [], "kandidaten": [],
         "notdienst_termine": [D(x) for x in notdienst], "monat": monat}
    exportdaten = sorted(x for x in N["exportdaten"] if x)
    A["exportdaten"] = exportdaten
    byday = collections.defaultdict(list)
    for s in N["shifts"]:
        byday[s["datum"]].append(s)
    feiertag = collections.defaultdict(set)
    for (name, datum), txts in N["abwesend"].items():
        if "Feiertag" in txts:
            feiertag[datum].add(name)
    # Datenpflege aus Personen/Texten
    for name, p in N["personen"].items():
        g = group_of(name, p["rolle"])
        if p["rolle"] is None:
            A["daten"].append(("Berufsbezeichnung fehlt", name, "", "Keine Berufsbezeichnung im Export; Person wird keiner Berufsgruppe zugeordnet (nur relevant, falls Dienste eingetragen sind)."))
        elif p["rolle"] == "Auszubildende/r":
            A["daten"].append(("Berufsbezeichnung", name, "", "Im Export „Auszubildende/r“, laut Vorgabe als PTA-Praktikant (nicht approbiert) gewertet."))
    absent_trunc = sorted({t for v in N["abwesend"].values() for t in v if t.endswith("...")})
    for t in absent_trunc:
        n = sum(1 for v in N["abwesend"].values() if t in v)
        A["daten"].append(("Abwesenheitstext abgeschnitten", "", "", f"„{t}“ ({n}×) im Export gekürzt; zählt in jedem Fall nicht als Anwesenheit."))
    # Modelle je Tag
    models = {}
    for t in N["tage"]:
        d = D(t["datum"])
        sh = byday.get(t["datum"], [])
        m = build_model(d, sh, N["personen"])
        models[d] = (m, sh)
    A["models"] = models
    for w in weeks:
        exp = w.get("exportdatum")
        von = D(dt.datetime.strptime(w["von"], "%d.%m.%Y").date().isoformat())
        plan = (exp is None) or (D(exp) < von)
        A["weeks"].append({"kw": w["kw"], "von": von, "bis": D(dt.datetime.strptime(w["bis"], "%d.%m.%Y").date().isoformat()),
                           "export": exp, "plan": plan})
        if not plan:
            A["daten"].append(("Soll/Ist gemischt", "", f"KW {w['kw']}", f"Export vom {exp[8:]}.{exp[5:7]}.{exp[:4]} liegt nach Wochenbeginn: Woche kann bereits Ist-Zeiten enthalten (Plan und Ist gemischt)."))
    # Tagesauswertung
    for t in N["tage"]:
        d = D(t["datum"]); m, sh = models[d]
        day = {"datum": d, "wd": WD[d.weekday()], "kw": t["kw"], "typ": daytype(d), "status": "pruefen",
               "blocks": [], "kbo": {}, "lab": None, "notiz": []}
        mmdd = d.strftime("%m-%d")
        in_month = (monat is None) or d.strftime("%Y-%m") == monat
        day["im_monat"] = in_month
        if mmdd in sondertage:
            day["status"] = "sonder"
        elif d.isoformat() in feiertag:
            day["status"] = "feiertag"; day["feiertag_personen"] = sorted(feiertag[d.isoformat()])
            if sh:
                A["offen"].append((dstr(d), "Feiertag mit eingetragenen Diensten – Öffnung/Besetzung klären", ", ".join(sorted({s['name'] for s in sh}))))
            else:
                A["offen"].append((dstr(d), "Feiertag laut Export – keine Dienste eingetragen; Öffnung/Besetzung klären (nicht bewertet)", ""))
        elif day["typ"] == "so":
            day["status"] = "sonntag"
            if sh:
                A["offen"].append((dstr(d), "Sonntag mit eingetragenen Diensten – keine Öffnungszeit definiert", ", ".join(sorted({s['name'] for s in sh}))))
        if day["status"] == "pruefen":
            cnt = counts(m); cntp = counts(m, pauses=True)
            res = eval_blocks(m, cnt)
            day["cnt"] = cnt
            pis = pause_issues(m)
            for r in res:
                r["pause"] = [x for x in pis if x["a"] >= r["a"] and x["b"] <= r["b"]]
                r["nap_min"] = int(cnt["nap"][r["a"]:r["b"]].min())
                r["unsicher_gesamt"] = r["tmin"] < r["tsoll"] <= r["tpot_min"]
                r["unsicher_app"] = r["asoll"] and r["amin"] < r["asoll"] <= r["apot_min"]
                r["bestaetigt_gesamt"] = r["tpot_min"] < r["tsoll"]
                r["bestaetigt_app"] = bool(r["asoll"]) and r["apot_min"] < r["asoll"]
            day["blocks"] = res
            # Bestätigte / offene Unterbesetzungen als Zeitspannen
            for kind, key, pkey, soll_i in (("Gesamt", "tot", "pt", 3), ("Approbierte", "app", "pa", 4)):
                for r in res:
                    soll = r["tsoll"] if kind == "Gesamt" else r["asoll"]
                    if not soll: continue
                    a, b = r["a"], r["b"]
                    arr = cnt[key][a:b]; pot = cnt[pkey][a:b]
                    conf = (arr + pot) < soll
                    openm = (arr < soll) & ~conf
                    for (x, y) in spans(conf, a):
                        A["befunde"].append(befund(m, N, cnt, d, x, y, kind, key, soll, r, "bestätigt"))
                    for (x, y) in spans(openm, a):
                        A["befunde"].append(befund(m, N, cnt, d, x, y, kind, key, soll, r, "offen"))
            for x in pis:
                A["pausen"].append((d, x))
            # KBO
            for k in KBO_TIMES.get(day["typ"], []):
                pers, br = kbo_status(m, tmin(k))
                day["kbo"][k] = (pers, br)
            if d.weekday() in LAB_DAYS or True:
                day["lab"] = lab_people(m)
            day["hints"] = m.hints
        # Datenpflege (Tätigkeit vs. Bereich, Mitternachtsabschnitte)
        for s in sh:
            beres = sorted(s["bereiche"]); acts = sorted(s["taetigkeiten"])
            if s["von"] == "00:00" or s["bis"] == "23:59":
                A["offen"].append((dstr(d), f"Dienstabschnitt über Mitternacht (exportbedingt geteilt bei 23:59/00:00): {s['name']} {s['von']}–{s['bis']} – möglicher Notdienst, Termine nicht mitgeteilt", s["name"]))
            if len(s["bereiche"]) != 1:
                A["daten"].append(("Bereich nicht eindeutig", s["name"], dstr(d), f"{s['von']}–{s['bis']}: Bereiche {beres or ['keiner']}"))
                continue
            b = beres[0]
            if b == "KBO" and "Handverkauf" in acts:
                A["daten"].append(("Tätigkeit ≠ Bereich", s["name"], dstr(d), f"{s['von']}–{s['bis']}: Bereich KBO, Tätigkeit „Handverkauf“ – zählt als KBO (Bereichszuordnung hat Vorrang)."))
            elif b == "JZN" and any(a.startswith("Backoffice") for a in acts):
                A["daten"].append(("Tätigkeit ≠ Bereich", s["name"], dstr(d), f"{s['von']}–{s['bis']}: Bereich JZN, Tätigkeit „{', '.join(acts)}“ – zählt als JZN."))
            elif b == "PBO" and "Backoffice Warenwirtschaft" in acts:
                A["daten"].append(("Tätigkeit ≠ Bereich", s["name"], dstr(d), f"{s['von']}–{s['bis']}: Bereich PBO mit Tätigkeit Warenwirtschaft – bleibt PBO, nicht KBO."))
            elif b == "PBO" and "Handverkauf" in acts:
                A["daten"].append(("Tätigkeit ≠ Bereich", s["name"], dstr(d), f"{s['von']}–{s['bis']}: Bereich PBO, Tätigkeit Handverkauf – zählt als PBO."))
            elif b == "Lab" and acts and "Labor" not in acts:
                A["daten"].append(("Tätigkeit ≠ Bereich", s["name"], dstr(d), f"{s['von']}–{s['bis']}: Bereich Labor, Tätigkeit {acts}"))
            if s["zusatz"]:
                A["daten"].append(("Zusatztext im Dienst", s["name"], dstr(d), f"{s['von']}–{s['bis']} ({b}): „{', '.join(sorted(s['zusatz']))}“ – Standort außerhalb Nienberge/Homeoffice, zählt nicht."))
        if day["status"] == "pruefen":
            for typ, txt in m.hints:
                if typ == "Datenpflege":
                    A["daten"].append(("Dienstdaten", "", dstr(d), txt))
                else:
                    A["daten"].append(("Hinweis Mittagspause", "", dstr(d), txt))
            # Sa Zielzusammensetzung
            if day["typ"] == "sa":
                for r in day["blocks"]:
                    if r["name"] == "" and r["tsoll"] == 3:
                        ok_min = r["tmin"] >= r["tsoll"] and r["amin"] >= r["asoll"]
                        r["ziel_abw"] = ok_min and (r["amin"] < 1 or r["nap_min"] < 2)
                        r["ziel_text"] = f"Zielbesetzung 1 Apotheker/in + 2 PTA/Praktikant/PhiP: Ist min. {r['amin']} approbiert, {r['nap_min']} nicht approbiert"
        A["tage"].append(day)
    # Notdienst
    for nd in A["notdienst_termine"]:
        A.setdefault("notdienst", {})[nd] = notdienst_check(models, nd)
    # Prüfkandidaten
    A["kandidaten"] = kandidaten(A, byday)
    return A


def befund(m, N, cnt, d, x, y, kind, key, soll, r, art):
    ist = int(cnt[key][x:y].min())
    # anrechenbare Personen in der Spanne
    zaehlt = []
    for n in m.C:
        c = m.C[n][x:y]
        if not c.any(): continue
        g = m.group(n)
        if key == "app" and g != "approbiert": continue
        part = "" if c.all() else " (teilweise)"
        zaehlt.append(f"{n} ({role_label(N, n)}){part}")
    nicht = []
    for n, lst in m.site.items():
        for a, b, br, akt, s in lst:
            if a < y and b > x and not m.C[n][max(a, x):min(b, y)].all():
                if key == "app" and m.group(n) != "approbiert" and br != "Lab":
                    pass
                why = ("Labor – als nicht approbierte Person nicht mitgezählt" if (br == "Lab" and m.group(n) != "approbiert")
                       else f"Bereich {br} (nicht Nienberge)" if br in ("JZY", "JZV", "JZA")
                       else "Zuordnung unklar")
                if key == "app" and m.group(n) != "approbiert":
                    why = f"nicht approbiert ({why})"
                nicht.append(f"{n} {fmt(max(a, x))}–{fmt(min(b, y))}: {why}")
    # Pausenhinweis
    return {"datum": d, "von": x, "bis": y, "kind": kind, "ist": ist, "soll": soll, "block": r["label"], "art": art,
            "zaehlt": zaehlt, "nicht": nicht}


def notdienst_check(models, nd):
    """09:00 am Tag nd bis 09:00 Folgetag: durchgehend mind. eine approbierte Person in einem Nienberge-Dienst."""
    nxt = nd + dt.timedelta(days=1)
    cov = np.zeros(2 * M, bool); pers = []
    missing_day = False
    for off, day in ((0, nd), (M, nxt)):
        if day not in models:
            missing_day = True; continue
        m, sh = models[day]
        for n in m.real:
            if m.group(n) != "approbiert": continue
            for a, b, beres in m.real[n]:
                if any(x in ("JZN", "PBO", "KBO", "Lab") for x in beres):
                    cov[off + a:off + b] = True; pers.append((n, off + a, off + b))
    # Exportgrenze 23:59 -> 00:00 als lückenlos
    cov[M - 1] = cov[M - 1] or (cov[M - 2] and cov[M])
    win = cov[9 * 60:M + 9 * 60]
    gaps = spans(~win, 9 * 60)
    return {"gaps": gaps, "persons": pers, "missing_day": missing_day or (nd + dt.timedelta(days=1) not in models)}


def variant_shifts(sh, name, mode, t=None):
    out = []
    own = sorted([s for s in sh if s["name"] == name], key=lambda s: tmin(s["von"]))
    for s in sh:
        if s["name"] != name:
            out.append(s)
    if mode == "all":
        return out
    first = own[0]; last = own[-1]
    for s in own:
        s2 = dict(s)
        if mode == "start" and s is first:
            s2["von"] = fmt(t)
        if mode == "end" and s is last:
            s2["bis"] = fmt(t)
        out.append(s2)
    return out


def kandidaten(A, byday):
    N = A["N"]; out = []
    nd_days = set()
    for nd in A["notdienst_termine"]:
        nd_days.add(nd); nd_days.add(nd + dt.timedelta(days=1))
    for day in A["tage"]:
        if day["status"] != "pruefen" or day["typ"] == "so":
            continue
        d = day["datum"]
        m0, sh = A["models"][d]
        if violations(m0) or d in nd_days:
            continue
        if any(r["unsicher_gesamt"] or r["unsicher_app"] for r in day["blocks"]):
            continue
        base_p = {(x["kind"], x["a"], x["b"]) for x in pause_issues(m0)}
        names = sorted({s["name"] for s in sh})
        for n in names:
            own = sorted([s for s in sh if s["name"] == n], key=lambda s: tmin(s["von"]))
            # nur Personen, die für Nienberge zählen oder im Labor/KBO stehen
            if not (m0.C[n].any() or m0.L[n].any() or m0.P[n].any()):
                continue
            g = m0.group(n)
            res = {"datum": d, "name": n, "gruppe": role_label(N, n), "dienste": ", ".join(f"{s['von']}–{s['bis']} ({'/'.join(sorted(s['bereiche'])) or '?'})" for s in own)}
            mv = build_model(d, variant_shifts(sh, n, "all"), N["personen"])
            v = violations(mv)
            res["ganz"] = not v
            res["ganz_grund"] = "; ".join(v[:3]) if v else ""
            res["pause_neu"] = False
            if not v:
                new_p = {(x["kind"], x["a"], x["b"]) for x in pause_issues(mv)}
                res["pause_neu"] = bool(new_p - base_p)
            # Teilzeiträume
            a0, b0 = tmin(own[0]["von"]), end_min(own[0]["bis"])
            best_start = None
            for t in range(a0 + 15, b0, 15):
                mv = build_model(d, variant_shifts(sh, n, "start", t), N["personen"])
                if violations(mv): break
                best_start = t
            last = own[-1]; a1, b1 = tmin(last["von"]), end_min(last["bis"])
            best_end = None
            for t in range(b1 - 15, a1, -15):
                mv = build_model(d, variant_shifts(sh, n, "end", t), N["personen"])
                if violations(mv): break
                best_end = t
            res["start_bis"] = best_start; res["ende_ab"] = best_end
            res["rest_start"] = (b0 - best_start) if best_start else None
            res["rest_end"] = (best_end - a1) if best_end else None
            res["orig_start"] = a0; res["orig_ende"] = b1
            if res["ganz"] or (best_start and best_start - a0 >= 60) or (best_end and b1 - best_end >= 60):
                out.append(res)
    return out
