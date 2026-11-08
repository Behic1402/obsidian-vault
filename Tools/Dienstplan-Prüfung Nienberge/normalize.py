"""Normalisiert die Rohdaten des Parsers: Bereichszuordnung je Dienstabschnitt, Duplikate zusammenführen."""
import datetime as dt, re, collections

SECTION_DEFAULT = {"3": "JZN", "3b": "KBO", "3c": "Lab"}   # Standardbereich je Bereichsabschnitt
COUNTS_SITES = {"JZN", "PBO", "KBO", "Lab"}                # zählen für Nienberge
NON_COUNT = {"JZY", "JZV", "JZA"}

# Berufsgruppen. "Auszubildende/r" nur für Nick Große ausdrücklich als PTA-Praktikant freigegeben.
ROLE_GROUP = {"Apotheker/in": "approbiert", "PTA": "nicht_approbiert", "PhiP": "nicht_approbiert",
              "PTA-Praktikant/in": "nicht_approbiert"}
ROLE_OVERRIDE = {("Große, Nick", "Auszubildende/r"): "nicht_approbiert"}


def tmin(s):
    h, m = s.split(":"); return int(h) * 60 + int(m)


def fmt(m):
    return f"{m // 60:02d}:{m % 60:02d}"


def group_of(name, role):
    if (name, role) in ROLE_OVERRIDE: return ROLE_OVERRIDE[(name, role)]
    return ROLE_GROUP.get(role, "unklar")


def section_default(sektion):
    m = re.match(r"^(\d+[a-z]?)\s", sektion or "")
    return SECTION_DEFAULT.get(m.group(1)) if m else None


def normalize(weeks):
    """Liefert dict(personen, tage, shifts, abwesend, feiertag, hinweise)."""
    persons = {}
    shifts = collections.OrderedDict()        # key (name, datum, von, bis) -> dict
    absent = collections.defaultdict(set)     # (name, datum) -> {Text}
    hints = []                                # Datenpflegehinweise
    days = []
    exportdates = set()
    for w in weeks:
        exportdates.add(w.get("exportdatum"))
        for t in w["tage"]:
            days.append({"datum": t["datum"], "wd": t["wd"], "kw": w["kw"]})
        for p in w["personen"]:
            r = persons.setdefault(p["name"], {"rolle": p["rolle"]})
            if p["rolle"] and not r["rolle"]: r["rolle"] = p["rolle"]
        for z in w["zellen"]:
            for o in z["sonstiges"]:
                absent[(z["name"], z["datum"])].add(o)
            for s in z["shifts"]:
                eff = s["tag"] or section_default(z["sektion"])
                key = (z["name"], z["datum"], s["von"], s["bis"])
                src = (z["sektion"] or "?").split(" ")[0]
                e = shifts.get(key)
                if e is None:
                    shifts[key] = {"name": z["name"], "datum": z["datum"], "von": s["von"], "bis": s["bis"],
                                   "bereiche": {eff} if eff else set(), "taetigkeiten": {s["taetigkeit"]} if s["taetigkeit"] else set(),
                                   "tags": {s["tag"]}, "pause_min": s["pause_min"], "pause_start": s["pause_start"],
                                   "zusatz": {s["unbekannter_zusatz"]} if s["unbekannter_zusatz"] else set(),
                                   "quellen": {src}, "kw": w["kw"]}
                else:
                    if eff: e["bereiche"].add(eff)
                    if s["taetigkeit"]: e["taetigkeiten"].add(s["taetigkeit"])
                    e["tags"].add(s["tag"]); e["quellen"].add(src)
                    if s["unbekannter_zusatz"]: e["zusatz"].add(s["unbekannter_zusatz"])
                    if s["pause_min"] and not e["pause_min"]:
                        e["pause_min"], e["pause_start"] = s["pause_min"], s["pause_start"]
                    elif s["pause_min"] and (s["pause_min"], s["pause_start"]) != (e["pause_min"], e["pause_start"]):
                        hints.append(("Pause widersprüchlich", z["name"], z["datum"], f"{s['von']}–{s['bis']}: {e['pause_min']}/{e['pause_start']} vs {s['pause_min']}/{s['pause_start']}"))
    return {"personen": persons, "tage": days, "shifts": list(shifts.values()), "abwesend": absent,
            "hinweise": hints, "exportdaten": exportdates}
