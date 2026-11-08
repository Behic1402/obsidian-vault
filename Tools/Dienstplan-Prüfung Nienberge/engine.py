"""Prüf-Engine: minutengenaue Besetzungsprüfung nach den Betriebsregeln (Nienberge).

Regeln stehen in der Vault-Notiz "20 Projekte/Dienstplan-Prüfung Nienberge.md".
Es werden keine Dienste ergänzt oder verändert. Unklares wird als "unsicher" geführt,
nie als ausreichende Besetzung gewertet.
"""
import datetime as dt, collections
import numpy as np
from normalize import tmin, fmt, group_of, COUNTS_SITES, NON_COUNT

M = 1440
# (von, bis, Name, Gesamt-Soll, Approbierte-Soll)
BLOCKS = {
    "wd": [("07:45", "08:00", "Aufschließen", 1, 0), ("08:00", "08:30", "", 2, 1), ("08:30", "12:00", "", 4, 1),
           ("12:00", "15:00", "", 2, 1), ("15:00", "18:00", "", 3, 1), ("18:00", "18:30", "", 2, 1),
           ("18:30", "19:00", "Abschließen", 1, 1)],
    "sa": [("08:45", "09:00", "Aufschließen", 1, 0), ("09:00", "13:00", "", 3, 1), ("13:00", "13:30", "Abschließen", 1, 1)],
}
KBO_TIMES = {"wd": ["10:00", "16:00"], "sa": ["10:00"]}
LAB_DAYS = (0, 2, 4)           # Mo, Mi, Fr
MIDDAY_GAP = 60                # Minuten: einstündige Lücke gilt als erkennbare Mittagspause
MIDDAY_FROM, MIDDAY_TO = tmin("11:00"), tmin("15:00")   # Lückenbeginn im Mittagsfenster


def end_min(s):
    return M if s == "23:59" else tmin(s)


def daytype(d):
    wd = d.weekday()
    return "wd" if wd < 5 else ("sa" if wd == 5 else "so")


def blocks_for(d):
    t = daytype(d)
    return [(tmin(a), tmin(b), n, g, p) for a, b, n, g, p in BLOCKS.get(t, [])]


def block_label(a, b, name):
    return f"{fmt(a)}–{fmt(b)}" + (f" {name}" if name else "")


class Model:
    """Tagesmodell: je Person Minutenarrays."""

    def __init__(self, date, persons):
        self.date = date
        self.persons = persons
        self.C = {}; self.P = {}; self.L = {}; self.N = {}   # bool-Arrays
        self.site = {}      # name -> Liste von (a,b,bereich,taetigkeit,quelle)
        self.bridge = {}    # name -> bool-Array überbrückte Pausen
        self.pauses = []    # dict(name,start,dur,quelle)
        self.hints = []     # (typ, text)
        self.real = {}      # name -> Liste (a,b,bereiche) nicht überbrückt

    def group(self, n):
        p = self.persons[n]
        return group_of(n, p["rolle"])


