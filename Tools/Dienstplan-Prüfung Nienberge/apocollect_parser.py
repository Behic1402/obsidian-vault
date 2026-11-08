#!/usr/bin/env python3
"""Liest ApoCollect-Wochenexporte (PDF) ein und liefert rohe Dienstabschnitte.

Es wird nichts ergänzt, gerundet oder geraten. Jede Zelle (Person x Tag x Bereichsabschnitt)
wird in Dienstabschnitte (Zeitspanne, Kürzel, Tätigkeit, Pause) und sonstige Texte
(z. B. Abwesenheiten) zerlegt. Positionsbasiert (Wortkoordinaten), damit auch Zeilen am
Seitenende sauber gelesen werden.
"""
import re, sys, json, datetime as dt
import pdfplumber

TIMERE = re.compile(r"(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})")
TAGRE = re.compile(r"\((JZN|JZY|JZV|JZA|PBO|KBO|Lab|[A-Za-zÄÖÜ]{2,5})\)")
PAUSERE = re.compile(r"P:\s*(\d+)\s*min(?:\s*\((\d{2}:\d{2})\))?")
HEADRE = re.compile(r"Arbeitsplan\s+KW\s*(\d+)\s*\((\d{2}\.\d{2}\.\d{4})\s*-\s*(\d{2}\.\d{2}\.\d{4})\)")
DAYS = ("MO", "DI", "MI", "DO", "FR", "SA", "SO")
ROLES = ["Auszubildende/r", "Apotheker/in", "PTA-Praktikant/in", "PTA", "PhiP", "PKA"]
KNOWN_ACT = ["Backoffice Pharmazeutisch", "Backoffice Warenwirtschaft", "Backoffice Kaufmännisch",
             "Handverkauf", "Labor"]
SECTIONRE = re.compile(r"^\d+[a-z]?\s+\S")


def _lines(words):
    """Wörter -> Zeilen (nach Position), als Text."""
    words = sorted(words, key=lambda w: (round(w["top"] / 3), w["x0"]))
    lines, cur, ctop = [], [], None
    for w in words:
        if ctop is None or abs(w["top"] - ctop) > 3.5:
            if cur: lines.append(cur)
            cur, ctop = [w], w["top"]
        else:
            cur.append(w)
    if cur: lines.append(cur)
    return [" ".join(x["text"] for x in sorted(l, key=lambda w: w["x0"])) for l in lines]


def parse_cell(text):
    t = text.replace("\x00", "fi").replace("🧪", " ")
    t = re.sub(r"\s+", " ", t).strip()
    ms = list(TIMERE.finditer(t))
    pre = t[: ms[0].start()].strip() if ms else t
    shifts = []
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(t)
        rest = t[m.end():end].strip()
        tag = None
        tm = TAGRE.match(rest)
        if tm:
            tag = tm.group(1); rest = rest[tm.end():].strip()
        pm = PAUSERE.search(rest)
        pmin = pstart = None
        if pm:
            pmin = int(pm.group(1)); pstart = pm.group(2)
            rest = (rest[: pm.start()] + " " + rest[pm.end():]).strip()
        acts = []
        for a in KNOWN_ACT:
            if a in rest:
                acts.append(a); rest = rest.replace(a, " ")
        rest = re.sub(r"\s+", " ", rest).strip()
        shifts.append({"von": m.group(1), "bis": m.group(2), "tag": tag,
                       "taetigkeit": " + ".join(acts), "pause_min": pmin, "pause_start": pstart,
                       "unbekannter_zusatz": rest or None})
    other = [pre] if pre else []
    return shifts, other


