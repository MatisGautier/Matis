// Génère les consignes patient du SOT : 1 PDF par langue (3 pages A4, 2 conditions par page)
// Usage : node generate.js
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const os = require('os');

const FONT_DIR = path.join(os.homedir(), '.fonts');
const font = (pkg, file) => 'file://' + path.join(FONT_DIR, pkg, 'package/files', file);

// État de chaque condition : yeux (open/closed), support et décor (fixed/moves)
const CONDITIONS = [
  { eyes: 'open',   support: 'fixed', surround: 'fixed' },
  { eyes: 'closed', support: 'fixed', surround: 'fixed' },
  { eyes: 'open',   support: 'fixed', surround: 'moves' },
  { eyes: 'open',   support: 'moves', surround: 'fixed' },
  { eyes: 'closed', support: 'moves', surround: 'fixed' },
  { eyes: 'open',   support: 'moves', surround: 'moves' },
];

const LANGS = {
  fr: {
    name: 'Français', title: "Test d'organisation sensorielle (SOT)", sub: 'Consignes patient',
    cond: 'Condition', eyes: 'Yeux', support: 'Support', surround: 'Décor',
    open: 'Ouverts', closed: 'Fermés',
    fixedS: 'Fixe', movesS: 'Peut bouger', fixedD: 'Fixe', movesD: 'Peut bouger',
    footer: 'Durée : 20 secondes · Vous êtes attaché(e) par un harnais : vous ne pouvez pas tomber.',
    text: [
      "Gardez les yeux ouverts et regardez droit devant vous. Le décor autour de vous ne bouge pas, et le support sous vos pieds non plus. Restez le plus droit et le plus immobile possible, les bras le long du corps.",
      "Fermez les yeux et gardez-les fermés jusqu'à la fin de l'essai. Le support sous vos pieds ne bouge pas. Restez le plus droit et le plus immobile possible.",
      "Gardez les yeux ouverts et regardez droit devant vous. Le décor autour de vous peut bouger légèrement : c'est normal. Le support sous vos pieds ne bouge pas. Restez le plus droit possible, sans bouger les pieds.",
      "Gardez les yeux ouverts et regardez droit devant vous. Le décor ne bouge pas, mais le support sous vos pieds peut bouger légèrement. Restez le plus droit possible, sans bouger les pieds.",
      "Fermez les yeux et gardez-les fermés jusqu'à la fin de l'essai. Le support sous vos pieds peut bouger légèrement. Restez le plus droit possible, sans bouger les pieds.",
      "Gardez les yeux ouverts et regardez droit devant vous. Le décor autour de vous et le support sous vos pieds peuvent bouger légèrement. Restez le plus droit possible, sans bouger les pieds.",
    ],
  },
  en: {
    name: 'English', title: 'Sensory Organization Test (SOT)', sub: 'Patient instructions',
    cond: 'Condition', eyes: 'Eyes', support: 'Platform', surround: 'Surroundings',
    open: 'Open', closed: 'Closed',
    fixedS: 'Fixed', movesS: 'May move', fixedD: 'Fixed', movesD: 'May move',
    footer: 'Duration: 20 seconds · You are wearing a safety harness: you cannot fall.',
    text: [
      "Keep your eyes open and look straight ahead. The surroundings do not move, and neither does the platform under your feet. Stand as straight and as still as possible, arms by your sides.",
      "Close your eyes and keep them closed until the end of the trial. The platform under your feet does not move. Stand as straight and as still as possible.",
      "Keep your eyes open and look straight ahead. The surroundings may move slightly: this is normal. The platform under your feet does not move. Stand as straight as possible without moving your feet.",
      "Keep your eyes open and look straight ahead. The surroundings do not move, but the platform under your feet may move slightly. Stand as straight as possible without moving your feet.",
      "Close your eyes and keep them closed until the end of the trial. The platform under your feet may move slightly. Stand as straight as possible without moving your feet.",
      "Keep your eyes open and look straight ahead. Both the surroundings and the platform under your feet may move slightly. Stand as straight as possible without moving your feet.",
    ],
  },
  de: {
    name: 'Deutsch', title: 'Sensorischer Organisationstest (SOT)', sub: 'Hinweise für Patienten',
    cond: 'Bedingung', eyes: 'Augen', support: 'Plattform', surround: 'Umgebung',
    open: 'Offen', closed: 'Geschlossen',
    fixedS: 'Unbewegt', movesS: 'Kann sich bewegen', fixedD: 'Unbewegt', movesD: 'Kann sich bewegen',
    footer: 'Dauer: 20 Sekunden · Sie sind durch einen Sicherheitsgurt gesichert: Sie können nicht fallen.',
    text: [
      "Halten Sie die Augen offen und blicken Sie geradeaus. Die Umgebung bewegt sich nicht, und die Plattform unter Ihren Füßen auch nicht. Stehen Sie so aufrecht und ruhig wie möglich, die Arme locker am Körper.",
      "Schließen Sie die Augen und lassen Sie sie bis zum Ende der Messung geschlossen. Die Plattform unter Ihren Füßen bewegt sich nicht. Stehen Sie so aufrecht und ruhig wie möglich.",
      "Halten Sie die Augen offen und blicken Sie geradeaus. Die Umgebung kann sich leicht bewegen – das ist normal. Die Plattform unter Ihren Füßen bewegt sich nicht. Stehen Sie so aufrecht wie möglich, ohne die Füße zu bewegen.",
      "Halten Sie die Augen offen und blicken Sie geradeaus. Die Umgebung bewegt sich nicht, aber die Plattform unter Ihren Füßen kann sich leicht bewegen. Stehen Sie so aufrecht wie möglich, ohne die Füße zu bewegen.",
      "Schließen Sie die Augen und lassen Sie sie bis zum Ende der Messung geschlossen. Die Plattform unter Ihren Füßen kann sich leicht bewegen. Stehen Sie so aufrecht wie möglich, ohne die Füße zu bewegen.",
      "Halten Sie die Augen offen und blicken Sie geradeaus. Sowohl die Umgebung als auch die Plattform unter Ihren Füßen können sich leicht bewegen. Stehen Sie so aufrecht wie möglich, ohne die Füße zu bewegen.",
    ],
  },
  es: {
    name: 'Español', title: 'Prueba de organización sensorial (SOT)', sub: 'Instrucciones para el paciente',
    cond: 'Condición', eyes: 'Ojos', support: 'Plataforma', surround: 'Entorno',
    open: 'Abiertos', closed: 'Cerrados',
    fixedS: 'Inmóvil', movesS: 'Puede moverse', fixedD: 'Inmóvil', movesD: 'Puede moverse',
    footer: 'Duración: 20 segundos · Lleva un arnés de seguridad: no puede caerse.',
    text: [
      "Mantenga los ojos abiertos y mire al frente. El entorno no se mueve, y la plataforma bajo sus pies tampoco. Mantenga el cuerpo lo más recto e inmóvil posible, con los brazos a lo largo del cuerpo.",
      "Cierre los ojos y manténgalos cerrados hasta el final de la prueba. La plataforma bajo sus pies no se mueve. Mantenga el cuerpo lo más recto e inmóvil posible.",
      "Mantenga los ojos abiertos y mire al frente. El entorno puede moverse ligeramente: es normal. La plataforma bajo sus pies no se mueve. Mantenga el cuerpo lo más recto posible, sin mover los pies.",
      "Mantenga los ojos abiertos y mire al frente. El entorno no se mueve, pero la plataforma bajo sus pies puede moverse ligeramente. Mantenga el cuerpo lo más recto posible, sin mover los pies.",
      "Cierre los ojos y manténgalos cerrados hasta el final de la prueba. La plataforma bajo sus pies puede moverse ligeramente. Mantenga el cuerpo lo más recto posible, sin mover los pies.",
      "Mantenga los ojos abiertos y mire al frente. Tanto el entorno como la plataforma bajo sus pies pueden moverse ligeramente. Mantenga el cuerpo lo más recto posible, sin mover los pies.",
    ],
  },
  pt: {
    name: 'Português', title: 'Teste de organização sensorial (SOT)', sub: 'Instruções para o paciente',
    cond: 'Condição', eyes: 'Olhos', support: 'Plataforma', surround: 'Ambiente',
    open: 'Abertos', closed: 'Fechados',
    fixedS: 'Imóvel', movesS: 'Pode mexer-se', fixedD: 'Imóvel', movesD: 'Pode mexer-se',
    footer: 'Duração: 20 segundos · Está preso(a) por um arnês de segurança: não pode cair.',
    text: [
      "Mantenha os olhos abertos e olhe em frente. O ambiente à sua volta não se mexe, nem a plataforma sob os seus pés. Mantenha o corpo o mais direito e imóvel possível, com os braços ao longo do corpo.",
      "Feche os olhos e mantenha-os fechados até ao fim do teste. A plataforma sob os seus pés não se mexe. Mantenha o corpo o mais direito e imóvel possível.",
      "Mantenha os olhos abertos e olhe em frente. O ambiente à sua volta pode mexer-se ligeiramente: é normal. A plataforma sob os seus pés não se mexe. Mantenha o corpo o mais direito possível, sem mexer os pés.",
      "Mantenha os olhos abertos e olhe em frente. O ambiente não se mexe, mas a plataforma sob os seus pés pode mexer-se ligeiramente. Mantenha o corpo o mais direito possível, sem mexer os pés.",
      "Feche os olhos e mantenha-os fechados até ao fim do teste. A plataforma sob os seus pés pode mexer-se ligeiramente. Mantenha o corpo o mais direito possível, sem mexer os pés.",
      "Mantenha os olhos abertos e olhe em frente. Tanto o ambiente à sua volta como a plataforma sob os seus pés podem mexer-se ligeiramente. Mantenha o corpo o mais direito possível, sem mexer os pés.",
    ],
  },
  ar: {
    name: 'العربية', dir: 'rtl', title: 'اختبار التنظيم الحسي (SOT)', sub: 'تعليمات للمريض',
    cond: 'الحالة', eyes: 'العينان', support: 'المنصة', surround: 'المحيط',
    open: 'مفتوحتان', closed: 'مغمضتان',
    fixedS: 'ثابتة', movesS: 'قد تتحرك', fixedD: 'ثابت', movesD: 'قد يتحرك',
    footer: 'المدة: 20 ثانية · أنت مثبَّت بحزام أمان: لا يمكنك السقوط.',
    text: [
      "أبقِ عينيك مفتوحتين وانظر إلى الأمام مباشرة. المحيط من حولك لا يتحرك، وكذلك المنصة تحت قدميك. حافظ على جسمك مستقيمًا وثابتًا قدر الإمكان، مع إبقاء ذراعيك بجانب جسمك.",
      "أغمض عينيك وأبقهما مغمضتين حتى نهاية الاختبار. المنصة تحت قدميك لا تتحرك. حافظ على جسمك مستقيمًا وثابتًا قدر الإمكان.",
      "أبقِ عينيك مفتوحتين وانظر إلى الأمام مباشرة. قد يتحرك المحيط من حولك قليلًا، وهذا أمر طبيعي. المنصة تحت قدميك لا تتحرك. حافظ على جسمك مستقيمًا قدر الإمكان دون تحريك قدميك.",
      "أبقِ عينيك مفتوحتين وانظر إلى الأمام مباشرة. المحيط من حولك لا يتحرك، لكن المنصة تحت قدميك قد تتحرك قليلًا. حافظ على جسمك مستقيمًا قدر الإمكان دون تحريك قدميك.",
      "أغمض عينيك وأبقهما مغمضتين حتى نهاية الاختبار. قد تتحرك المنصة تحت قدميك قليلًا. حافظ على جسمك مستقيمًا قدر الإمكان دون تحريك قدميك.",
      "أبقِ عينيك مفتوحتين وانظر إلى الأمام مباشرة. قد يتحرك المحيط من حولك والمنصة تحت قدميك قليلًا. حافظ على جسمك مستقيمًا قدر الإمكان دون تحريك قدميك.",
    ],
  },
  it: {
    name: 'Italiano', title: 'Test di organizzazione sensoriale (SOT)', sub: 'Istruzioni per il paziente',
    cond: 'Condizione', eyes: 'Occhi', support: 'Pedana', surround: 'Ambiente',
    open: 'Aperti', closed: 'Chiusi',
    fixedS: 'Immobile', movesS: 'Può muoversi', fixedD: 'Immobile', movesD: 'Può muoversi',
    footer: "Durata: 20 secondi · Indossa un'imbracatura di sicurezza: non può cadere.",
    text: [
      "Tenga gli occhi aperti e guardi dritto davanti a sé. L'ambiente intorno a lei non si muove, e nemmeno la pedana sotto i suoi piedi. Mantenga il corpo il più dritto e fermo possibile, con le braccia lungo i fianchi.",
      "Chiuda gli occhi e li tenga chiusi fino alla fine della prova. La pedana sotto i suoi piedi non si muove. Mantenga il corpo il più dritto e fermo possibile.",
      "Tenga gli occhi aperti e guardi dritto davanti a sé. L'ambiente intorno a lei può muoversi leggermente: è normale. La pedana sotto i suoi piedi non si muove. Mantenga il corpo il più dritto possibile, senza muovere i piedi.",
      "Tenga gli occhi aperti e guardi dritto davanti a sé. L'ambiente non si muove, ma la pedana sotto i suoi piedi può muoversi leggermente. Mantenga il corpo il più dritto possibile, senza muovere i piedi.",
      "Chiuda gli occhi e li tenga chiusi fino alla fine della prova. La pedana sotto i suoi piedi può muoversi leggermente. Mantenga il corpo il più dritto possibile, senza muovere i piedi.",
      "Tenga gli occhi aperti e guardi dritto davanti a sé. Sia l'ambiente intorno a lei sia la pedana sotto i suoi piedi possono muoversi leggermente. Mantenga il corpo il più dritto possibile, senza muovere i piedi.",
    ],
  },
};

