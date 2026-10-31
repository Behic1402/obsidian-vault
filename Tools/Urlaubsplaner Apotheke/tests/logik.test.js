const test = require('node:test');
const assert = require('node:assert/strict');
const L = require('../src/logik.js');
const { seed } = require('../src/daten.js');

const R = { start: '2026-12-28', feiertagssamstage: ['2027-05-01'] };

test('Rollierung: Startpunkt und 8-Wochen-Zyklus', () => {
  assert.equal(L.rollwoche('2026-12-28', 'PTA', R), 1);
  assert.equal(L.rollwoche('2027-01-03', 'PTA', R), 1); // Sonntag derselben Woche
  assert.equal(L.rollwoche('2027-01-04', 'PTA', R), 2);
  assert.equal(L.rollwoche('2027-02-22', 'PTA', R), 1);
  assert.equal(L.rollwoche('2026-06-01', 'PTA', R), null);
});
test('Rollierung: Feiertagssamstag verschiebt nur Apotheker', () => {
  assert.equal(L.rollwoche('2027-04-26', 'PTA', R), 2);
  assert.equal(L.rollwoche('2027-04-26', 'Apotheker', R), 2);
  assert.equal(L.rollwoche('2027-05-03', 'PTA', R), 3);
  assert.equal(L.rollwoche('2027-05-03', 'Apotheker', R), 2);
  assert.equal((L.rollwoche('2027-06-14', 'PTA', R) - L.rollwoche('2027-06-14', 'Apotheker', R) + 8) % 8, 1);
  assert.equal(L.rollwoche('2027-04-19', 'Apotheker', R), L.rollwoche('2027-04-19', 'PTA', R));
});
test('Datum: KW über Jahreswechsel, Wochentag, Montag', () => {
  assert.deepEqual(L.isoKW('2026-12-31'), { jahr: 2026, kw: 53 });
  assert.deepEqual(L.isoKW('2027-01-01'), { jahr: 2026, kw: 53 });
  assert.deepEqual(L.isoKW('2027-01-04'), { jahr: 2027, kw: 1 });
  assert.equal(L.wochentag('2026-12-28'), 'Mo');
  assert.equal(L.montagVon('2027-01-03'), '2026-12-28');
  assert.equal(L.anzeigeDatum('2027-01-04'), '04.01.2027');
});

test('Besetzung: Standardwoche, Homeoffice, Abwesenheit', () => {
  const d = seed();
  const mo = L.pruefeTag('2027-01-04', d);
  assert.equal(mo.rollPta, 2); assert.equal(mo.rollApo, 2);
  const b = mo.bloecke.find((x) => x.label === '08:30–12:00');
  assert.deepEqual([b.istP, b.istA, b.personalStatus, b.apothekerStatus], [5, 2, 'OK', 'OK']);
  const di = L.pruefeTag('2027-01-05', d).bloecke[0];
  assert.ok(!di.anwesend.includes('Tomke') && !di.abwesend.includes('Tomke'), 'Homeoffice zählt nicht');
  d.abwesenheiten.push({ datum: '2027-01-04', name: 'Katja', art: 'Urlaub', genehmigt: 'ja' });
  const b2 = L.pruefeTag('2027-01-04', d).bloecke.find((x) => x.label === '08:30–12:00');
  assert.equal(b2.istP, 4); assert.deepEqual(b2.abwesend, ['Katja']);
  const spaet = L.pruefeTag('2027-01-04', d).bloecke.find((x) => x.label === '18:30–19:00');
  assert.equal(spaet.apothekerStatus, 'Kein Apotheker');
  d.abwesenheiten.push({ datum: '2027-01-04', name: 'Tomke', art: 'Urlaub', genehmigt: 'ja' });
  const b3 = L.pruefeTag('2027-01-04', d).bloecke.find((x) => x.label === '08:30–12:00');
  assert.deepEqual([b3.personalStatus, b3.apothekerStatus], ['Unterbesetzt', 'Kein Apotheker']);
});
test('Besetzung: Aktiv=nein, Abwesenheit ohne Plan, Feiertag, vor Start, fehlende Regel', () => {
  const d = seed();
  d.personal.find((p) => p.name === 'Nick').aktiv = false;
  const t = L.pruefeTag('2027-01-04', d).bloecke.find((x) => x.label === '08:30–12:00');
  assert.ok(!t.anwesend.includes('Nick') && !t.abwesend.includes('Nick'));
  d.abwesenheiten.push({ datum: '2027-01-04', name: 'Maren', art: 'Urlaub', genehmigt: 'ja' });
  assert.ok(!L.pruefeTag('2027-01-04', d).bloecke.some((b) => b.abwesend.includes('Maren')));
  const f = L.pruefeTag('2027-05-06', d);
  assert.equal(f.feiertag, 'Christi Himmelfahrt');
  assert.ok(f.bloecke.every((b) => b.personalStatus === 'Feiertag'));
  assert.equal(L.pruefeTag('2026-06-01', d).rollPta, null);
  assert.equal(L.pruefeTag('2026-06-01', d).bloecke.length, 0);
  d.regeln = d.regeln.filter((r) => !(r.tag === 'Mo' && r.von === '12:00'));
  assert.equal(L.pruefeTag('2027-01-04', d).bloecke.find((x) => x.label === '12:00–15:00').personalStatus, 'Regel fehlt');
});
test('Auswirkung: neue Abwesenheit zeigt gekippte Blöcke', () => {
  const d = seed();
  const a = L.auswirkung([{ datum: '2027-01-04', name: 'Tomke' }, { datum: '2027-01-04', name: 'Katja' }], d);
  assert.ok(a.some((x) => x.label === '08:30–12:00'));
  assert.deepEqual(L.auswirkung([{ datum: '2027-01-04', name: 'Maren' }], d), []);
});
test('Abwesenheiten, Urlaubstage, Resturlaub, Jahresübersicht', () => {
  const d = seed();
  assert.deepEqual(L.addAbwesenheiten(d, { name: 'Maren', von: '2027-05-03', bis: '2027-05-09', art: 'Urlaub' }), { hinzu: 7, uebersprungen: 0 });
  assert.deepEqual(L.addAbwesenheiten(d, { name: 'Maren', von: '2027-05-03', bis: '2027-05-09', art: 'Urlaub' }), { hinzu: 0, uebersprungen: 7 });
  assert.equal(L.urlaubstage('Maren', 2027, d), 2); // Fr 07.05. + Sa 08.05. (Apotheker-W2 hat Maren am Samstag); Do = Feiertag, Mo/Di/Mi nicht im Plan, So zählt nie
  assert.equal(L.resturlaub('Maren', 2027, d), null);
  d.personal.find((p) => p.name === 'Maren').anspruch = 30;
  assert.equal(L.resturlaub('Maren', 2027, d), 28); // 30 minus Fr und Sa
  L.addAbwesenheiten(d, { name: 'Katja', von: '2027-01-01', art: 'Urlaub' });
  assert.equal(L.jahresuebersicht(2026, d).find((x) => x.name === 'Katja').kws[53], 'U');
  assert.equal(L.jahresuebersicht(2027, d).find((x) => x.name === 'Katja').kws[53], undefined);
});