def parse_pdf(path):
    out = {"datei": path.split("/")[-1], "kw": None, "von": None, "bis": None, "tage": [],
           "zellen": [], "sektionen": [], "personen": [], "exportdatum": None}
    section = None
    with pdfplumber.open(path) as pdf:
        for pno, page in enumerate(pdf.pages, 1):
            words = page.extract_words()
            full = page.extract_text() or ""
            em = re.search(r"(\d{2}\.\d{2}\.\d{4})\s*\n?\s*\d+\s*/\s*\d+\s*$", full.strip())
            if em and not out.get("exportdatum"):
                out["exportdatum"] = dt.datetime.strptime(em.group(1), "%d.%m.%Y").date().isoformat()
            h = HEADRE.search(full)
            if h and out["kw"] is None:
                out["kw"], out["von"], out["bis"] = int(h.group(1)), h.group(2), h.group(3)
            heads = []
            for i, w in enumerate(words):
                if w["text"] in DAYS and i + 1 < len(words) and re.match(r"\d{2}\.\d{2}\.\d{2}$", words[i + 1]["text"]):
                    heads.append({"wd": w["text"], "datum": dt.datetime.strptime(words[i + 1]["text"], "%d.%m.%y").date().isoformat(),
                                  "xc": (w["x0"] + words[i + 1]["x1"]) / 2, "top": w["top"]})
            if len(heads) != 7:
                raise RuntimeError(f"{path} Seite {pno}: {len(heads)} Tageskopfzeilen statt 7")
            heads.sort(key=lambda x: x["xc"])
            if not out["tage"]:
                out["tage"] = [{"wd": x["wd"], "datum": x["datum"]} for x in heads]
            colw = (heads[-1]["xc"] - heads[0]["xc"]) / 6
            left = heads[0]["xc"] - colw / 2
            head_bottom = max(x["top"] for x in heads) + 8
            # Fußzeile entfernen
            foot = [w for w in words if re.match(r"\d{2}\.\d{2}\.\d{4}$", w["text"]) and w["top"] > page.height - 40]
            foot_top = min([w["top"] for w in foot], default=page.height) - 1
            words = [w for w in words if w["top"] < foot_top and w["top"] > head_bottom - 1 - 0]
            # Titelzeile oberhalb der Tageskopfzeile ausschließen (schon durch head_bottom)
            tables = page.find_tables()
            if not tables:
                raise RuntimeError(f"{path} Seite {pno}: keine Tabelle")
            tops = sorted({round(c[1], 1) for c in tables[0].cells if c[3] > 0 and c[1] >= head_bottom - 6})
            tops = [t for t in tops if t < foot_top]
            bounds = [t for t in tops] + [foot_top]
            for ri, top in enumerate(tops):
                bot = bounds[ri + 1]
                rw = [w for w in words if top - 0.5 <= w["top"] < bot - 0.5]
                if not rw:
                    continue
                text_all = " ".join(w["text"] for w in sorted(rw, key=lambda w: (round(w["top"] / 3), w["x0"])))
                # Bereichsüberschrift
                if SECTIONRE.match(text_all) and not TIMERE.search(text_all) and len(_lines(rw)) == 1:
                    section = text_all.replace("\x00", "fi")
                    out["sektionen"].append({"seite": pno, "name": section})
                    continue
                lab = [w for w in rw if (w["x0"] + w["x1"]) / 2 < left]
                lines = _lines(lab)
                label = " ".join(lines)
                role = None
                for r in ROLES:
                    if label.endswith(" " + r):
                        role = r; label = label[: -len(r) - 1].strip(); break
                name = label.strip()
                if not name:
                    continue
                out["personen"].append({"sektion": section, "name": name, "rolle": role, "seite": pno})
                for ci in range(7):
                    x0, x1 = left + ci * colw, left + (ci + 1) * colw
                    cw = [w for w in rw if x0 <= (w["x0"] + w["x1"]) / 2 < x1]
                    if not cw:
                        continue
                    txt = " ".join(_lines(cw))
                    shifts, other = parse_cell(txt)
                    out["zellen"].append({"seite": pno, "sektion": section, "name": name, "rolle": role,
                                          "datum": heads[ci]["datum"], "wd": heads[ci]["wd"],
                                          "shifts": shifts, "sonstiges": other, "roh": txt})
    return out


if __name__ == "__main__":
    json.dump([parse_pdf(p) for p in sys.argv[1:]], sys.stdout, ensure_ascii=False, indent=1)
