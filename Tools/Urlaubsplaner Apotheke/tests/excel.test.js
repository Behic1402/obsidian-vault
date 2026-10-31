const test = require('node:test');
const assert = require('node:assert/strict');
const E = require('../src/excel.js');
const L = require('../src/logik.js');
const { seed } = require('../src/daten.js');

test('Import: Datumsformate, Namen, Gründe, Dubletten, Leerzeilen', () => {
  const d = seed();
  const rows = [
    [new Date('2026-02-02T00:00:00'), 'Malte', 'ja', 'Urlaub', 'KW6', 'Montag', null, 'ja'],
    [46056, 'Tomke (Ich)', 'ja', 'PBU', null, null, null, 'nein'],
    ['03.02.2026', 'Malte', 'ja', 'Kegeltreff', null, null, null, null],
    [new Date('2026-02-02T00:00:00'), 'Malte', 'ja', 'Urlaub'],
    ['2026-02-04', 'Unbekannt', 'ja', 'Urlaub'],
    [null, null], ['Datum', 'Name'],
  ];
  const r = E.parseAbwesenheiten(rows, d);
  assert.equal(r.eintraege.length, 3);
  assert.deepEqual(r.eintraege[0], { datum: '2026-02-02', name: 'Malte', art: 'Urlaub', genehmigt: 'ja', notiz: '' });
  assert.equal(r.eintraege[1].name, 'Tomke'); assert.equal(r.eintraege[1].genehmigt, 'nein');
  assert.equal(r.eintraege[2].art, 'Sonstiges'); assert.equal(r.eintraege[2].notiz, 'Kegeltreff');
  assert.deepEqual(r.unbekannteNamen, ['Unbekannt']);
  assert.equal(r.ignoriert, 2);
});
test('Export: Wochenplan und Jahr', () => {
  const d = seed();
  const w = E.exportWochenplan(L.pruefeWoche('2027-01-04', d));
  assert.equal(w.rows[0][0], 'Datum'); assert.equal(w.rows.length, 1 + 5 * 6 + 2);
  const j = E.exportJahr(L.jahresuebersicht(2027, d));
  assert.equal(j.rows[0].length, 54);
});
