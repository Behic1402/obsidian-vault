const test = require('node:test');
const assert = require('node:assert/strict');
const L = require('../src/logik.js');
const { seed } = require('../src/daten.js');
const d = seed();
const arbeitet = (name, tag, w, ort) => d.standardplan.some((e) => e.name === name && e.tag === tag && e.wochen.includes(w) && (!ort || e.ort === ort));
const wochenMit = (name, tag, ort) => [1, 2, 3, 4, 5, 6, 7, 8].filter((w) => arbeitet(name, tag, w, ort));

test('Matrix W1–W8: Samstage', () => {
  assert.deepEqual(wochenMit('Maren', 'Sa'), [2, 6]);
  assert.deepEqual(wochenMit('Katja', 'Sa'), [1, 5]);
  assert.deepEqual(wochenMit('Malte', 'Sa'), [4, 8]);
  assert.deepEqual(wochenMit('Tomke', 'Sa'), [3, 7]);
  assert.deepEqual(wochenMit('Marion I.', 'Sa'), [1, 3, 5, 7]);
  assert.deepEqual(wochenMit('Anja', 'Sa'), [2, 4, 6, 8]);
  assert.deepEqual(wochenMit('Rama', 'Sa'), [4, 8]);
  assert.deepEqual(wochenMit('Nick', 'Sa'), [1, 3, 5, 7]);
});
test('Matrix: freie Tage, Homeoffice, Wiederholungen', () => {
  assert.deepEqual(wochenMit('Katja', 'Fr'), [1, 3, 4, 5, 7, 8]);
  assert.deepEqual(wochenMit('Malte', 'Di'), [2, 3, 4, 5, 6, 7, 8]);
  assert.deepEqual(wochenMit('Tomke', 'Di', 'Homeoffice'), [2, 6]);
  assert.deepEqual(wochenMit('Tomke', 'Di', 'Filiale'), [1, 3, 4, 5, 8]);
  assert.ok(!arbeitet('Tomke', 'Di', 7));
  assert.deepEqual(wochenMit('Nick', 'Mi'), [1, 2, 4, 5, 6, 8]);
  ['Marion B.', 'Jutta'].forEach((n) => ['Mo', 'Di', 'Do'].forEach((t) => {
    const e = d.standardplan.filter((x) => x.name === n && x.tag === t);
    e.forEach((x) => assert.equal(x.wochen.length, 8));
  }));
  assert.ok(!d.standardplan.some((e) => e.name === 'Rama' && e.tag !== 'Sa'), 'Rama: kein Labor');
  assert.ok(!d.standardplan.some((e) => e.name === 'PhiP'));
});
test('Stammdaten und Regeln', () => {
  assert.equal(d.personal.find((p) => p.name === 'PhiP').aktiv, false);
  assert.equal(d.personal.find((p) => p.name === 'Nick').rolle, 'PTA-Praktikant');
  assert.equal(d.personal.find((p) => p.name === 'Nick').approbiert, false);
  assert.equal(d.regeln.length, 5 * 6 + 2);
  const sa = d.regeln.find((r) => r.tag === 'Sa' && r.von === '09:00');
  assert.deepEqual([sa.minP, sa.minA], [3, 1]);
  assert.deepEqual(d.rollierung.feiertagssamstage, ['2027-05-01', '2027-12-25', '2028-01-01']);
  d.rollierung.feiertagssamstage.forEach((s) => assert.equal(L.wochentag(s), 'Sa'));
});
test('Gegenprobe zum alten Standardplan (Blöcke je Apotheker)', () => {
  const blocks = (name, tag) => {
    const bl = L.bloeckeVonTag(tag, d); const s = new Set();
    d.standardplan.filter((e) => e.name === name && e.tag === tag).forEach((e) => L.bloeckeFuer(e, bl).forEach((l) => s.add(l)));
    return [...s].sort();
  };
  assert.equal(blocks('Tomke', 'Mo').join(), ['08:00–08:30', '08:30–12:00', '12:00–15:00', '15:00–18:00'].join());
  assert.equal(blocks('Katja', 'Mo').length, 6);
  assert.equal(blocks('Malte', 'Di').join(), ['08:30–12:00', '12:00–15:00', '15:00–18:00', '18:00–18:30', '18:30–19:00'].join());
  assert.equal(blocks('Maren', 'Do').length, 6);
  assert.equal(blocks('Maren', 'Fr').length, 3);
  assert.equal(blocks('Katja', 'Fr').length, 2);
  assert.equal(blocks('Katja', 'Mi').length, 5);
  assert.equal(blocks('Tomke', 'Do').length, 4);
  assert.equal(blocks('Katja', 'Sa').join(), ['09:00–13:00', '13:00–13:30'].join());
});
