/* Oberfläche. Alle Daten bleiben lokal im Browser (localStorage). */
(function () {
  'use strict';
  const KEY = 'urlaubsplaner.v1';
  const ARTEN = ['Urlaub', 'Krank', 'Fortbildung', 'PBU', 'ÜS-Ausgleich', 'ÜS-frei', 'Sonstiges'];
  const ROLLEN = { 'Apotheker/in': ['Apotheker', true], PTA: ['PTA', false], 'PTA-Praktikant': ['PTA', false], PhiP: ['PTA', false] };
  const TABS = [['woche', 'Wochenprüfung'], ['kalender', 'Kalender'], ['abw', 'Abwesenheiten'], ['personal', 'Personal'], ['plan', 'Standardplan'], ['regeln', 'Regeln & Rollierung'], ['daten', 'Daten']];
  const MONATE = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'];
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const L = Logik, E = Excel;

  function laden() {
    try {
      const j = JSON.parse(localStorage.getItem(KEY) || 'null');
      if (j && gueltig(j)) return j;
    } catch (e) { /* defekte Daten ignorieren */ }
    return Daten.seed();
  }
  function gueltig(j) {
    return j && ['personal', 'standardplan', 'bloecke', 'regeln', 'feiertage', 'abwesenheiten'].every((k) => Array.isArray(j[k])) &&
      j.rollierung && /^\d{4}-\d{2}-\d{2}$/.test(j.rollierung.start) && Array.isArray(j.rollierung.feiertagssamstage);
  }
  function speichern() { try { localStorage.setItem(KEY, JSON.stringify(S.d)); } catch (e) { S.meldung = ['bad', 'Speichern im Browser nicht möglich – bitte JSON-Sicherung exportieren.']; } }
  function heute() { const n = new Date(); return n.getFullYear() + '-' + String(n.getMonth() + 1).padStart(2, '0') + '-' + String(n.getDate()).padStart(2, '0'); }

  const S = { tab: 'woche', d: laden(), meldung: null, form: { name: '', von: '', bis: '', art: 'Urlaub', genehmigt: 'ja', notiz: '' }, planPerson: null, filterName: '', filterJahr: null };
  S.datum = heute() < S.d.rollierung.start ? S.d.rollierung.start : heute();
  S.jahr = +S.datum.slice(0, 4); S.monat = +S.datum.slice(5, 7); S.filterJahr = 0;
  S.planPerson = (S.d.personal[0] || {}).name || null; S.form.name = S.planPerson || '';

  const chip = (st) => `<span class="chip ${st === 'OK' ? 's-OK' : st === 'Feiertag' ? 's-Feiertag' : st === 'Regel fehlt' ? 's-Regel' : 's-bad'}">${esc(st)}</span>`;
  const opt = (arr, sel) => arr.map((x) => `<option${x === sel ? ' selected' : ''}>${esc(x)}</option>`).join('');
  const namenOpt = (sel, nurAktiv) => S.d.personal.filter((p) => !nurAktiv || p.aktiv).map((p) => `<option${p.name === sel ? ' selected' : ''}>${esc(p.name)}</option>`).join('');
  const meldungHtml = () => { const m = S.meldung; S.meldung = null; return m ? `<div class="${m[0] === 'ok' ? 'okbox' : m[0] === 'info' ? 'info' : 'warnbox'}" role="status">${esc(m[1])}</div>` : ''; };

  // ---------- Wochenprüfung ----------
  function tabWoche() {
    const mon = L.montagVon(S.datum), kw = L.isoKW(mon);
    const woche = L.pruefeWoche(S.datum, S.d);
    const t0 = woche[0];
    let h = `<div class="card noprint"><div class="row">
      <button class="btn sec" data-a="wocheMinus">◀ Vorherige</button>
      <label>Datum in der Woche<input type="date" data-c="datum" value="${S.datum}"></label>
      <label>Kalenderwoche<input type="number" data-c="kw" value="${kw.kw}" min="1" max="53"></label>
      <button class="btn sec" data-a="wochePlus">Nächste ▶</button>
      <button class="btn sec" data-a="heute">Heute</button></div></div>`;
    h += `<div class="card"><h2>KW ${kw.kw}/${kw.jahr} · ${L.anzeigeDatum(mon)} – ${L.anzeigeDatum(L.addTage(mon, 5))}</h2>`;
    if (t0.rollPta === null) {
      h += `<div class="info">Diese Woche liegt vor dem Rollierungsbeginn (${L.anzeigeDatum(S.d.rollierung.start)}). Es gibt keinen Standardplan, daher keine Prüfung.</div></div>`;
      return h;
    }
    h += `<p>Rollwoche <b>PTA: W${t0.rollPta}</b> · Rollwoche <b>Apotheker: W${t0.rollApo}</b>${t0.rollPta !== t0.rollApo ? ' <span class="mut">(Apotheker liegt wegen Feiertagssamstag eine Woche zurück)</span>' : ''}</p></div>`;
    woche.forEach((t) => {
      const probleme = t.bloecke.filter(L.blockProblem).length;
      const gesamt = t.feiertag ? chip('Feiertag') : probleme ? `<span class="chip s-bad">${probleme} Block${probleme > 1 ? 'e' : ''} kritisch</span>` : chip('OK');
      h += `<div class="card"><div class="tagkopf"><h3>${t.tag} ${L.anzeigeDatum(t.datum)}</h3>${t.feiertag ? `<span class="mut">${esc(t.feiertag)}</span>` : ''}${gesamt}</div>`;
      h += `<div class="scroll"><table><tr><th>Zeitblock</th><th>Soll P/A</th><th>Ist P/A</th><th>Personal</th><th>Apotheker</th><th>Abwesend</th><th>Anwesend</th></tr>`;
      t.bloecke.forEach((b) => {
        h += `<tr><td>${b.label}</td><td>${b.minP == null ? '–' : b.minP + ' / ' + b.minA}${b.nurAppr ? ' (nur approb.)' : ''}</td><td>${b.istP} / ${b.istA}</td><td>${chip(b.personalStatus)}</td><td>${chip(b.apothekerStatus)}</td><td>${esc(b.abwesend.join(', '))}</td><td class="small">${esc(b.anwesend.join(', '))}</td></tr>`;
      });
      h += `</table></div></div>`;
    });
    return h;
  }

  // ---------- Kalender ----------
  function tabKalender() {
    const erster = `${S.jahr}-${String(S.monat).padStart(2, '0')}-01`;
    const start = L.montagVon(erster);
    const set = new Set(S.d.abwesenheiten.map((a) => a.datum + '|' + a.name));
    let h = `<div class="card noprint"><div class="row"><button class="btn sec" data-a="monatMinus">◀</button><b>${MONATE[S.monat - 1]} ${S.jahr}</b><button class="btn sec" data-a="monatPlus">▶</button>
      <label>Jahr<input type="number" data-c="jahr" value="${S.jahr}" min="2020" max="2100"></label></div></div>`;
    h += `<div class="card"><div class="kal">${['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'].map((t) => `<div class="kh">${t}</div>`).join('')}`;
    for (let i = 0; i < 42; i++) {
      const iso = L.addTage(start, i);
      if (i >= 35 && +iso.slice(5, 7) !== S.monat) break;
      const imMonat = +iso.slice(5, 7) === S.monat;
      const st = L.tagStatus(iso, S.d, set);
      const abw = S.d.abwesenheiten.filter((a) => a.datum === iso);
      const fei = L.feiertagVon(iso, S.d);
      h += `<div class="z ${st === 'warn' ? 'warn' : st === 'feiertag' || fei ? 'feiertag' : ''} ${imMonat ? '' : 'out'} ${L.wochentag(iso).toLowerCase()}" data-a="gotoTag" data-v="${iso}" title="${st === 'warn' ? 'Unterbesetzung – anklicken für Details' : ''}">
        <b>${+iso.slice(8)}</b>${st === 'warn' ? ' <span class="chip s-bad">!</span>' : ''}${fei ? `<div class="mut">${esc(fei)}</div>` : ''}
        ${abw.map((a) => `<span class="pill a-${esc(a.art)}">${esc(a.name)}</span>`).join('')}</div>`;
    }
    h += `</div><p class="small mut">Rot = mindestens ein Zeitblock unterbesetzt oder ohne Apotheker. Violett = Feiertag. Klick auf einen Tag öffnet die Wochenprüfung.</p></div>`;
    const ue = L.jahresuebersicht(S.jahr, S.d);
    h += `<div class="card"><h2>Jahresübersicht ${S.jahr}</h2><div class="scroll"><table class="jt"><tr><th>Name</th>${Array.from({ length: 53 }, (_, i) => `<th>${i + 1}</th>`).join('')}</tr>`;
    ue.forEach((u) => {
      h += `<tr><td>${esc(u.name)}${u.aktiv ? '' : ' <span class="mut">(inaktiv)</span>'}</td>${Array.from({ length: 53 }, (_, i) => `<td>${u.kws[i + 1] ? `<span class="pill a-${esc(artVonKuerzel(u.kws[i + 1]))}">${esc(u.kws[i + 1])}</span>` : ''}</td>`).join('')}</tr>`;
    });
    h += `</table></div><p class="small mut">Kürzel: U Urlaub · K Krank · F Fortbildung · P PBU · Ü ÜS-Ausgleich/-frei · S Sonstiges. Zuordnung nach ISO-Kalenderwoche des Datums.</p></div>`;
    return h;
  }
  const artVonKuerzel = (k) => ({ U: 'Urlaub', K: 'Krank', F: 'Fortbildung', P: 'PBU', 'Ü': 'ÜS-Ausgleich', S: 'Sonstiges' }[k]);

  // ---------- Abwesenheiten ----------
  function neueAbwesenheiten() {
    const f = S.form;
    if (!f.name || !f.von) return [];
    const bis = f.bis && f.bis >= f.von ? f.bis : f.von;
    const vorhanden = new Set(S.d.abwesenheiten.map((a) => a.datum + '|' + a.name));
    const out = [];
    for (let n = L.dayNum(f.von); n <= L.dayNum(bis); n++) { const iso = L.isoFromDayNum(n); if (!vorhanden.has(iso + '|' + f.name)) out.push({ datum: iso, name: f.name }); }
    return out;
  }
  function tabAbw() {
    const f = S.form;
    let h = meldungHtml() + `<div class="card"><h2>Abwesenheit eintragen</h2><div class="row">
      <label>Person<select data-f="name">${namenOpt(f.name, false)}</select></label>
      <label>Von<input type="date" data-f="von" value="${f.von}"></label>
      <label>Bis<input type="date" data-f="bis" value="${f.bis}"></label>
      <label>Art<select data-f="art">${opt(ARTEN, f.art)}</select></label>
      <label>Genehmigt?<select data-f="genehmigt">${opt(['ja', 'nein'], f.genehmigt)}</select></label>
      <label>Notiz<input data-f="notiz" value="${esc(f.notiz)}"></label>
      <button class="btn" data-a="abwSpeichern">Eintragen</button></div>`;
    const neu = neueAbwesenheiten();
    if (neu.length && f.art !== 'Krank') {
      const eff = L.auswirkung(neu, S.d);
      h += eff.length
        ? `<div class="warnbox"><b>Achtung: Diese Abwesenheit führt zu Unterbesetzung</b> (${eff.length} Block${eff.length > 1 ? 'e' : ''}):<ul>${eff.slice(0, 20).map((e) => `<li>${L.wochentag(e.datum)} ${L.anzeigeDatum(e.datum)}, ${e.label}: ${esc(e.status)}</li>`).join('')}</ul></div>`
        : `<div class="okbox">Keine zusätzliche Unterbesetzung durch diese Abwesenheit (${neu.length} Tag${neu.length > 1 ? 'e' : ''}).</div>`;
    }
    h += `<p class="small mut">Die Prüfung läuft sofort beim Ausfüllen. Wochenenden werden mit gespeichert und zählen nur, wenn die Person an dem Tag laut Standardplan arbeitet.</p></div>`;
    h += `<div class="card noprint"><h2>Import aus Excel</h2><p class="small mut">Liest das Blatt „Abwesenheiten“ (Datum, Name, Grund …) deiner bisherigen Excel-Datei. Die Daten bleiben im Browser.</p><input type="file" accept=".xlsx,.xls" data-c="importXlsx"></div>`;
    const jahre = [...new Set(S.d.abwesenheiten.map((a) => +a.datum.slice(0, 4)).concat([S.jahr]))].sort();
    let liste = S.d.abwesenheiten.filter((a) => (!S.filterName || a.name === S.filterName) && (!S.filterJahr || +a.datum.slice(0, 4) === S.filterJahr)).sort((a, b) => a.datum.localeCompare(b.datum) || a.name.localeCompare(b.name));
    h += `<div class="card"><h2>Liste</h2><div class="row noprint"><label>Jahr<select data-c="filterJahr"><option value="0">alle</option>${jahre.map((j) => `<option${j === S.filterJahr ? ' selected' : ''}>${j}</option>`).join('')}</select></label>
      <label>Person<select data-c="filterName"><option value="">alle</option>${namenOpt(S.filterName, false)}</select></label></div>
      <p class="small mut">${liste.length} Einträge</p><div class="scroll"><table><tr><th>Datum</th><th>Tag</th><th>KW</th><th>Name</th><th>Art</th><th>Genehmigt</th><th>Notiz</th><th></th></tr>`;
    liste.slice(0, 400).forEach((a) => {
      h += `<tr><td>${L.anzeigeDatum(a.datum)}</td><td>${L.wochentag(a.datum)}</td><td>${L.isoKW(a.datum).kw}</td><td>${esc(a.name)}</td><td><span class="pill a-${esc(a.art)}">${esc(a.art)}</span></td><td>${esc(a.genehmigt)}</td><td>${esc(a.notiz)}</td><td><button class="btn del noprint" data-a="abwLoeschen" data-v="${a.datum}|${esc(a.name)}" aria-label="Löschen">✕</button></td></tr>`;
    });
    return h + `</table></div>${liste.length > 400 ? '<p class="small mut">Nur die ersten 400 Einträge angezeigt – bitte filtern.</p>' : ''}</div>`;
  }

  // ---------- Personal ----------
  function tabPersonal() {
    let h = meldungHtml() + `<div class="card"><h2>Personal</h2><p class="small mut">„Aktiv = nein“ nimmt die Person komplett aus Prüfung und Listen, der Standardplan bleibt erhalten. Resturlaub = Anspruch minus Urlaubstage ${S.jahr} (nur Tage, an denen die Person laut Standardplan arbeitet, ohne Feiertage).</p>
      <div class="scroll"><table><tr><th>Name</th><th>Rolle</th><th>Approbiert</th><th>Rollgruppe</th><th>Aktiv</th><th>Zählt Mindestbesetzung</th><th>Anspruch ${S.jahr} (Tage)</th><th>Genommen</th><th>Rest</th><th>Hinweis</th><th></th></tr>`;
    S.d.personal.forEach((p, i) => {
      const rest = L.resturlaub(p.name, S.jahr, S.d);
      h += `<tr><td>${esc(p.name)}</td><td>${esc(p.rolle)}</td><td>${p.approbiert ? 'ja' : 'nein'}</td><td>${esc(p.rollgruppe)}</td>
        <td><input type="checkbox" data-c="pAktiv" data-i="${i}" ${p.aktiv ? 'checked' : ''} aria-label="Aktiv ${esc(p.name)}"></td>
        <td><input type="checkbox" data-c="pZaehlt" data-i="${i}" ${p.zaehlt ? 'checked' : ''}></td>
        <td><input type="number" min="0" step="0.5" data-c="pAnspruch" data-i="${i}" value="${p.anspruch == null ? '' : p.anspruch}"></td>
        <td>${L.urlaubstage(p.name, S.jahr, S.d)}</td><td>${rest == null ? '–' : rest}</td>
        <td><input data-c="pHinweis" data-i="${i}" value="${esc(p.hinweis)}"></td><td><button class="btn del" data-a="pLoeschen" data-i="${i}">✕</button></td></tr>`;
    });
    h += `</table></div></div><div class="card"><h2>Person hinzufügen</h2><div class="row"><label>Name<input id="np-name"></label>
      <label>Rolle<select id="np-rolle">${opt(Object.keys(ROLLEN), 'PTA')}</select></label><button class="btn" data-a="pNeu">Hinzufügen</button></div>
      <p class="small mut">Danach den Standardplan der Person im Reiter „Standardplan“ anlegen.</p></div>`;
    return h;
  }

  // ---------- Standardplan ----------
  function tabPlan() {
    const p = S.d.personal.find((x) => x.name === S.planPerson) || S.d.personal[0];
    if (!p) return '<div class="card">Keine Personen vorhanden.</div>';
    S.planPerson = p.name;
    const tage = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa'];
    const eintraege = S.d.standardplan.map((e, i) => [e, i]).filter(([e]) => e.name === p.name)
      .sort((a, b) => tage.indexOf(a[0].tag) - tage.indexOf(b[0].tag) || a[0].von.localeCompare(b[0].von));
    let h = meldungHtml() + `<div class="card"><h2>Standardplan W1–W8</h2><div class="row"><label>Person<select data-c="planPerson">${namenOpt(p.name, false)}</select></label>
      <button class="btn" data-a="planNeu">+ Eintrag</button></div>
      <p class="small mut">Ort „Filiale“ zählt zur Mindestbesetzung. „Homeoffice“ und „Labor“ zählen nicht. Ein freier Tag ist einfach kein Eintrag. Rollwochen: Apotheker und PTA werden getrennt gerechnet (siehe Regeln & Rollierung).</p>
      ${eintraege.length === 0 ? '<div class="info">Noch kein Plan hinterlegt.</div>' : ''}
      <div class="scroll"><table><tr><th>Tag</th><th>Von</th><th>Bis</th><th>Ort</th><th>Rollwochen</th><th></th></tr>`;
    eintraege.forEach(([e, i]) => {
      h += `<tr><td><select data-c="eTag" data-i="${i}">${opt(tage, e.tag)}</select></td><td><input type="time" data-c="eVon" data-i="${i}" value="${e.von}"></td><td><input type="time" data-c="eBis" data-i="${i}" value="${e.bis}"></td>
        <td><select data-c="eOrt" data-i="${i}">${opt(['Filiale', 'Homeoffice', 'Labor'], e.ort)}</select></td>
        <td class="wochen">${[1, 2, 3, 4, 5, 6, 7, 8].map((w) => `<label><input type="checkbox" data-c="eWoche" data-i="${i}" data-w="${w}" ${e.wochen.includes(w) ? 'checked' : ''}>W${w}</label>`).join('')}</td>
        <td><button class="btn del" data-a="eLoeschen" data-i="${i}">✕</button></td></tr>`;
    });
    return h + `</table></div></div>`;
  }

  // ---------- Regeln & Rollierung ----------
  function tabRegeln() {
    const R = S.d.rollierung;
    let h = meldungHtml() + `<div class="card"><h2>Rollierung</h2><div class="row"><label>Montag der Rollwoche 1<input type="date" data-c="rStart" value="${R.start}"></label></div>
      <p class="small mut">PTA/PTA-Praktikant/PhiP laufen starr im 8-Wochen-Rhythmus. Bei Apothekern pausiert die Zählung nach jeder Woche mit einem Feiertagssamstag (Folgewoche bekommt dieselbe Rollwoche).</p>
      <h3>Feiertagssamstage (nur Apotheker-Rhythmus)</h3><p>${R.feiertagssamstage.map((s) => `<span class="chip s-Feiertag">${L.anzeigeDatum(s)} <a href="#" data-a="fsDel" data-v="${s}" aria-label="Entfernen">✕</a></span> `).join(' ') || '<span class="mut">keine</span>'}</p>
      <div class="row"><label>Samstag hinzufügen<input type="date" id="fs-neu"></label><button class="btn sec" data-a="fsAdd">Hinzufügen</button></div></div>`;
    h += `<div class="card"><h2>Mindestbesetzung</h2><div class="scroll"><table><tr><th>Tag</th><th>Zeitblock</th><th>Min. Personen</th><th>Min. Approbierte</th><th>Nur Approbierte</th></tr>`;
    S.d.regeln.forEach((r, i) => {
      h += `<tr><td>${r.tag}</td><td>${r.von}–${r.bis}</td><td><input type="number" min="0" data-c="rP" data-i="${i}" value="${r.minP}"></td><td><input type="number" min="0" data-c="rA" data-i="${i}" value="${r.minA}"></td><td><input type="checkbox" data-c="rN" data-i="${i}" ${r.nurAppr ? 'checked' : ''}></td></tr>`;
    });
    h += `</table></div><p class="small mut">Zeitblöcke: Mo–Fr ${S.d.bloecke.filter((b) => b.tagTyp === 'MoFr').map(L.blockLabel).join(', ')} · Sa ${S.d.bloecke.filter((b) => b.tagTyp === 'Sa').map(L.blockLabel).join(', ')}</p></div>`;
    h += `<div class="card"><h2>Feiertage (NRW, an diesen Tagen wird nicht bewertet)</h2><p>${S.d.feiertage.slice().sort((a, b) => a.datum.localeCompare(b.datum)).map((f) => `<span class="chip s-Feiertag">${L.anzeigeDatum(f.datum)} ${esc(f.name)} <a href="#" data-a="feDel" data-v="${f.datum}" aria-label="Entfernen">✕</a></span> `).join(' ')}</p>
      <div class="row"><label>Datum<input type="date" id="fe-d"></label><label>Name<input id="fe-n"></label><button class="btn sec" data-a="feAdd">Hinzufügen</button></div>
      <p class="small mut">Vorbefüllt für 2026–2028; bitte für spätere Jahre ergänzen und die Liste einmal prüfen.</p></div>`;
    return h;
  }

  // ---------- Daten ----------
  function tabDaten() {
    return meldungHtml() + `<div class="card"><h2>Sicherung</h2><div class="row"><button class="btn" data-a="jsonExport">JSON-Sicherung herunterladen</button>
      <label>JSON-Sicherung einlesen<input type="file" accept=".json" data-c="jsonImport"></label></div>
      <p class="small mut">Die Daten liegen nur in diesem Browser. Bitte regelmäßig eine Sicherung speichern.</p></div>
      <div class="card"><h2>Excel-Export</h2><div class="row"><button class="btn" data-a="xlsExport">Excel: Woche ${L.anzeigeDatum(L.montagVon(S.datum))}, Jahresübersicht ${S.jahr}, Abwesenheiten</button><button class="btn sec" data-a="drucken">Drucken / als PDF speichern</button></div></div>
      <div class="card"><h2>Zurücksetzen</h2><button class="btn del" data-a="reset">Alles auf Ausgangsdaten zurücksetzen (löscht Abwesenheiten)</button></div>`;
  }

  // ---------- Rendern & Ereignisse ----------
  function render() {
    document.getElementById('nav').innerHTML = TABS.map(([k, n]) => `<button data-a="tab" data-v="${k}" class="${S.tab === k ? 'on' : ''}">${n}</button>`).join('');
    const fn = { woche: tabWoche, kalender: tabKalender, abw: tabAbw, personal: tabPersonal, plan: tabPlan, regeln: tabRegeln, daten: tabDaten }[S.tab];
    document.getElementById('app').innerHTML = fn();
  }
  function aendern(fn) { fn(); speichern(); render(); }
  function download(name, blob) { const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name; document.body.appendChild(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 500); }

  const A = {
    tab: (v) => { S.tab = v; render(); },
    wocheMinus: () => { S.datum = L.addTage(S.datum, -7); render(); },
    wochePlus: () => { S.datum = L.addTage(S.datum, 7); render(); },
    heute: () => { S.datum = heute(); render(); },
    gotoTag: (v) => { S.datum = v; S.tab = 'woche'; render(); },
    monatMinus: () => { S.monat--; if (S.monat < 1) { S.monat = 12; S.jahr--; } render(); },
    monatPlus: () => { S.monat++; if (S.monat > 12) { S.monat = 1; S.jahr++; } render(); },
    abwSpeichern: () => {
      const f = S.form;
      if (!f.name || !f.von) { S.meldung = ['bad', 'Bitte Person und Startdatum angeben.']; return render(); }
      const bis = f.bis || f.von;
      if (bis < f.von) { S.meldung = ['bad', 'Das Enddatum liegt vor dem Startdatum.']; return render(); }
      const r = L.addAbwesenheiten(S.d, { name: f.name, von: f.von, bis, art: f.art, genehmigt: f.genehmigt, notiz: f.notiz });
      S.meldung = ['ok', `${r.hinzu} Tag(e) eingetragen${r.uebersprungen ? `, ${r.uebersprungen} bereits vorhanden` : ''}.`];
      S.form.von = ''; S.form.bis = ''; S.form.notiz = ''; speichern(); render();
    },
    abwLoeschen: (v) => aendern(() => { const [datum, name] = v.split('|'); S.d.abwesenheiten = S.d.abwesenheiten.filter((a) => !(a.datum === datum && a.name === name)); }),
    pLoeschen: (_, el) => { const p = S.d.personal[+el.dataset.i]; if (confirm(`${p.name} wirklich löschen? Der Standardplan dieser Person wird ebenfalls gelöscht. Tipp: „Aktiv“ abwählen genügt meistens.`)) aendern(() => { S.d.standardplan = S.d.standardplan.filter((e) => e.name !== p.name); S.d.abwesenheiten = S.d.abwesenheiten.filter((a) => a.name !== p.name); S.d.personal.splice(+el.dataset.i, 1); }); },
    pNeu: () => {
      const name = document.getElementById('np-name').value.trim(), rolle = document.getElementById('np-rolle').value;
      if (!name) { S.meldung = ['bad', 'Bitte einen Namen eingeben.']; return render(); }
      if (S.d.personal.some((p) => p.name.toLowerCase() === name.toLowerCase())) { S.meldung = ['bad', 'Diesen Namen gibt es schon.']; return render(); }
      aendern(() => { S.d.personal.push({ name, rolle, approbiert: ROLLEN[rolle][1], rollgruppe: ROLLEN[rolle][0], aktiv: true, zaehlt: true, anspruch: null, hinweis: '' }); S.planPerson = name; S.tab = 'plan'; });
    },
    planNeu: () => aendern(() => { S.d.standardplan.push({ name: S.planPerson, wochen: [1, 2, 3, 4, 5, 6, 7, 8], tag: 'Mo', von: '08:00', bis: '13:00', ort: 'Filiale' }); }),
    eLoeschen: (_, el) => aendern(() => S.d.standardplan.splice(+el.dataset.i, 1)),
    fsAdd: () => {
      const v = document.getElementById('fs-neu').value;
      if (!v) return;
      if (L.wochentag(v) !== 'Sa') { S.meldung = ['bad', 'Das gewählte Datum ist kein Samstag.']; return render(); }
      aendern(() => { if (!S.d.rollierung.feiertagssamstage.includes(v)) S.d.rollierung.feiertagssamstage.push(v); S.d.rollierung.feiertagssamstage.sort(); });
    },
    fsDel: (v) => aendern(() => { S.d.rollierung.feiertagssamstage = S.d.rollierung.feiertagssamstage.filter((x) => x !== v); }),
    feAdd: () => {
      const d = document.getElementById('fe-d').value, n = document.getElementById('fe-n').value.trim();
      if (!d || !n) { S.meldung = ['bad', 'Bitte Datum und Name des Feiertags angeben.']; return render(); }
      aendern(() => { if (!S.d.feiertage.some((f) => f.datum === d)) S.d.feiertage.push({ datum: d, name: n }); });
    },
    feDel: (v) => aendern(() => { S.d.feiertage = S.d.feiertage.filter((f) => f.datum !== v); }),
    jsonExport: () => download('urlaubsplaner-sicherung-' + heute() + '.json', new Blob([JSON.stringify(S.d, null, 1)], { type: 'application/json' })),
    xlsExport: () => {
      const wb = XLSX.utils.book_new();
      [E.exportWochenplan(L.pruefeWoche(S.datum, S.d)), E.exportJahr(L.jahresuebersicht(S.jahr, S.d)), E.exportAbwesenheiten(S.d)]
        .forEach((s) => XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(s.rows), s.name));
      XLSX.writeFile(wb, 'urlaubsplaner-' + heute() + '.xlsx');
    },
    drucken: () => window.print(),
    reset: () => { if (confirm('Wirklich ALLES zurücksetzen? Alle eingetragenen Abwesenheiten und Änderungen gehen verloren.')) aendern(() => { S.d = Daten.seed(); }); },
  };
  const C = {
    datum: (el) => { if (el.value) { S.datum = el.value; render(); } },
    kw: (el) => { const kw = +el.value; if (kw >= 1 && kw <= 53) { const mon = L.montagVon(S.datum), cur = L.isoKW(mon); S.datum = L.addTage(mon, (kw - cur.kw) * 7); render(); } },
    jahr: (el) => { if (+el.value >= 2020) { S.jahr = +el.value; render(); } },
    filterJahr: (el) => { S.filterJahr = +el.value; render(); }, filterName: (el) => { S.filterName = el.value; render(); },
    planPerson: (el) => { S.planPerson = el.value; render(); },
    pAktiv: (el) => aendern(() => { S.d.personal[+el.dataset.i].aktiv = el.checked; }),
    pZaehlt: (el) => aendern(() => { S.d.personal[+el.dataset.i].zaehlt = el.checked; }),
    pAnspruch: (el) => aendern(() => { S.d.personal[+el.dataset.i].anspruch = el.value === '' ? null : Math.max(0, +el.value); }),
    pHinweis: (el) => { S.d.personal[+el.dataset.i].hinweis = el.value; speichern(); },
    eTag: (el) => aendern(() => { S.d.standardplan[+el.dataset.i].tag = el.value; }),
    eVon: (el) => aendern(() => { if (el.value) S.d.standardplan[+el.dataset.i].von = el.value; }),
    eBis: (el) => aendern(() => { if (el.value) S.d.standardplan[+el.dataset.i].bis = el.value; }),
    eOrt: (el) => aendern(() => { S.d.standardplan[+el.dataset.i].ort = el.value; }),
    eWoche: (el) => aendern(() => { const e = S.d.standardplan[+el.dataset.i], w = +el.dataset.w; e.wochen = el.checked ? [...new Set(e.wochen.concat(w))].sort() : e.wochen.filter((x) => x !== w); }),
    rStart: (el) => { if (!el.value) return; if (L.wochentag(el.value) !== 'Mo') { S.meldung = ['bad', 'Der Rollierungsstart muss ein Montag sein.']; return render(); } aendern(() => { S.d.rollierung.start = el.value; }); },
    rP: (el) => aendern(() => { S.d.regeln[+el.dataset.i].minP = Math.max(0, +el.value || 0); }),
    rA: (el) => aendern(() => { S.d.regeln[+el.dataset.i].minA = Math.max(0, +el.value || 0); }),
    rN: (el) => aendern(() => { S.d.regeln[+el.dataset.i].nurAppr = el.checked; }),
    jsonImport: (el) => {
      const f = el.files[0]; if (!f) return;
      f.text().then((t) => {
        try { const j = JSON.parse(t); if (!gueltig(j)) throw new Error('Struktur'); aendern(() => { S.d = j; S.meldung = ['ok', 'Sicherung eingelesen.']; }); }
        catch (e) { S.meldung = ['bad', 'Die Datei ist keine gültige Urlaubsplaner-Sicherung. Es wurde nichts verändert.']; render(); }
      });
    },
    importXlsx: (el) => {
      const f = el.files[0]; if (!f) return;
      f.arrayBuffer().then((buf) => {
        try {
          const wb = XLSX.read(buf, { cellDates: true });
          const ws = wb.Sheets['Abwesenheiten'];
          if (!ws) throw new Error('Blatt „Abwesenheiten“ nicht gefunden');
          const r = E.parseAbwesenheiten(XLSX.utils.sheet_to_json(ws, { header: 1, raw: true }), S.d);
          const vorhanden = new Set(S.d.abwesenheiten.map((a) => a.datum + '|' + a.name));
          let neu = 0;
          r.eintraege.forEach((e) => { if (!vorhanden.has(e.datum + '|' + e.name)) { S.d.abwesenheiten.push(e); neu++; } });
          S.meldung = [r.unbekannteNamen.length ? 'bad' : 'ok', `${neu} Abwesenheiten importiert, ${r.eintraege.length - neu} schon vorhanden.${r.unbekannteNamen.length ? ' Nicht übernommen (Name unbekannt): ' + r.unbekannteNamen.join(', ') + '.' : ''}`];
          speichern(); render();
        } catch (e) { S.meldung = ['bad', 'Import nicht möglich: ' + e.message]; render(); }
      });
    },
  };
  document.addEventListener('click', (ev) => {
    const el = ev.target.closest('[data-a]'); if (!el) return;
    if (el.tagName === 'A') ev.preventDefault();
    const fn = A[el.dataset.a]; if (fn) fn(el.dataset.v, el);
  });
  document.addEventListener('change', (ev) => {
    const el = ev.target;
    if (el.dataset.f) { S.form[el.dataset.f] = el.value; if (el.dataset.f === 'von' && (!S.form.bis || S.form.bis < el.value)) S.form.bis = el.value; return render(); }
    if (el.dataset.c && C[el.dataset.c]) C[el.dataset.c](el);
  });
  window.__urlaubsplaner = S; // für Tests
  render();
})();
