// Fügt alle Quellen zu einer einzigen, offline lauffähigen HTML-Datei zusammen.
const fs = require('fs'), path = require('path');
const r = (p) => fs.readFileSync(path.join(__dirname, p), 'utf8').replace(/<\/script/gi, '<\\/script');
let html = fs.readFileSync(path.join(__dirname, 'src/index.template.html'), 'utf8');
const teile = { STYLE: r('src/style.css'), XLSX: r('vendor/xlsx.full.min.js'), LOGIK: r('src/logik.js'), DATEN: r('src/daten.js'), EXCEL: r('src/excel.js'), APP: r('src/app.js') };
Object.entries(teile).forEach(([k, v]) => { html = html.split('/*' + k + '*/').join('\u0000' + k + '\u0000'); });
Object.entries(teile).forEach(([k, v]) => { html = html.split('\u0000' + k + '\u0000').join(v); });
fs.writeFileSync(path.join(__dirname, 'urlaubsplaner.html'), html);
console.log('urlaubsplaner.html', (html.length / 1024).toFixed(0) + ' KB');