def build_model(date, shifts, persons, hints_out=None):
    """shifts: Liste normalisierter Dienste dieses Tages (Dict aus normalize)."""
    m = Model(date, persons)
    byp = collections.defaultdict(list)
    for s in shifts:
        byp[s["name"]].append(s)
    for name, lst in byp.items():
        lst.sort(key=lambda s: (tmin(s["von"]), end_min(s["bis"])))
        grp = m.group(name)
        C = np.zeros(M, bool); P = np.zeros(M, bool); L = np.zeros(M, bool); N = np.zeros(M, bool)
        Br = np.zeros(M, bool)
        sstate = []     # je Dienst: Zustand
        real = []
        m.site[name] = []
        # Zustand je Dienst und Minute (Überlappung unterschiedlicher Bereiche -> unsicher)
        cov = np.zeros((4, M), bool)   # C, P, L, N Beiträge
        for s in lst:
            a, b = tmin(s["von"]), end_min(s["bis"])
            if b <= a:
                m.hints.append(("Datenpflege", f"{name}: Dienst {s['von']}–{s['bis']} hat Ende ≤ Beginn, nicht gewertet"))
                continue
            beres = sorted(s["bereiche"]) or [None]
            st = set()
            for br in beres:
                st.add(_state(br, grp))
            if len(beres) > 1:
                m.hints.append(("Datenpflege", f"{name}: Dienst {s['von']}–{s['bis']} mit widersprüchlichen Bereichen {beres} aus verschiedenen Abschnitten"))
            real.append((a, b, tuple(beres)))
            m.site[name].append((a, b, "/".join(b_ or "?" for b_ in beres), "/".join(sorted(s["taetigkeiten"])), s))
            # Zustand bestimmen: eindeutig, wenn nur ein Zustand; sonst unsicher
            if len(st) == 1:
                x = next(iter(st))
                sstate.append((a, b, x))
            else:
                sstate.append((a, b, "U" if ("C" in st or "U" in st) else ("L" if "L" in st else "N")))
        # Überlappung innerhalb einer Person: gleiche Minute mehrfach -> Prüfen
        for (a, b, x) in sstate:
            idx = {"C": 0, "U": 1, "L": 2, "N": 3}[x]
            cov[idx, a:b] = True
        multi = (cov.sum(axis=0) > 1)
        if multi.any():
            # Minuten mit verschiedenen Zuständen
            amb = multi & (cov[0] | cov[1])      # (zählend oder unsicher) UND weiterer Zustand
            C = cov[0] & ~multi
            P = cov[1] | (multi & (cov[0] | cov[1]))
            L = cov[2] & ~multi
            N = cov[3] & ~multi
            if (multi).any():
                m.hints.append(("Datenpflege", f"{name}: überlappende Dienste mit unterschiedlicher Zuordnung ({fmt(int(np.argmax(multi)))} ff.)"))
        else:
            C, P, L, N = cov[0], cov[1], cov[2], cov[3]
        # Überbrückbare Mittagspausen (exakt 60 min Lücke zwischen zwei Diensten, Beginn 11:00–15:00)
        merged = sorted(sstate)
        for i in range(len(merged) - 1):
            a1, b1, x1 = merged[i]; a2, b2, x2 = merged[i + 1]
            gap = a2 - b1
            if gap <= 0:
                continue
            if gap == MIDDAY_GAP and MIDDAY_FROM <= b1 <= MIDDAY_TO:
                if x1 == x2 == "C":
                    C = C.copy(); C[b1:a2] = True
                elif x1 == x2 == "L":
                    L = L.copy(); L[b1:a2] = True
                elif x1 == x2 == "N":
                    N = N.copy(); N[b1:a2] = True
                elif "C" in (x1, x2) or "U" in (x1, x2):
                    P = P.copy(); P[b1:a2] = True
                else:
                    N = N.copy(); N[b1:a2] = True
                Br[b1:a2] = True
                m.pauses.append({"name": name, "start": b1, "dur": gap, "quelle": "Lücke"})
                if x1 != x2:
                    m.hints.append(("Pause", f"{name}: überbrückte Pause {fmt(b1)}–{fmt(a2)} zwischen unterschiedlichen Zuordnungen ({_sn(x1)} → {_sn(x2)}), Anrechenbarkeit unsicher"))
            else:
                m.hints.append(("Datenpflege", f"{name}: Lücke {fmt(b1)}–{fmt(a2)} ({gap} min) zwischen Diensten, nicht als Mittagspause behandelt"))
        # annotierte Pausen
        for s in lst:
            if s["pause_min"]:
                if not s["pause_start"]:
                    m.hints.append(("Datenpflege", f"{name}: Pause {s['pause_min']} min ohne Beginnzeit ({s['von']}–{s['bis']})"))
                    continue
                ps = tmin(s["pause_start"])
                if not (tmin(s["von"]) <= ps and ps + s["pause_min"] <= end_min(s["bis"])):
                    m.hints.append(("Datenpflege", f"{name}: Pause {s['pause_start']} liegt nicht im Dienst {s['von']}–{s['bis']}"))
                m.pauses.append({"name": name, "start": ps, "dur": s["pause_min"], "quelle": "P"})
        m.C[name], m.P[name], m.L[name], m.N[name], m.bridge[name] = C, P, L, N, Br
        m.real[name] = real
    # Doppelzählung der Pausen verhindern: gleiche Person + gleicher Zeitraum nur einmal
    seen = set(); uniq = []
    for p in m.pauses:
        k = (p["name"], p["start"], p["dur"])
        if k in seen: continue
        seen.add(k); uniq.append(p)
    m.pauses = uniq
    for n in {p["name"] for p in m.pauses}:
        ps = [p for p in m.pauses if p["name"] == n]
        if len(ps) > 1:
            m.hints.append(("Datenpflege", f"{n}: mehrere Pausen am Tag ({', '.join(fmt(p['start']) + '/' + str(p['dur']) + ' min' for p in ps)}), bitte prüfen (keine doppelte Anrechnung)"))
    return m


def _state(bereich, grp):
    """Zustand eines Dienstabschnitts nach Bereich und Berufsgruppe."""
    if bereich is None:
        return "U"
    if bereich in ("JZN", "PBO", "KBO"):
        return "C" if grp != "unklar" else "U"
    if bereich == "Lab":
        return {"approbiert": "C", "nicht_approbiert": "L"}.get(grp, "U")
    if bereich in NON_COUNT:
        return "N"
    return "U"


def _sn(x):
    return {"C": "anrechenbar", "L": "Labor (nicht approbiert)", "N": "nicht Nienberge", "U": "unklar"}[x]


