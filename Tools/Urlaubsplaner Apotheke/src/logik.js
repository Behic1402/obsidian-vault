/* Urlaubsplaner Apotheke – reine Logik (läuft in Node und im Browser). */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.Logik = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';
  const TAGE = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'];

  // ---------- Datum (nur Tageszahlen in UTC, keine lokale Zeit) ----------
  function dayNum(iso) {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
    if (!m) throw new Error('Ungültiges Datum: ' + iso);
    return Math.round(Date.UTC(+m[1], +m[2] - 1, +m[3]) / 86400000);
  }
  function isoFromDayNum(n) {
    const d = new Date(n * 86400000);
    const p = (x) => String(x).padStart(2, '0');
    return d.getUTCFullYear() + '-' + p(d.getUTCMonth() + 1) + '-' + p(d.getUTCDate());
  }
  const wtIdx = (iso) => (((dayNum(iso) + 3) % 7) + 7) % 7; // Mo = 0
  const wochentag = (iso) => TAGE[wtIdx(iso)];
  const montagVon = (iso) => isoFromDayNum(dayNum(iso) - wtIdx(iso));
  const addTage = (iso, n) => isoFromDayNum(dayNum(iso) + n);
  function isoKW(iso) {
    const n = dayNum(iso);
    const donnerstag = n - wtIdx(iso) + 3;
    const jahr = +isoFromDayNum(donnerstag).slice(0, 4);
    const neujahr = dayNum(jahr + '-01-01');
    return { jahr, kw: Math.floor((donnerstag - neujahr) / 7) + 1 };
  }
  const anzeigeDatum = (iso) => iso.slice(8) + '.' + iso.slice(5, 7) + '.' + iso.slice(0, 4);

  // ---------- Rollierung ----------
  function rollwoche(iso, gruppe, R) {
    const mon = dayNum(montagVon(iso));
    const startMon = dayNum(montagVon(R.start));
    if (mon < startMon) return null;
    let w = (mon - startMon) / 7;
    if (gruppe === 'Apotheker') {
      const davor = (R.feiertagssamstage || []).filter((s) => {
        const m = dayNum(montagVon(s));
        return m >= startMon && m < mon;
      }).length;
      w -= davor;
    }
    return (((w % 8) + 8) % 8) + 1;
  }

  // ---------- Zeitblöcke ----------
  const minuten = (hhmm) => { const [h, m] = hhmm.split(':').map(Number); return h * 60 + m; };
  const blockLabel = (b) => b.von + '–' + b.bis;
  const blockTyp = (tag) => (tag === 'Sa' ? 'Sa' : 'MoFr');
  const bloeckeVonTag = (tag, d) => d.bloecke.filter((b) => b.tagTyp === blockTyp(tag));
  function bloeckeFuer(eintrag, bloecke) {
    const v = minuten(eintrag.von), b = minuten(eintrag.bis);
    return bloecke
      .filter((bl) => Math.min(b, minuten(bl.bis)) - Math.max(v, minuten(bl.von)) > 0)
      .map(blockLabel);
  }

  // ---------- Besetzungsprüfung ----------
  const gruppeVon = (p) => (p.rollgruppe === 'Apotheker' ? 'Apotheker' : 'PTA');
  const abwSet = (d) => new Set(d.abwesenheiten.map((a) => a.datum + '|' + a.name));
  const feiertagVon = (iso, d) => { const f = d.feiertage.find((x) => x.datum === iso); return f ? f.name : null; };

  function pruefeTag(iso, d, set) {
    set = set || abwSet(d);
    const tag = wochentag(iso);
    const rollApo = rollwoche(iso, 'Apotheker', d.rollierung);
    const rollPta = rollwoche(iso, 'PTA', d.rollierung);
    const feiertag = feiertagVon(iso, d);
    const res = { datum: iso, tag, rollApo, rollPta, feiertag, bloecke: [] };
    if (tag === 'So' || rollPta === null) return res;
    const bl = bloeckeVonTag(tag, d);
    const geplant = {}; // label -> [{name, appr, abw}]
    bl.forEach((b) => (geplant[blockLabel(b)] = []));
    d.personal.filter((p) => p.aktiv && p.zaehlt).forEach((p) => {
      const roll = gruppeVon(p) === 'Apotheker' ? rollApo : rollPta;
      const labels = new Set();
      d.standardplan
        .filter((e) => e.name === p.name && e.tag === tag && e.ort === 'Filiale' && e.wochen.includes(roll))
        .forEach((e) => bloeckeFuer(e, bl).forEach((l) => labels.add(l)));
      const abw = set.has(iso + '|' + p.name);
      labels.forEach((l) => geplant[l].push({ name: p.name, appr: p.approbiert, abw }));
    });
    bl.forEach((b) => {
      const label = blockLabel(b);
      const regel = d.regeln.find((r) => r.tag === tag && r.von === b.von && r.bis === b.bis);
      const da = geplant[label].filter((x) => !x.abw);
      const istP = da.length, istA = da.filter((x) => x.appr).length;
      let ps, as;
      if (feiertag) ps = as = 'Feiertag';
      else if (!regel) ps = as = 'Regel fehlt';
      else {
        ps = istP < regel.minP ? 'Unterbesetzt' : 'OK';
        as = istA < regel.minA ? 'Kein Apotheker' : 'OK';
      }
      res.bloecke.push({
        label, minP: regel ? regel.minP : null, minA: regel ? regel.minA : null,
        nurAppr: !!(regel && regel.nurAppr), istP, istA, personalStatus: ps, apothekerStatus: as,
        anwesend: da.map((x) => x.name), abwesend: geplant[label].filter((x) => x.abw).map((x) => x.name),
      });
    });
    return res;
  }
  function pruefeWoche(iso, d) {
    const mon = montagVon(iso), set = abwSet(d);
    return [0, 1, 2, 3, 4, 5].map((i) => pruefeTag(addTage(mon, i), d, set));
  }
  const blockProblem = (b) => b.personalStatus === 'Unterbesetzt' || b.apothekerStatus === 'Kein Apotheker';
  function tagStatus(iso, d, set) {
    const t = pruefeTag(iso, d, set);
    if (t.tag === 'So' || t.rollPta === null) return 'leer';
    if (t.feiertag) return 'feiertag';
    return t.bloecke.some(blockProblem) ? 'warn' : 'ok';
  }
  function auswirkung(neue, d) {
    const nachher = Object.assign({}, d, { abwesenheiten: d.abwesenheiten.concat(neue) });
    const out = [];
    [...new Set(neue.map((n) => n.datum))].forEach((iso) => {
      const v = pruefeTag(iso, d), n = pruefeTag(iso, nachher);
      n.bloecke.forEach((b, i) => {
        if (blockProblem(b) && !blockProblem(v.bloecke[i])) {
          out.push({ datum: iso, label: b.label, status: [b.personalStatus, b.apothekerStatus].filter((s) => s !== 'OK').join(' + ') });
        }
      });
    });
    return out;
  }

  // ---------- Abwesenheiten, Resturlaub, Jahresübersicht ----------
  function addAbwesenheiten(d, a) {
    let hinzu = 0, uebersprungen = 0;
    const vorhanden = abwSet(d);
    for (let n = dayNum(a.von); n <= dayNum(a.bis || a.von); n++) {
      const iso = isoFromDayNum(n), key = iso + '|' + a.name;
      if (vorhanden.has(key)) { uebersprungen++; continue; }
      vorhanden.add(key);
      d.abwesenheiten.push({ datum: iso, name: a.name, art: a.art || 'Urlaub', genehmigt: a.genehmigt || 'ja', notiz: a.notiz || '' });
      hinzu++;
    }
    return { hinzu, uebersprungen };
  }
  function hatPlan(p, iso, d) {
    const roll = rollwoche(iso, gruppeVon(p), d.rollierung);
    const tag = wochentag(iso);
    return roll !== null && d.standardplan.some((e) => e.name === p.name && e.tag === tag && e.wochen.includes(roll));
  }
  function urlaubstage(name, jahr, d) {
    const p = d.personal.find((x) => x.name === name);
    if (!p) return 0;
    return d.abwesenheiten.filter((a) =>
      a.name === name && a.art === 'Urlaub' && a.datum.startsWith(jahr + '-') && wochentag(a.datum) !== 'So' &&
      !feiertagVon(a.datum, d) && hatPlan(p, a.datum, d)).length;
  }
  function resturlaub(name, jahr, d) {
    const p = d.personal.find((x) => x.name === name);
    if (!p || p.anspruch === null || p.anspruch === undefined || p.anspruch === '') return null;
    return p.anspruch - urlaubstage(name, jahr, d);
  }
  const KUERZEL = { Urlaub: 'U', Krank: 'K', Fortbildung: 'F', PBU: 'P', 'ÜS-Ausgleich': 'Ü', 'ÜS-frei': 'Ü', Sonstiges: 'S' };
  function jahresuebersicht(jahr, d) {
    return d.personal.map((p) => {
      const kws = {};
      d.abwesenheiten.filter((a) => a.name === p.name).forEach((a) => {
        const k = isoKW(a.datum);
        if (k.jahr === jahr && !kws[k.kw]) kws[k.kw] = KUERZEL[a.art] || 'S';
      });
      return { name: p.name, aktiv: p.aktiv, kws };
    });
  }

  return {
    TAGE, dayNum, isoFromDayNum, wochentag, montagVon, addTage, isoKW, anzeigeDatum, rollwoche,
    bloeckeFuer, blockLabel, bloeckeVonTag, pruefeTag, pruefeWoche, tagStatus, auswirkung,
    addAbwesenheiten, urlaubstage, resturlaub, jahresuebersicht, feiertagVon, blockProblem, KUERZEL,
  };
});