// Pictogrammes (SVG, trait en currentColor)
const WAVES = '<path d="M6 8 q3 -4 6 0 M40 8 q3 -4 6 0" stroke-width="2.5" fill="none"/>';
const ICONS = {
  open: '<svg viewBox="0 0 52 40"><path d="M4 20 Q26 -2 48 20 Q26 42 4 20 Z" fill="none" stroke-width="3"/><circle cx="26" cy="20" r="7" fill="currentColor"/></svg>',
  closed: '<svg viewBox="0 0 52 40"><path d="M4 16 Q26 34 48 16" fill="none" stroke-width="3"/><path d="M12 24 l-4 6 M20 28 l-2 7 M32 28 l2 7 M40 24 l4 6" stroke-width="3"/></svg>',
  support_fixed: '<svg viewBox="0 0 52 40"><rect x="6" y="24" width="40" height="8" rx="2" fill="currentColor"/><path d="M19 22 v-12 M33 22 v-12" stroke-width="4" stroke-linecap="round"/></svg>',
  support_moves: '<svg viewBox="0 0 52 40"><g transform="rotate(-8 26 28)"><rect x="6" y="24" width="40" height="8" rx="2" fill="currentColor"/><path d="M19 22 v-12 M33 22 v-12" stroke-width="4" stroke-linecap="round"/></g><path d="M2 38 q4 -4 8 0 M42 38 q4 -4 8 0" stroke-width="2.5" fill="none"/></svg>',
  surround_fixed: '<svg viewBox="0 0 52 40"><path d="M8 34 V10 L26 4 L44 10 V34" fill="none" stroke-width="3" stroke-linejoin="round"/><path d="M8 34 H44" stroke-width="3"/><rect x="20" y="16" width="12" height="10" fill="none" stroke-width="2.5"/></svg>',
  surround_moves: '<svg viewBox="0 0 52 40"><g transform="rotate(6 26 20)"><path d="M8 34 V10 L26 4 L44 10 V34" fill="none" stroke-width="3" stroke-linejoin="round"/><path d="M8 34 H44" stroke-width="3"/><rect x="20" y="16" width="12" height="10" fill="none" stroke-width="2.5"/></g><g transform="translate(0 28)">' + WAVES + '</g></svg>',
};

