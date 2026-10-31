/* Seed-Stammdaten (keine Abwesenheiten). Quelle: Übergabe + Excel-Vorlage von Behic. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.Daten = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';
  const ALLE = [1, 2, 3, 4, 5, 6, 7, 8];
  const ohne = (...x) => ALLE.filter((w) => !x.includes(w));
  const P = [];
  function plan(name, tag, wochen, zeiten, ort, unbestaetigt) {
    zeiten.forEach((z) => {
      const [von, bis] = z.split('-');
      const e = { name, wochen, tag, von, bis, ort: ort || 'Filiale' };
      if (unbestaetigt) e.unbestaetigt = true;
      P.push(e);
    });
  }
  // Apotheker (Zeiten aus Excel-Vorlage)
  plan('Tomke', 'Mo', ALLE, ['08:00-14:00', '15:00-18:00']);
  plan('Katja', 'Mo', ALLE, ['08:00-13:00', '14:00-19:00']);
  plan('Malte', 'Di', ohne(1), ['09:00-12:00', '13:00-19:00']);
  plan('Tomke', 'Di', [1, 3, 4, 5, 8], ['08:00-13:00', '14:00-19:00']);
  plan('Tomke', 'Di', [2, 6], ['08:00-19:00'], 'Homeoffice');
  plan('Katja', 'Di', ALLE, ['08:00-13:00']);
  plan('Malte', 'Mi', ALLE, ['09:00-12:00', '13:00-19:00']);
  plan('Katja', 'Mi', ALLE, ['08:00-13:00', '14:00-18:30']);
  plan('Maren', 'Do', ALLE, ['08:00-14:00', '15:00-19:00']);
  plan('Tomke', 'Do', ALLE, ['08:00-13:00', '14:00-18:00']);
  plan('Maren', 'Fr', ALLE, ['08:00-13:00']);
  plan('Tomke', 'Fr', ALLE, ['08:00-13:00', '14:00-19:00']);
  plan('Katja', 'Fr', ohne(2, 6), ['09:00-14:00']);
  plan('Katja', 'Sa', [1, 5], ['09:00-13:30']);
  plan('Maren', 'Sa', [2, 6], ['09:00-13:30']);
  plan('Tomke', 'Sa', [3, 7], ['09:00-13:30']);
  plan('Malte', 'Sa', [4, 8], ['09:00-13:30']);
  // PTA (Zeiten aus Übergabe)
  plan('Marion B.', 'Mo', ALLE, ['14:00-18:30']);
  plan('Marion B.', 'Di', ALLE, ['13:00-18:00']);
  plan('Marion B.', 'Mi', ALLE, ['07:45-13:15']);
  plan('Marion B.', 'Do', ALLE, ['08:00-13:00']);
  plan('Jutta', 'Mo', ALLE, ['08:00-14:00']);
  plan('Jutta', 'Di', ALLE, ['07:45-18:30']);
  plan('Jutta', 'Do', ALLE, ['14:00-18:30']);
  plan('Jutta', 'Fr', ALLE, ['07:45-18:30']);
  plan('Marion I.', 'Mo', ALLE, ['07:45-13:00']);
  plan('Marion I.', 'Di', ALLE, ['08:00-13:00']);
  plan('Marion I.', 'Mi', ALLE, ['08:00-18:30']);
  plan('Marion I.', 'Fr', ALLE, ['08:00-13:00']);
  plan('Marion I.', 'Sa', [1, 3, 5, 7], ['08:45-13:15']);
  plan('Anja', 'Mi', ALLE, ['09:00-13:00']);
  plan('Anja', 'Do', ALLE, ['08:00-13:00']);
  plan('Anja', 'Fr', ALLE, ['08:00-18:00']);
  plan('Anja', 'Sa', [2, 4, 6, 8], ['08:45-13:00']);
  plan('Rama', 'Sa', [4, 8], ['09:00-13:00']); // Labor bewusst nicht eingetragen
  ['Mo', 'Di', 'Do'].forEach((t) => plan('Nick', t, ALLE, ['09:00-18:00']));
  plan('Nick', 'Mi', ohne(3, 7), ['09:00-18:00']);
  plan('Nick', 'Fr', ALLE, ['10:00-18:00']);
  plan('Nick', 'Sa', [1, 3, 5, 7], ['09:00-13:00']);

  const pers = (name, rolle, appr, gruppe, aktiv, hinweis) =>
    ({ name, rolle, approbiert: appr, rollgruppe: gruppe, aktiv, zaehlt: true, anspruch: null, hinweis: hinweis || '' });
  const personal = [
    pers('Tomke', 'Apotheker/in', true, 'Apotheker', true, 'Büro = Homeoffice, zählt nicht zur Filiale'),
    pers('Katja', 'Apotheker/in', true, 'Apotheker', true),
    pers('Malte', 'Apotheker/in', true, 'Apotheker', true),
    pers('Maren', 'Apotheker/in', true, 'Apotheker', true),
    pers('Marion I.', 'PTA', false, 'PTA', true),
    pers('Marion B.', 'PTA', false, 'PTA', true),
    pers('Jutta', 'PTA', false, 'PTA', true),
    pers('Anja', 'PTA', false, 'PTA', true),
    pers('Rama', 'PTA', false, 'PTA', true, 'Laborzeiten zählen nicht; nur Samstag'),
    pers('Nick', 'PTA-Praktikant', false, 'PTA', true, 'Mit Aktiv = nein aus der Planung nehmen'),
    pers('PhiP', 'PhiP', false, 'PTA', false, '2027 noch kein Plan bekannt'),
  ];

  const MOFR = [['08:00', '08:30', 2, 1], ['08:30', '12:00', 4, 1], ['12:00', '15:00', 2, 1],
    ['15:00', '18:00', 3, 1], ['18:00', '18:30', 2, 1], ['18:30', '19:00', 1, 1, true]];
  const SA = [['09:00', '13:00', 3, 1], ['13:00', '13:30', 1, 1, true]];
  const bloecke = MOFR.map((b) => ({ tagTyp: 'MoFr', von: b[0], bis: b[1] }))
    .concat(SA.map((b) => ({ tagTyp: 'Sa', von: b[0], bis: b[1] })));
  const regeln = [];
  ['Mo', 'Di', 'Mi', 'Do', 'Fr'].forEach((t) => MOFR.forEach((b) => regeln.push({ tag: t, von: b[0], bis: b[1], minP: b[2], minA: b[3], nurAppr: !!b[4] })));
  SA.forEach((b) => regeln.push({ tag: 'Sa', von: b[0], bis: b[1], minP: b[2], minA: b[3], nurAppr: !!b[4] }));

  const f = (datum, name) => ({ datum, name });
  const feiertage = [
    f('2026-01-01', 'Neujahr'), f('2026-04-03', 'Karfreitag'), f('2026-04-06', 'Ostermontag'), f('2026-05-01', 'Tag der Arbeit'),
    f('2026-05-14', 'Christi Himmelfahrt'), f('2026-05-25', 'Pfingstmontag'), f('2026-06-04', 'Fronleichnam'),
    f('2026-10-03', 'Tag der Deutschen Einheit'), f('2026-11-01', 'Allerheiligen'), f('2026-12-25', '1. Weihnachtstag'), f('2026-12-26', '2. Weihnachtstag'),
    f('2027-01-01', 'Neujahr'), f('2027-03-26', 'Karfreitag'), f('2027-03-29', 'Ostermontag'), f('2027-05-01', 'Tag der Arbeit'),
    f('2027-05-06', 'Christi Himmelfahrt'), f('2027-05-17', 'Pfingstmontag'), f('2027-05-27', 'Fronleichnam'),
    f('2027-10-03', 'Tag der Deutschen Einheit'), f('2027-11-01', 'Allerheiligen'), f('2027-12-25', '1. Weihnachtstag'), f('2027-12-26', '2. Weihnachtstag'),
    f('2028-01-01', 'Neujahr'), f('2028-04-14', 'Karfreitag'), f('2028-04-17', 'Ostermontag'), f('2028-05-01', 'Tag der Arbeit'),
    f('2028-05-25', 'Christi Himmelfahrt'), f('2028-06-05', 'Pfingstmontag'), f('2028-06-15', 'Fronleichnam'),
    f('2028-10-03', 'Tag der Deutschen Einheit'), f('2028-11-01', 'Allerheiligen'), f('2028-12-25', '1. Weihnachtstag'), f('2028-12-26', '2. Weihnachtstag'),
  ];

  function seed() {
    return JSON.parse(JSON.stringify({
      personal, standardplan: P, bloecke, regeln, feiertage, abwesenheiten: [],
      rollierung: { start: '2026-12-28', feiertagssamstage: ['2027-05-01', '2027-12-25', '2028-01-01'] },
    }));
  }
  return { seed };
});
