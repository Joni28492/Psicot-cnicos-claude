// uso: node pdf.js origen.html destino.pdf "texto del pie"
const { chromium } = require('playwright');
(async () => {
  const [, , src, out, pie] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + src);
  await p.pdf({
    path: out, format: 'A4', printBackground: true,
    margin: { top: '13mm', bottom: '16mm', left: '14mm', right: '14mm' },
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: `<div style="font:8px Arial,sans-serif;width:100%;text-align:center;color:#555">${pie} · pág. <span class="pageNumber"></span>/<span class="totalPages"></span></div>`,
  });
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
