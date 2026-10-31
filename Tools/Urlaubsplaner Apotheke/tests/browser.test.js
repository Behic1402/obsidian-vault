// Browser-Smoketest (Playwright, vorinstalliert): node tests/browser.test.js
const { chromium } = require('playwright');
const path = require('path'), assert = require('node:assert/strict'), fs = require('fs');
(async () => {
  const url = 'file://' + path.join(__dirname, '..', 'urlaubsplaner.html');
  const b = await chromium.launch(); const ctx = await b.newContext({ acceptDownloads: true }); const p = await ctx.newPage();
  const fehler = [], fremd = [];
  p.on('console', (m) => m.type() === 'error' && fehler.push(m.text()));
  p.on('pageerror', (e) => fehler.push(String(e)));
  p.on('request', (r) => { if (!r.url().startsWith('file:') && !r.url().startsWith('data:') && !r.url().startsWith('blob:')) fremd.push(r.url()); });
  await p.goto(url);
  // Start: Rollierungsbeginn, Wochenprüfung
  assert.match(await p.textContent('h2 >> nth=0'), /KW 53\/2026/);
  await p.fill('input[data-c=datum]', '2027-01-04'); await p.dispatchEvent('input[data-c=datum]', 'change');
  assert.match(await p.textContent('#app'), /PTA: W2/);
  assert.equal(await p.locator('.card table tr').count() > 30, true);
  // Abwesenheit mit Warnung: Tomke + Katja Montag
  await p.click('nav button:has-text("Abwesenheiten")');
  await p.selectOption('select[data-f=name]', 'Katja');
  await p.fill('input[data-f=von]', '2027-01-04'); await p.dispatchEvent('input[data-f=von]', 'change');
  assert.match(await p.textContent('#app'), /Keine zusätzliche Unterbesetzung|führt zu Unterbesetzung/);
  await p.click('button[data-a=abwSpeichern]');
  assert.match(await p.textContent('#app'), /1 Tag\(e\) eingetragen/);
  await p.selectOption('select[data-f=name]', 'Tomke');
  await p.fill('input[data-f=von]', '2027-01-04'); await p.dispatchEvent('input[data-f=von]', 'change');
  assert.match(await p.textContent('.warnbox'), /Unterbesetzung/);
  await p.click('button[data-a=abwSpeichern]');
  // Wochenprüfung zeigt Montag kritisch
  await p.click('nav button:has-text("Wochenprüfung")');
  assert.match(await p.textContent('#app'), /Kein Apotheker/);
  // Nick deaktivieren
  await p.click('nav button:has-text("Personal")');
  await p.locator('input[data-c=pAktiv][data-i="9"]').uncheck();
  await p.click('nav button:has-text("Wochenprüfung")');
  assert.ok(!(await p.textContent('#app')).includes('Nick'));
  // Reload behält Daten
  await p.reload(); await p.click('nav button:has-text("Abwesenheiten")');
  assert.match(await p.textContent('#app'), /04\.01\.2027/);
  // Kalender
  await p.click('nav button:has-text("Kalender")');
  assert.ok(await p.locator('.kal .z').count() >= 28);
  // JSON Roundtrip
  await p.click('nav button:has-text("Daten")');
  const [dl] = await Promise.all([p.waitForEvent('download'), p.click('button[data-a=jsonExport]')]);
  const f = await dl.path(); const json = fs.readFileSync(f, 'utf8');
  const vorher = await p.evaluate(() => JSON.stringify(window.__urlaubsplaner.d));
  assert.deepEqual(JSON.parse(json), JSON.parse(vorher));
  await p.setInputFiles('input[data-c=jsonImport]', f);
  await p.waitForSelector('.okbox');
  fs.writeFileSync('/tmp/kaputt.json', '{"x":1}');
  await p.setInputFiles('input[data-c=jsonImport]', '/tmp/kaputt.json');
  await p.waitForSelector('.warnbox');
  assert.equal(await p.evaluate(() => JSON.stringify(window.__urlaubsplaner.d)), vorher);
  // Excel-Export
  const [dx] = await Promise.all([p.waitForEvent('download'), p.click('button[data-a=xlsExport]')]);
  assert.ok(fs.statSync(await dx.path()).size > 4000);
  await p.screenshot({ path: '/tmp/daten.png' });
  await p.click('nav button:has-text("Wochenprüfung")'); await p.screenshot({ path: '/tmp/woche.png', fullPage: true });
  assert.deepEqual(fehler, []); assert.deepEqual(fremd, []);
  await b.close(); console.log('Browser-Test OK');
})().catch((e) => { console.error(e); process.exit(1); });
