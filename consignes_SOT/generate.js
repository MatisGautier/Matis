// Génère les consignes patient du SOT : 1 PDF par langue (3 pages A4, 2 conditions par page)
// Usage : node generate.js
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { execFileSync } = require('child_process');

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

// Phrases courtes pour la version illustrée (patients sourds) + sous-titres des versions adaptées
const SIMPLE = {
  fr: { sourds: 'Consignes illustrées', malvoyants: 'Gros caractères',
    eyesOpen: 'Yeux ouverts : regardez devant vous', eyesClosed: "Yeux fermés jusqu'à la fin",
    floorFixed: 'Le sol ne bouge pas', floorMoves: 'Le sol peut bouger',
    wallFixed: 'Le décor ne bouge pas', wallMoves: 'Le décor peut bouger',
    stand: 'Restez droit, les pieds immobiles', signal: "Tape sur l'épaule = début et fin",
    time: '20 secondes', safe: 'Harnais : vous ne pouvez pas tomber' },
  en: { sourds: 'Illustrated instructions', malvoyants: 'Large print',
    eyesOpen: 'Eyes open: look straight ahead', eyesClosed: 'Eyes closed until the end',
    floorFixed: 'The floor does not move', floorMoves: 'The floor may move',
    wallFixed: 'The surroundings do not move', wallMoves: 'The surroundings may move',
    stand: 'Stand straight, feet still', signal: 'Tap on the shoulder = start and end',
    time: '20 seconds', safe: 'Harness: you cannot fall' },
  de: { sourds: 'Bebilderte Hinweise', malvoyants: 'Großdruck',
    eyesOpen: 'Augen offen: geradeaus schauen', eyesClosed: 'Augen zu bis zum Ende',
    floorFixed: 'Der Boden bewegt sich nicht', floorMoves: 'Der Boden kann sich bewegen',
    wallFixed: 'Die Umgebung bewegt sich nicht', wallMoves: 'Die Umgebung kann sich bewegen',
    stand: 'Aufrecht stehen, Füße still', signal: 'Tippen auf die Schulter = Start und Ende',
    time: '20 Sekunden', safe: 'Sicherheitsgurt: Sie können nicht fallen' },
  es: { sourds: 'Instrucciones ilustradas', malvoyants: 'Letra grande',
    eyesOpen: 'Ojos abiertos: mire al frente', eyesClosed: 'Ojos cerrados hasta el final',
    floorFixed: 'El suelo no se mueve', floorMoves: 'El suelo puede moverse',
    wallFixed: 'El entorno no se mueve', wallMoves: 'El entorno puede moverse',
    stand: 'Cuerpo recto, pies quietos', signal: 'Toque en el hombro = inicio y fin',
    time: '20 segundos', safe: 'Arnés: no puede caerse' },
  pt: { sourds: 'Instruções ilustradas', malvoyants: 'Letra grande',
    eyesOpen: 'Olhos abertos: olhe em frente', eyesClosed: 'Olhos fechados até ao fim',
    floorFixed: 'O chão não se mexe', floorMoves: 'O chão pode mexer-se',
    wallFixed: 'O ambiente não se mexe', wallMoves: 'O ambiente pode mexer-se',
    stand: 'Corpo direito, pés quietos', signal: 'Toque no ombro = início e fim',
    time: '20 segundos', safe: 'Arnês: não pode cair' },
  ar: { sourds: 'تعليمات مصوَّرة', malvoyants: 'خط كبير',
    eyesOpen: 'العينان مفتوحتان: انظر إلى الأمام', eyesClosed: 'العينان مغمضتان حتى النهاية',
    floorFixed: 'الأرض لا تتحرك', floorMoves: 'قد تتحرك الأرض',
    wallFixed: 'المحيط لا يتحرك', wallMoves: 'قد يتحرك المحيط',
    stand: 'قف مستقيمًا، والقدمان ثابتتان', signal: 'لمسة على الكتف = البداية والنهاية',
    time: '20 ثانية', safe: 'حزام أمان: لا يمكنك السقوط' },
  it: { sourds: 'Istruzioni illustrate', malvoyants: 'Caratteri grandi',
    eyesOpen: 'Occhi aperti: guardi davanti a sé', eyesClosed: 'Occhi chiusi fino alla fine',
    floorFixed: 'Il pavimento non si muove', floorMoves: 'Il pavimento può muoversi',
    wallFixed: "L'ambiente non si muove", wallMoves: "L'ambiente può muoversi",
    stand: 'Corpo dritto, piedi fermi', signal: 'Tocco sulla spalla = inizio e fine',
    time: '20 secondi', safe: 'Imbracatura: non può cadere' },
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


// Version illustrée (patients sourds) : dessin de la cabine + phrases courtes
const COLOR = { fixed: ['#2e8b6e', '#eaf6f1'], moves: ['#d9822b', '#fdf1e4'] };
const INK = '#123a52';

function scene(c, id) {
  const [wall, wallBg] = COLOR[c.surround];
  const [floor] = COLOR[c.support];
  const marker = (name, color) =>
    `<marker id="${name}${id}" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="${color}"/></marker>`;
  const arc = (d, color, name) =>
    `<path d="${d}" fill="none" stroke="${color}" stroke-width="5" stroke-linecap="round" marker-start="url(#${name}${id})" marker-end="url(#${name}${id})"/>`;
  const eyes = c.eyes === 'open'
    ? `<circle cx="91" cy="60" r="4.5" fill="${INK}"/><circle cx="109" cy="60" r="4.5" fill="${INK}"/>`
    : `<path d="M84 59 q7 7 14 0 M102 59 q7 7 14 0" fill="none" stroke="${INK}" stroke-width="3.5" stroke-linecap="round"/>`;
  return `<svg viewBox="0 -14 200 262" role="img">
    <defs>${marker('w', wall)}${marker('f', floor)}</defs>
    <g transform="${c.surround === 'moves' ? 'rotate(-4 100 110)' : ''}">
      <path d="M30 200 V32 Q30 18 44 18 H156 Q170 18 170 32 V200" fill="${wallBg}" stroke="${wall}" stroke-width="6"/>
    </g>
    ${c.surround === 'moves' ? arc('M58 2 Q100 -12 142 2', wall, 'w') : ''}
    <path d="M86 22 L90 92 M114 22 L110 92" stroke="#8a97a0" stroke-width="2.5" stroke-dasharray="5 3"/>
    <g stroke="${INK}" stroke-linecap="round" fill="none">
      <path d="M100 88 V148" stroke-width="9"/>
      <path d="M100 98 L85 142 M100 98 L115 142" stroke-width="7"/>
      <path d="M100 148 L90 198 M100 148 L110 198" stroke-width="8"/>
    </g>
    <circle cx="100" cy="62" r="25" fill="#f6dcc4" stroke="${INK}" stroke-width="4"/>
    ${eyes}
    <path d="M93 74 q7 5 14 0" fill="none" stroke="${INK}" stroke-width="3" stroke-linecap="round"/>
    <g transform="${c.support === 'moves' ? 'rotate(-5 100 207)' : ''}">
      <rect x="45" y="199" width="110" height="16" rx="4" fill="${floor}"/>
    </g>
    ${c.support === 'moves' ? arc('M58 232 Q100 246 142 232', floor, 'f') : ''}
  </svg>`;
}

function halfDeaf(L, i, code) {
  const c = CONDITIONS[i];
  const S = SIMPLE[code];
  const step = (icon, text, state) => `<li class="${state}"><span class="ico">${icon}</span><span>${esc(text)}</span></li>`;
  const steps = [
    step(ICONS[c.eyes], c.eyes === 'open' ? S.eyesOpen : S.eyesClosed, c.eyes === 'open' ? 'ok' : 'closed'),
    step(ICONS['support_' + c.support], c.support === 'fixed' ? S.floorFixed : S.floorMoves, c.support === 'fixed' ? 'ok' : 'move'),
    // Yeux fermés : le décor n'a pas d'importance pour le patient, on ne le mentionne pas
    c.eyes === 'open' ? step(ICONS['surround_' + c.surround], c.surround === 'fixed' ? S.wallFixed : S.wallMoves, c.surround === 'fixed' ? 'ok' : 'move') : '',
    step('<span class="emo">🧍</span>', S.stand, 'neutral'),
  ].join('');
  return `
  <section class="half deaf">
    <header><span>${esc(L.title)}</span><span>${esc(S.sourds)}</span></header>
    <div class="row">
      <div class="scene">${scene(c, i)}</div>
      <div class="col">
        <h1><span class="num">${i + 1}</span>${esc(L.cond)} ${i + 1}</h1>
        <ul class="steps">${steps}</ul>
      </div>
    </div>
    <div class="signal"><span class="emo">✋</span>${esc(S.signal)}</div>
    <footer><span class="emo">⏱️</span> ${esc(S.time)} &nbsp;·&nbsp; <span class="emo">🦺</span> ${esc(S.safe)}</footer>
  </section>`;
}

// Version gros caractères (patients malvoyants / lecteur d'écran) : noir et blanc, contraste maximal
function halfLowVision(L, i, code) {
  const c = CONDITIONS[i];
  const badge = (label, icon, value, state) =>
    `<div class="badge ${state}"><div class="ico">${ICONS[icon]}</div><div class="lbl">${esc(label)}</div><div class="val">${esc(value)}</div></div>`;
  return `
  <section class="half lv">
    <header><span>${esc(L.title)}</span><span>${esc(SIMPLE[code].malvoyants)}</span></header>
    <h1>${esc(L.cond)} ${i + 1}</h1>
    <div class="badges">
      ${badge(L.eyes, c.eyes, c.eyes === 'open' ? L.open : L.closed, c.eyes === 'open' ? 'ok' : 'closed')}
      ${badge(L.support, 'support_' + c.support, c.support === 'fixed' ? L.fixedS : L.movesS, c.support === 'fixed' ? 'ok' : 'move')}
      ${badge(L.surround, 'surround_' + c.surround, c.surround === 'fixed' ? L.fixedD : L.movesD, c.surround === 'fixed' ? 'ok' : 'move')}
    </div>
    <p class="txt">${esc(L.text[i])}</p>
    <footer>${esc(L.footer)}</footer>
  </section>`;
}

const CSS = `
@font-face{font-family:NS;font-weight:400;src:url(${font('noto-sans', 'noto-sans-latin-400-normal.woff2')})}
@font-face{font-family:NS;font-weight:700;src:url(${font('noto-sans', 'noto-sans-latin-700-normal.woff2')})}
@font-face{font-family:NS;font-weight:400;unicode-range:U+0100-024F,U+1E00-1EFF;src:url(${font('noto-sans', 'noto-sans-latin-ext-400-normal.woff2')})}
@font-face{font-family:NSA;font-weight:400;src:url(${font('noto-sans-arabic', 'noto-sans-arabic-arabic-400-normal.woff2')})}
@font-face{font-family:NSA;font-weight:700;src:url(${font('noto-sans-arabic', 'noto-sans-arabic-arabic-700-normal.woff2')})}
@page{size:A4;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:NS,NSA,sans-serif;color:#1d2a33}
.emo{font-family:'Noto Color Emoji'}
.page{width:210mm;height:297mm;display:flex;flex-direction:column;page-break-after:always;overflow:hidden}
.half{height:148.5mm;padding:11mm 16mm 9mm;display:flex;flex-direction:column}
.cut{height:0;border-top:1.5px dashed #9aa7b0;margin:0 8mm}
header{display:flex;justify-content:space-between;font-size:9.5pt;color:#5b6b76;border-bottom:1px solid #d6dde2;padding-bottom:2.5mm}
h1{font-size:26pt;font-weight:700;margin:6mm 0 5mm;display:flex;align-items:center;gap:4mm;color:${INK}}
.num{display:inline-flex;align-items:center;justify-content:center;width:13mm;height:13mm;border-radius:50%;background:${INK};color:#fff;font-size:22pt}
.badges{display:flex;gap:5mm;margin-bottom:6mm}
.badge{flex:1;border-radius:3mm;padding:3mm 2mm;text-align:center;border:2px solid}
.badge .ico svg{width:15mm;height:11.5mm;stroke:currentColor;stroke-linecap:round}
.badge .lbl{font-size:10pt;margin-top:1mm;opacity:.8}
.badge .val{font-size:13pt;font-weight:700}
.ok{border-color:#2e8b6e;background:#eaf6f1;color:#1f6b53}
.closed{border-color:#3b5b9a;background:#ecf0f8;color:#2d4a85}
.move{border-color:#d9822b;background:#fdf1e4;color:#a85d14}
.neutral{border-color:#c9d2d8;background:#f4f6f8;color:${INK}}
.txt{font-size:15pt;line-height:1.5;flex:1}
footer{font-size:10pt;color:#5b6b76;border-top:1px solid #d6dde2;padding-top:2.5mm}
[dir=rtl] .txt{font-size:16pt;line-height:1.7}

/* Sourds */
.deaf{padding-top:9mm}
.deaf .row{display:flex;gap:6mm;flex:1;min-height:0;margin-top:3mm}
.deaf .scene{width:58mm;flex:none;display:flex;align-items:center}
.deaf .scene svg{width:100%;height:auto;max-height:98mm}
.deaf .col{flex:1;display:flex;flex-direction:column}
.deaf h1{margin:1mm 0 4mm}
.steps{list-style:none;display:flex;flex-direction:column;gap:2.5mm}
.steps li{display:flex;align-items:center;gap:3mm;border:2px solid;border-radius:3mm;padding:2mm 3mm;font-size:14pt;font-weight:700;line-height:1.25}
.steps .ico{flex:none;width:13mm;text-align:center}
.steps .ico svg{width:12mm;height:9mm;stroke:currentColor;stroke-linecap:round;vertical-align:middle}
.steps .emo{font-size:20pt}
.signal{display:flex;align-items:center;gap:3mm;margin:3mm 0 3mm;padding:2.5mm 4mm;border-radius:3mm;background:${INK};color:#fff;font-size:14pt;font-weight:700}
.signal .emo{font-size:20pt}
.deaf footer{font-size:11pt;color:${INK}}
.deaf footer .emo{font-size:13pt}

/* Malvoyants : noir sur blanc, l'état n'est jamais codé par la seule couleur */
.lv,.lv header,.lv footer{color:#000}
.lv{padding:9mm 13mm 7mm}
.lv header{font-size:13pt;font-weight:700;border-bottom:3px solid #000}
.lv h1{font-size:36pt;margin:3mm 0 3mm;color:#000}
.lv .badges{gap:4mm;margin-bottom:4mm}
.lv .badge{border:4px solid #000;border-radius:2mm;background:#fff;color:#000;padding:2mm}
.lv .badge.move{border-style:dashed;background:#ffe94d}
.lv .badge.closed{background:#000;color:#fff}
.lv .badge .ico svg{width:17mm;height:13mm}
.lv .badge .lbl{font-size:13pt;opacity:1}
.lv .badge .val{font-size:17pt}
.lv .txt{font-size:20pt;line-height:1.4}
.lv footer{font-size:13pt;font-weight:700;border-top:3px solid #000}
[dir=rtl] .lv .txt{font-size:21pt;line-height:1.55}
`;

function html(code, render, variant) {
  const L = LANGS[code];
  const pages = [0, 2, 4]
    .map((i) => `<div class="page">${render(L, i, code)}<div class="cut"></div>${render(L, i + 1, code)}</div>`)
    .join('');
  return `<!doctype html><html lang="${code}" dir="${L.dir || 'ltr'}"><head><meta charset="utf-8">
<title>${esc(L.title)} – ${esc(variant)}</title><style>${CSS}</style></head><body>${pages}</body></html>`;
}

const VARIANTS = [
  { dir: '.', prefix: 'SOT_consignes', render: half, label: (code) => LANGS[code].sub },
  { dir: 'sourds', prefix: 'SOT_sourds', render: halfDeaf, label: (code) => SIMPLE[code].sourds },
  { dir: 'malvoyants', prefix: 'SOT_malvoyants', render: halfLowVision, label: (code) => SIMPLE[code].malvoyants },
];

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const v of VARIANTS) {
    const outDir = path.join(__dirname, v.dir);
    fs.mkdirSync(outDir, { recursive: true });
    const files = [];
    for (const code of Object.keys(LANGS)) {
      await page.setContent(html(code, v.render, v.label(code)), { waitUntil: 'load' });
      await page.evaluate(() => document.fonts.ready);
      const file = path.join(outDir, `${v.prefix}_${code}.pdf`);
      // tagged : PDF balisé, lisible par les lecteurs d'écran
      await page.pdf({ path: file, format: 'A4', printBackground: true, preferCSSPageSize: true, tagged: true, outline: true });
      files.push(file);
      console.log('écrit', path.relative(__dirname, file));
    }
    // Fichier unique toutes langues
    const all = path.join(outDir, `${v.prefix}_toutes_langues.pdf`);
    execFileSync('python3', ['-c',
      'import sys\nfrom pypdf import PdfWriter\nw=PdfWriter()\nfor f in sys.argv[2:]: w.append(f)\nw.write(sys.argv[1])',
      all, ...files]);
    console.log('écrit', path.relative(__dirname, all));
  }
  await browser.close();
})();