def counts(m, pauses=False, exclude=()):
    tot = np.zeros(M, int); app = np.zeros(M, int); pt = np.zeros(M, int); pa = np.zeros(M, int)
    nap = np.zeros(M, int)
    pm = None
    if pauses:
        pm = collections.defaultdict(lambda: np.zeros(M, bool))
        for p in m.pauses:
            pm[p["name"]][p["start"]:p["start"] + p["dur"]] = True
    for n in m.C:
        if n in exclude:
            continue
        C = m.C[n]; P = m.P[n]
        if pm is not None and n in pm:
            C = C & ~pm[n]; P = P & ~pm[n]
        g = m.group(n)
        tot += C
        if g == "approbiert":
            app += C; pa += P
        elif g == "nicht_approbiert":
            nap += C
        else:
            pa += P   # unklar: potentiell approbiert
        pt += P
    return {"tot": tot, "app": app, "nap": nap, "pt": pt, "pa": pa}


def eval_blocks(m, cnt):
    res = []
    for a, b, name, gs, ps in blocks_for(m.date):
        t = cnt["tot"][a:b]; p = cnt["app"][a:b]
        res.append({"a": a, "b": b, "name": name, "label": block_label(a, b, name),
                    "tsoll": gs, "asoll": ps, "tmin": int(t.min()), "tmax": int(t.max()),
                    "amin": int(p.min()), "amax": int(p.max()),
                    "tpot_min": int((t + cnt["pt"][a:b]).min()), "apot_min": int((p + cnt["pa"][a:b]).min())})
    return res


def kbo_status(m, tmin_):
    """KBO-Zuordnung zum Zeitpunkt (nur echte, nicht überbrückte Dienste)."""
    pers = []
    for n, lst in m.real.items():
        for a, b, beres in lst:
            if a <= tmin_ < b and "KBO" in beres:
                pers.append((n, a, b, beres))
    bridged = [n for n, br in m.bridge.items() if br[tmin_] and any(
        True for a, b, beres in m.real.get(n, []) if "KBO" in beres)]
    return pers, bridged


def lab_people(m):
    app, nap, unk = [], [], []
    for n, lst in m.real.items():
        g = m.group(n)
        for a, b, beres in lst:
            if "Lab" in beres:
                (app if g == "approbiert" else nap if g == "nicht_approbiert" else unk).append((n, a, b))
    return app, nap, unk


def fmt_people(lst):
    return "; ".join(f"{n} {fmt(a)}–{fmt(b)}" for n, a, b in lst)


def violations(m, cnt=None):
    """Harte Verstöße (nur sichere Zählung) – für Prüfkandidaten."""
    cnt = cnt or counts(m)
    v = []
    for r in eval_blocks(m, cnt):
        if r["tmin"] < r["tsoll"]:
            v.append(f"{r['label']} Gesamt {r['tmin']}<{r['tsoll']}")
        if r["asoll"] and r["amin"] < r["asoll"]:
            v.append(f"{r['label']} Approbierte {r['amin']}<{r['asoll']}")
    t = daytype(m.date)
    for k in KBO_TIMES.get(t, []):
        pers, _ = kbo_status(m, tmin(k))
        if not pers:
            v.append(f"KBO {k} nicht besetzt")
    if m.date.weekday() in LAB_DAYS:
        a, n, u = lab_people(m)
        if not a: v.append("Labor: keine approbierte Person")
        if not n: v.append("Labor: keine nicht approbierte Person")
    return v


def pause_issues(m, base=None):
    """Szenario: alle Pausen zur Richtzeit. Liefert Blöcke, in denen dadurch Soll unterschritten würde,
    obwohl die Besetzung ohne Abzug ausreicht."""
    c0 = counts(m); c1 = counts(m, pauses=True)
    out = []
    for a, b, name, gs, ps in blocks_for(m.date):
        for kind, key, soll in (("Gesamt", "tot", gs), ("Approbierte", "app", ps)):
            if soll == 0:
                continue
            if c0[key][a:b].min() < soll:
                continue            # schon ohne Pausen zu wenig -> bestätigte Unterbesetzung
            arr = c1[key][a:b]
            if arr.min() < soll:
                # zusammenhängende Minuten unter Soll
                bad = arr < soll
                spans = []; i = 0
                while i < len(bad):
                    if bad[i]:
                        j = i
                        while j < len(bad) and bad[j]: j += 1
                        spans.append((a + i, a + j, int(arr[i:j].min()), int(c0[key][a + i:a + j].min())))
                        i = j
                    else:
                        i += 1
                for (x, y, ist, ohne) in spans:
                    pw = [p for p in m.pauses if p["start"] < y and p["start"] + p["dur"] > x]
                    out.append({"kind": kind, "a": x, "b": y, "ist": ist, "ohne": ohne, "soll": soll,
                                "label": block_label(a, b, name), "pausen": pw})
    return out
