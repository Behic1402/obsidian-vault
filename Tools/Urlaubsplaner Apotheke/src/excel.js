/* Excel-Import/-Export (ohne SheetJS-Abhängigkeit: liefert/erwartet Zeilen-Arrays). */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(require('./logik.js'));
  else root.Excel = factory(root.Logik);
})(typeof self !== 'undefined' ? self : this, function (L) {
  'use strict';
  function zuIso(v) {
    if (v instanceof Date && !isNaN(v)) return new Date(v.getTime() + 12 * 3600e3).toISOString().slice(0, 10);
    if (typeof v === 'number') return L.isoFromDayNum(L.dayNum('1899-12-30') + Math.floor(v));
    if (typeof v === 'string') {
      let m = /^(\d{4})-(\d{2})-(\d{2})/.exec(v.trim());
      if (m) return m[1] + '-' + m[2] + '-' + m[3];
      m = /^(\d{1,2})\.(\d{1,2})\.(\d{4})/.exec(v.trim());
      if (m) return m[3] + '-' + m[2].padStart(2, '0') + '-' + m[1].padStart(2, '0');
    }
    return null;
  }
  function art(grund) {
    const g = String(grund || '').trim();
    if (/^urlaub$/i.test(g)) return { art: 'Urlaub', notiz: '' };
    if (/^pbu$/i.test(g)) return { art: 'PBU', notiz: '' };
    if (/^ü?s?-?\s*ausgleich/i.test(g) || /^ÜS-Ausgleich$/i.test(g)) return { art: 'ÜS-Ausgleich', notiz: '' };
    if (/^ÜS-frei/i.test(g)) return { art: 'ÜS-frei', notiz: g === 'ÜS-frei' ? '' : g };
    if (/^krank/i.test(g)) return { art: 'Krank', notiz: '' };
    if (/^fortbildung/i.test(g)) return { art: 'Fortbildung', notiz: '' };
    return { art: 'Sonstiges', notiz: g };
  }
  function parseAbwesenheiten(rows, d) {
    const namen = new Map(d.personal.map((p) => [p.name, p.name]));
    const eintraege = [], unbekannte = new Set(), gesehen = new Set();
    let ignoriert = 0;
    rows.forEach((r) => {
      const iso = r && zuIso(r[0]);
      let name = r && r[1] != null ? String(r[1]).replace(/\s*\(Ich\)\s*/i, '').trim() : '';
      if (!iso || !name) { ignoriert++; return; }
      if (!namen.has(name)) { unbekannte.add(name); return; }
      const key = iso + '|' + name;
      if (gesehen.has(key)) return;
      gesehen.add(key);
      const a = art(r[3]);
      const gen = String(r[7] == null ? 'ja' : r[7]).trim();
      const ja = /^(ja|nein)$/i.test(gen) || gen === '';
      const notiz = [a.notiz, ja ? '' : 'Genehmigt: ' + gen].filter(Boolean).join(' · ');
      eintraege.push({ datum: iso, name, art: a.art, genehmigt: gen.toLowerCase() === 'nein' ? 'nein' : 'ja', notiz });
    });
    return { eintraege, unbekannteNamen: [...unbekannte], ignoriert };
  }
  function exportWochenplan(woche) {
    const rows = [['Datum', 'Tag', 'Zeitblock', 'Min. Personen', 'Min. Approbierte', 'Ist Personen', 'Ist Approbierte', 'Personal-Status', 'Apotheker-Status', 'Abwesend', 'Anwesend', 'Rollwoche Apotheker', 'Rollwoche PTA']];
    woche.forEach((t) => {
      if (!t.bloecke.length) rows.push([L.anzeigeDatum(t.datum), t.tag, t.feiertag || 'vor Rollierungsbeginn']);
      t.bloecke.forEach((b) => rows.push([L.anzeigeDatum(t.datum), t.tag, b.label, b.minP, b.minA, b.istP, b.istA, b.personalStatus, b.apothekerStatus, b.abwesend.join(', '), b.anwesend.join(', '), 'W' + t.rollApo, 'W' + t.rollPta]));
    });
    return { name: 'Wochenplan', rows };
  }
  function exportJahr(uebersicht) {
    const kopf = ['Mitarbeiter']; for (let k = 1; k <= 53; k++) kopf.push('KW' + k);
    const rows = [kopf];
    uebersicht.forEach((u) => { const z = [u.name]; for (let k = 1; k <= 53; k++) z.push(u.kws[k] || ''); rows.push(z); });
    return { name: 'Jahresübersicht', rows };
  }
  function exportAbwesenheiten(d) {
    const rows = [['Datum', 'Name', 'Art', 'Genehmigt?', 'Notiz']];
    d.abwesenheiten.slice().sort((a, b) => a.datum.localeCompare(b.datum)).forEach((a) => rows.push([L.anzeigeDatum(a.datum), a.name, a.art, a.genehmigt, a.notiz || '']));
    return { name: 'Abwesenheiten', rows };
  }
  return { parseAbwesenheiten, exportWochenplan, exportJahr, exportAbwesenheiten, zuIso };
});