const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');

function half(L, i) {
  const c = CONDITIONS[i];
  const badge = (label, icon, value, state) =>
    `<div class="badge ${state}"><div class="ico">${ICONS[icon]}</div><div class="lbl">${esc(label)}</div><div class="val">${esc(value)}</div></div>`;
  return `
  <section class="half">
    <header><span>${esc(L.title)}</span><span>${esc(L.sub)}</span></header>
    <h1><span class="num">${i + 1}</span>${esc(L.cond)} ${i + 1}</h1>
    <div class="badges">
      ${badge(L.eyes, c.eyes, c.eyes === 'open' ? L.open : L.closed, c.eyes === 'open' ? 'ok' : 'closed')}
      ${badge(L.support, 'support_' + c.support, c.support === 'fixed' ? L.fixedS : L.movesS, c.support === 'fixed' ? 'ok' : 'move')}
      ${badge(L.surround, 'surround_' + c.surround, c.surround === 'fixed' ? L.fixedD : L.movesD, c.surround === 'fixed' ? 'ok' : 'move')}
    </div>
    <p class="txt">${esc(L.text[i])}</p>
    <footer>${esc(L.footer)}</footer>
  </section>`;
}

function html(code) {
  const L = LANGS[code];
  const pages = [0, 2, 4].map((i) => `<div class="page">${half(L, i)}<div class="cut"></div>${half(L, i + 1)}</div>`).join('');
  return `<!doctype html><html lang="${code}" dir="${L.dir || 'ltr'}"><head><meta charset="utf-8"><style>
@font-face{font-family:NS;font-weight:400;src:url(${font('noto-sans', 'noto-sans-latin-400-normal.woff2')})}
@font-face{font-family:NS;font-weight:700;src:url(${font('noto-sans', 'noto-sans-latin-700-normal.woff2')})}
@font-face{font-family:NS;font-weight:400;unicode-range:U+0100-024F,U+1E00-1EFF;src:url(${font('noto-sans', 'noto-sans-latin-ext-400-normal.woff2')})}
@font-face{font-family:NSA;font-weight:400;src:url(${font('noto-sans-arabic', 'noto-sans-arabic-arabic-400-normal.woff2')})}
@font-face{font-family:NSA;font-weight:700;src:url(${font('noto-sans-arabic', 'noto-sans-arabic-arabic-700-normal.woff2')})}
@page{size:A4;margin:0}
*{box-sizing:border-box;margin:0}
body{font-family:NS,NSA,sans-serif;color:#1d2a33}
.page{width:210mm;height:297mm;display:flex;flex-direction:column;page-break-after:always;overflow:hidden}
.half{height:148.5mm;padding:11mm 16mm 9mm;display:flex;flex-direction:column}
.cut{height:0;border-top:1.5px dashed #9aa7b0;margin:0 8mm}
header{display:flex;justify-content:space-between;font-size:9.5pt;color:#5b6b76;border-bottom:1px solid #d6dde2;padding-bottom:2.5mm}
h1{font-size:26pt;font-weight:700;margin:6mm 0 5mm;display:flex;align-items:center;gap:4mm;color:#123a52}
.num{display:inline-flex;align-items:center;justify-content:center;width:13mm;height:13mm;border-radius:50%;background:#123a52;color:#fff;font-size:22pt}
.badges{display:flex;gap:5mm;margin-bottom:6mm}
.badge{flex:1;border-radius:3mm;padding:3mm 2mm;text-align:center;border:2px solid}
.badge .ico svg{width:15mm;height:11.5mm;stroke:currentColor;stroke-linecap:round}
.badge .lbl{font-size:10pt;color:#5b6b76;margin-top:1mm}
.badge .val{font-size:13pt;font-weight:700}
.ok{border-color:#2e8b6e;background:#eaf6f1;color:#1f6b53}
.closed{border-color:#3b5b9a;background:#ecf0f8;color:#2d4a85}
.move{border-color:#d9822b;background:#fdf1e4;color:#a85d14}
.badge .lbl{color:inherit;opacity:.8}
.txt{font-size:15pt;line-height:1.5;flex:1}
footer{font-size:10pt;color:#5b6b76;border-top:1px solid #d6dde2;padding-top:2.5mm}
[dir=rtl] .txt{font-size:16pt;line-height:1.7}
</style></head><body>${pages}</body></html>`;
}

(async () => {
  const outDir = __dirname;
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const code of Object.keys(LANGS)) {
    await page.setContent(html(code), { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    const file = path.join(outDir, `SOT_consignes_${code}.pdf`);
    await page.pdf({ path: file, format: 'A4', printBackground: true, preferCSSPageSize: true });
    console.log('écrit', file);
  }
  await browser.close();
})();
