#!/usr/bin/env node
/* Build the Word report, or the executive brief, from tracker.json. Generic: works for any attack.

   node build_report.js tracker.json DIAGRAM_DIR OUT.docx [--exec]

   --exec builds the one or two page executive brief: page one of the report plus the top actions, with no ledger,
   technique or source tables. Both are handed over as Word files; no PDF copy is made.

   Needs the docx npm package (npm install -g docx). Quotes in tracker.json are never written to the report.
   In the full report, claim (Cxx, Axx) and source (Sxx) IDs link to bookmarks in the ledger appendix and the
   source register, so the report works on its own without the dashboard. Headings follow summary.language
   (en, es, fr, de, pt); ATT&CK names, ICD 203 terms and field terms stay in English. */
const fs = require('fs');
const os = require('os');
const path = require('path');
const zlib = require('zlib');
const { execFileSync } = require('child_process');
let docx;
try { docx = require('docx'); } catch (e) {
  try { docx = require(path.join(execFileSync('npm', ['root', '-g']).toString().trim(), 'docx')); }
  catch (e2) { console.error('MISSING the docx npm package. Run: npm install -g docx'); process.exit(2); }
}
const { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType, ShadingType,
  AlignmentType, ImageRun, Bookmark, InternalHyperlink, ExternalHyperlink, Header, Footer, PageNumber,
  LevelFormat, BorderStyle } = docx;

const args = process.argv.slice(2);
const EXEC = args.includes('--exec');
const [trackerPath, diagramDir, outPath] = args.filter((a) => !a.startsWith('--'));
if (!trackerPath || !outPath) { console.error('usage: node build_report.js tracker.json DIAGRAM_DIR OUT.docx [--exec]'); process.exit(2); }
const t = JSON.parse(fs.readFileSync(trackerPath, 'utf8'));
const S = (Array.isArray(t.summary) ? t.summary[0] : t.summary) || {};
const rows = (name) => (t[name] || []);
const str = (v) => (v == null ? '' : String(v)).trim();
const idList = (v) => str(Array.isArray(v) ? v.join(' ') : v).split(/[\s,]+/).filter(Boolean);
const NA = 'Not available in provided reports';
let ATTACK = null;
try { ATTACK = JSON.parse(fs.readFileSync(path.join(__dirname, 'attack_v20.json'), 'utf8')); } catch (e) { /* mitigations are skipped */ }

/* ---------- headings in the user's language ---------- */
const LABELS = {
  en: { title: (a) => `${a} Attack Tracker`, exec: (a) => `${a}: executive brief`, status: 'Status', iteration: 'Iteration', asof: 'As of', newest: 'Newest source',
    summary: 'Summary (bottom line)', relevance: 'Relevance to us', leadership: 'For leadership', kj: 'Key judgments', glance: 'Attack at a glance',
    metrics: 'Response metrics', changed: 'What changed since the last update', timeline: 'Timeline', victims: 'Victims', figures: 'Figures and how they were counted',
    chain: 'Attack chain and TTPs', mitigations: 'ATT&CK reference mitigations', soc: 'Kill chain for SOC hand-off', software: 'Software involved and versions',
    attribution: 'Attribution', hyps: 'Competing hypotheses', ach: 'Consistency of signals with each hypothesis', signals: 'Attribution signals and their limits',
    diamond: 'Diamond Model', said: 'Who has said what', actionsCh: 'Relevance and recommended actions', exposure: 'Exposure question', actions: 'Actions',
    watch: 'Indicators to watch', gaps: 'Information gaps', sourcesCh: 'Claims and sources', conflicts: 'Where sources disagree', register: 'Source register',
    scope: 'Scope', validation: 'Validation status', appendix: 'Appendix: claims ledger', topActions: 'Top actions' },
  es: { title: (a) => `Seguimiento del ataque: ${a}`, exec: (a) => `${a}: resumen ejecutivo`, status: 'Estado', iteration: 'Iteración', asof: 'A fecha de', newest: 'Fuente más reciente',
    summary: 'Resumen (conclusión principal)', relevance: 'Relevancia para nosotros', leadership: 'Para la dirección', kj: 'Juicios clave', glance: 'El ataque de un vistazo',
    metrics: 'Métricas de respuesta', changed: 'Qué ha cambiado desde la última actualización', timeline: 'Cronología', victims: 'Víctimas', figures: 'Cifras y cómo se contaron',
    chain: 'Cadena de ataque y TTP', mitigations: 'Mitigaciones de referencia de ATT&CK', soc: 'Cadena de ataque para el SOC', software: 'Software implicado y versiones',
    attribution: 'Atribución', hyps: 'Hipótesis en competencia', ach: 'Coherencia de los indicios con cada hipótesis', signals: 'Indicios de atribución y sus límites',
    diamond: 'Modelo de diamante', said: 'Quién ha dicho qué', actionsCh: 'Relevancia y acciones recomendadas', exposure: 'Pregunta de exposición', actions: 'Acciones',
    watch: 'Indicadores que vigilar', gaps: 'Lagunas de información', sourcesCh: 'Afirmaciones y fuentes', conflicts: 'Dónde discrepan las fuentes', register: 'Registro de fuentes',
    scope: 'Alcance', validation: 'Estado de la validación', appendix: 'Anexo: registro de afirmaciones', topActions: 'Acciones prioritarias' },
  fr: { title: (a) => `Suivi de l'attaque : ${a}`, exec: (a) => `${a} : note de synthèse`, status: 'Statut', iteration: 'Itération', asof: 'Au', newest: 'Source la plus récente',
    summary: "Synthèse (l'essentiel)", relevance: 'Pertinence pour nous', leadership: 'Pour la direction', kj: 'Jugements clés', glance: "L'attaque en bref",
    metrics: 'Indicateurs de réponse', changed: 'Ce qui a changé depuis la dernière mise à jour', timeline: 'Chronologie', victims: 'Victimes', figures: 'Chiffres et méthode de comptage',
    chain: "Chaîne d'attaque et TTP", mitigations: 'Mesures de référence ATT&CK', soc: "Chaîne d'attaque pour le SOC", software: 'Logiciels concernés et versions',
    attribution: 'Attribution', hyps: 'Hypothèses concurrentes', ach: 'Cohérence des signaux avec chaque hypothèse', signals: "Signaux d'attribution et leurs limites",
    diamond: 'Modèle du diamant', said: 'Qui a dit quoi', actionsCh: 'Pertinence et actions recommandées', exposure: "Question d'exposition", actions: 'Actions',
    watch: 'Indicateurs à surveiller', gaps: 'Lacunes d\'information', sourcesCh: 'Affirmations et sources', conflicts: 'Où les sources divergent', register: 'Registre des sources',
    scope: 'Périmètre', validation: 'État de la validation', appendix: 'Annexe : registre des affirmations', topActions: 'Actions prioritaires' },
  de: { title: (a) => `Angriffsverfolgung: ${a}`, exec: (a) => `${a}: Kurzbericht für die Leitung`, status: 'Status', iteration: 'Iteration', asof: 'Stand', newest: 'Neueste Quelle',
    summary: 'Zusammenfassung (Kernaussage)', relevance: 'Relevanz für uns', leadership: 'Für die Leitung', kj: 'Zentrale Bewertungen', glance: 'Der Angriff im Überblick',
    metrics: 'Reaktionskennzahlen', changed: 'Änderungen seit der letzten Aktualisierung', timeline: 'Zeitleiste', victims: 'Betroffene', figures: 'Zahlen und Zählweise',
    chain: 'Angriffskette und TTPs', mitigations: 'ATT&CK-Referenzmaßnahmen', soc: 'Angriffskette für die SOC-Übergabe', software: 'Beteiligte Software und Versionen',
    attribution: 'Attribution', hyps: 'Konkurrierende Hypothesen', ach: 'Vereinbarkeit der Hinweise mit jeder Hypothese', signals: 'Attributionshinweise und ihre Grenzen',
    diamond: 'Diamond-Modell', said: 'Wer was gesagt hat', actionsCh: 'Relevanz und empfohlene Maßnahmen', exposure: 'Frage zur Exposition', actions: 'Maßnahmen',
    watch: 'Zu beobachtende Anzeichen', gaps: 'Informationslücken', sourcesCh: 'Aussagen und Quellen', conflicts: 'Wo Quellen sich widersprechen', register: 'Quellenverzeichnis',
    scope: 'Umfang', validation: 'Validierungsstatus', appendix: 'Anhang: Aussagenregister', topActions: 'Wichtigste Maßnahmen' },
  pt: { title: (a) => `Acompanhamento do ataque: ${a}`, exec: (a) => `${a}: resumo executivo`, status: 'Status', iteration: 'Iteração', asof: 'Em', newest: 'Fonte mais recente',
    summary: 'Resumo (conclusão principal)', relevance: 'Relevância para nós', leadership: 'Para a liderança', kj: 'Avaliações principais', glance: 'O ataque em resumo',
    metrics: 'Métricas de resposta', changed: 'O que mudou desde a última atualização', timeline: 'Cronologia', victims: 'Vítimas', figures: 'Números e como foram contados',
    chain: 'Cadeia de ataque e TTPs', mitigations: 'Mitigações de referência do ATT&CK', soc: 'Cadeia de ataque para o SOC', software: 'Software envolvido e versões',
    attribution: 'Atribuição', hyps: 'Hipóteses concorrentes', ach: 'Coerência dos sinais com cada hipótese', signals: 'Sinais de atribuição e seus limites',
    diamond: 'Modelo Diamante', said: 'Quem disse o quê', actionsCh: 'Relevância e ações recomendadas', exposure: 'Pergunta de exposição', actions: 'Ações',
    watch: 'Indicadores a vigiar', gaps: 'Lacunas de informação', sourcesCh: 'Afirmações e fontes', conflicts: 'Onde as fontes divergem', register: 'Registro de fontes',
    scope: 'Escopo', validation: 'Status da validação', appendix: 'Apêndice: registro de afirmações', topActions: 'Ações prioritárias' },
};
const LANG = str(S.language).toLowerCase().slice(0, 2);
const L = LABELS[LANG] || LABELS.en;

const claimIds = new Set(rows('ledger').map((c) => str(c.claim_id)));
const sourceIds = new Set(rows('sources').map((x) => str(x.source_id)));
const FONT = 'Arial';
const W = 9360; // US Letter, 1-inch margins, in DXA
const safeUrl = (u) => (/^https?:\/\//i.test(str(u)) ? str(u) : null);

/* ---------- text with linked IDs (plain text in the executive brief, which has no appendix) ---------- */
function runs(text, opts = {}) {
  const out = [];
  const s = str(text);
  if (EXEC) return [new TextRun({ text: s, ...opts })];
  const re = /\b([CAS]\d{2,})\b/g;
  let last = 0, m;
  while ((m = re.exec(s))) {
    const id = m[1];
    const anchor = sourceIds.has(id) && id.startsWith('S') ? `src_${id}` : (claimIds.has(id) ? `claim_${id}` : null);
    if (!anchor) continue;
    if (m.index > last) out.push(new TextRun({ text: s.slice(last, m.index), ...opts }));
    out.push(new InternalHyperlink({ anchor, children: [new TextRun({ text: id, style: 'Hyperlink', ...opts })] }));
    last = m.index + id.length;
  }
  if (last < s.length || !out.length) out.push(new TextRun({ text: s.slice(last), ...opts }));
  return out;
}
const P = (text, opts = {}) => new Paragraph({ spacing: { after: 120 }, ...opts.para, children: runs(text, opts.run) });
let firstH1 = true;
const H1 = (text, breakBefore = true) => {
  const p = new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: breakBefore && !firstH1 && !EXEC, keepNext: true,
    children: [new TextRun(text)] });
  firstH1 = false;
  return p;
};
const H2 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_2, keepNext: true, children: [new TextRun(text)] });
const H3 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_3, keepNext: true, children: [new TextRun(text)] });
const note = (text) => new Paragraph({ spacing: { after: 120 }, keepNext: true,
  children: [new TextRun({ text, italics: true, color: '555555', size: 18 })] });

/* ---------- tables with dual widths ---------- */
const border = { style: BorderStyle.SINGLE, size: 4, color: 'C9CED6' };
const borders = { top: border, bottom: border, left: border, right: border };
function table(headers, data, fractions, cellFn) {
  const widths = fractions.map((f) => Math.floor(W * f));
  widths[widths.length - 1] = W - widths.slice(0, -1).reduce((a, b) => a + b, 0);
  const cell = (content, i, head) => new TableCell({
    width: { size: widths[i], type: WidthType.DXA }, borders,
    margins: { top: 60, bottom: 60, left: 90, right: 90 },
    shading: head ? { type: ShadingType.CLEAR, fill: 'EEF0F3', color: 'auto' } : undefined,
    children: Array.isArray(content) ? content
      : [new Paragraph({ children: head ? [new TextRun({ text: str(content), bold: true, size: 18 })] : runs(content, { size: 18 }) })],
  });
  const trs = [new TableRow({ tableHeader: true, cantSplit: true, children: headers.map((h, i) => cell(h, i, true)) })];
  for (const r of data) trs.push(new TableRow({ cantSplit: true, children: r.map((v, i) => cell(cellFn ? cellFn(v, i, r) : v, i, false)) }));
  return new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: widths, rows: trs });
}
const spacer = () => new Paragraph({ spacing: { after: 160 }, children: [] });

/* ---------- images: PNG, or SVG with a PNG fallback when matplotlib was missing ---------- */
function blankPng(w, h) {
  const crcTable = Array.from({ length: 256 }, (_, n) => { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; return c >>> 0; });
  const crc = (buf) => { let c = 0xffffffff; for (const b of buf) c = crcTable[(c ^ b) & 0xff] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; };
  const chunk = (type, data) => {
    const len = Buffer.alloc(4); len.writeUInt32BE(data.length);
    const td = Buffer.concat([Buffer.from(type), data]); const c = Buffer.alloc(4); c.writeUInt32BE(crc(td));
    return Buffer.concat([len, td, c]);
  };
  const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4); ihdr[8] = 8; ihdr[9] = 0;
  const raw = Buffer.alloc((w + 1) * h, 255); for (let y = 0; y < h; y++) raw[y * (w + 1)] = 0;
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ihdr), chunk('IDAT', zlib.deflateSync(raw)), chunk('IEND', Buffer.alloc(0))]);
}
function svgToPng(svgPath) {
  const out = path.join(os.tmpdir(), `tc-${process.pid}-${path.basename(svgPath, '.svg')}.png`);
  const tries = [['rsvg-convert', ['-z', '2', '-o', out, svgPath]], ['magick', [svgPath, out]], ['convert', [svgPath, out]],
    ['inkscape', [svgPath, '--export-type=png', `--export-filename=${out}`]]];
  for (const [cmd, a] of tries) {
    try { execFileSync(cmd, a, { stdio: 'ignore' }); if (fs.existsSync(out)) return fs.readFileSync(out); } catch (e) { /* try the next tool */ }
  }
  return null;
}
let usedSvg = false;
function image(file, widthPx, alt) {
  const base = path.join(diagramDir || '.', file);
  const png = base + '.png', svg = base + '.svg';
  let w, h, run;
  if (fs.existsSync(png)) {
    const buf = fs.readFileSync(png);
    w = buf.readUInt32BE(16); h = buf.readUInt32BE(20);
    // Never enlarge past natural size (images are rendered at 200 dpi, shown at 96 px per inch).
    let dw = Math.min(widthPx, Math.round(w * 96 / 200));
    if (dw * h / w > 600) dw = Math.round(600 * w / h);
    run = new ImageRun({ type: 'png', data: buf, transformation: { width: dw, height: Math.round(dw * h / w) }, altText: { title: alt, description: alt, name: alt } });
  } else if (fs.existsSync(svg)) {
    const buf = fs.readFileSync(svg);
    const head = buf.toString('utf8', 0, 600);
    w = Number((head.match(/\bwidth="([\d.]+)/) || [])[1]) || 600; h = Number((head.match(/\bheight="([\d.]+)/) || [])[1]) || 400;
    let dw = Math.min(widthPx, w);
    if (dw * h / w > 600) dw = Math.round(600 * w / h);
    const fallback = svgToPng(svg) || blankPng(Math.max(1, Math.round(w)), Math.max(1, Math.round(h)));
    usedSvg = true;
    run = new ImageRun({ type: 'svg', data: buf, fallback: { type: 'png', data: fallback }, transformation: { width: dw, height: Math.round(dw * h / w) }, altText: { title: alt, description: alt, name: alt } });
  } else {
    return note(`The ${alt.toLowerCase()} image was not rendered in this run.`);
  }
  return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 160 }, keepNext: false, children: [run] });
}
const fmtDate = (v) => {
  const m = str(v).match(/^(\d{4})-(\d{2})(?:-(\d{2}))?(?:T(\d{2}):(\d{2}))?/);
  if (!m) return str(v);
  const mon = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][Number(m[2]) - 1];
  return (m[3] ? Number(m[3]) + ' ' : '') + mon + ' ' + m[1] + (m[4] ? `, ${m[4]}:${m[5]} UTC` : '');
};

/* ---------- derived content ---------- */
const PREC = ['exact', 'day', 'approx', 'month'];
function irMetrics() {
  const evs = rows('timeline').filter((e) => str(e.status) !== 'Superseded' && !isNaN(Date.parse(str(e.when).length === 7 ? str(e.when) + '-01' : str(e.when))));
  const when = (e) => Date.parse(str(e.when).length === 7 ? str(e.when) + '-01' : str(e.when));
  const first = (types) => evs.filter((e) => types.includes(str(e.event_type))).sort((a, b) => when(a) - when(b))[0];
  const defs = [['Dwell time', ['earliest-activity', 'initial-access'], ['detection']], ['Time to contain', ['detection'], ['containment']],
    ['Time to disclose', ['detection'], ['disclosure']], ['Time to notify', ['detection'], ['notification']]];
  const out = [];
  for (const [name, a, b] of defs) {
    const ea = first(a), eb = first(b);
    if (!ea || !eb) continue;
    const days = (when(eb) - when(ea)) / 864e5;
    if (days < 0) continue;
    const pa = str(ea.precision) || 'day', pb = str(eb.precision) || 'day';
    const worst = PREC.indexOf(pa) > PREC.indexOf(pb) ? pa : pb;
    out.push([name, worst === 'exact' ? (Math.round(days * 10) / 10).toString() : Math.round(days).toString(), worst,
      `${ea.event_id} (${fmtDate(ea.when)}) to ${eb.event_id} (${fmtDate(eb.when)})`]);
  }
  return out;
}
function latestChanges() {
  const all = rows('changes');
  const its = all.map((r) => Number(r.iteration)).filter((n) => n > 0);
  return its.length ? all.filter((r) => Number(r.iteration) === Math.max(...its)) : all;
}
const ttpDomain = (r) => str(r.domain) || (/^T0\d{3}/.test(str(r.technique_id)) ? 'ics' : 'enterprise');
function mitigationsFor(r) {
  if (!ATTACK) return [];
  const dom = ATTACK[ttpDomain(r)];
  const tech = dom && dom.techniques[str(r.technique_id)];
  return tech ? tech.mitigations.map((m) => [m, dom.mitigations[m] || '']) : [];
}

/* ---------- page one: the leadership page (the whole of the executive brief, plus top actions) ---------- */
const body = [];
const ledger = rows('ledger');
const kjs = ledger.filter((c) => str(c.topic) === 'Key judgment');

body.push(new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun(EXEC ? L.exec(str(S.attack)) : L.title(str(S.attack)))] }));
const newest = str(S.newest_source_date) ? `  |  ${L.newest}: ${fmtDate(S.newest_source_date)}` : '';
body.push(new Paragraph({ spacing: { after: 240 }, children: [new TextRun({ text:
  `${L.status}: ${str(S.status)}  |  ${L.iteration} ${str(S.iteration)}  |  ${L.asof} ${fmtDate(S.as_of)}${newest}  |  ${str(S.tlp)}`, color: '555555', size: 18 })] }));

body.push(H1(L.summary, false));
body.push(P(S.bluf));
if (str(S.relevance)) { body.push(H2(L.relevance)); body.push(P(S.relevance)); }
body.push(H2(L.leadership));
body.push(P(S.leadership));

body.push(H2(L.kj));
kjs.forEach((c) => body.push(new Paragraph({ numbering: { reference: 'kj', level: 0 }, spacing: { after: 80 },
  children: [...runs(c.claim),
    ...(EXEC ? [] : [new TextRun({ text: '  Basis: ', color: '555555' }), ...runs(str(c.basis) || NA, { color: '555555' })]),
    ...(str(c.contrary) ? [new TextRun({ text: '  Strongest contrary signal: ', color: '555555' }), ...runs(str(c.contrary), { color: '555555' })] : [])] })));
if (!kjs.length) body.push(P(NA));

body.push(H2(L.glance));
body.push(table(['Item', 'Summary'], [
  ['Victim', str(S.glance_victim) || NA], ['Attack type', str(S.glance_type) || NA],
  ['Window', str(S.glance_window) || NA], ['Initial access', str(S.glance_access) || NA],
  ['Impact', str(S.glance_impact) || NA], ['Attribution status', str(S.glance_attribution) || NA],
], [0.25, 0.75]));

const metrics = irMetrics();
if (metrics.length) {
  body.push(H2(L.metrics));
  body.push(table(['Metric', 'Days', 'Precision', 'From and to'], metrics, [0.22, 0.1, 0.13, 0.55]));
}

const changes = latestChanges();
if (changes.length && !EXEC) {
  body.push(H2(L.changed));
  body.push(table(['ID', 'Kind', 'Item', 'Before', 'After'],
    changes.map((r) => [r.change_id, r.kind, r.item, r.before, r.after]), [0.08, 0.13, 0.49, 0.15, 0.15]));
}

const gaps = rows('gaps');
const openRow = (g) => str(g.status) !== 'Closed';
if (EXEC) {
  body.push(H2(L.topActions));
  const top = gaps.filter((g) => g.kind === 'Action' && openRow(g)).slice(0, 5);
  if (top.length) body.push(table(['Action', 'How', 'Owner'], top.map((g) => [g.item, g.next_step, g.owner]), [0.3, 0.55, 0.15]));
  else body.push(P(NA));
  body.push(H2(L.exposure));
  body.push(P(S.exposure));
  body.push(note('The attack tracker dashboard, the Word report and the STIX bundle hold the timeline, techniques, sources and the claims ledger behind every statement here.'));
} else {
  /* ---------- Timeline ---------- */
  body.push(H1(L.timeline));
  body.push(image('timeline', 500, 'Timeline'));
  body.push(table(['ID', 'When', 'Lane', 'Event', 'Status', 'Claims'],
    [...rows('timeline')].sort((a, b) => str(a.when).localeCompare(str(b.when)))
      .map((e) => [e.event_id, fmtDate(e.when) + (str(e.end) ? ' to ' + fmtDate(e.end) : ''), e.lane, e.event, e.status, e.claim_ids]),
    [0.07, 0.16, 0.15, 0.39, 0.11, 0.12]));

  /* ---------- Victims ---------- */
  body.push(H1(L.victims));
  body.push(table(['ID', 'Victim', 'Role', 'Tier', 'Impact', 'Data exposed', 'How counted'],
    rows('victims').map((v) => [v.victim_id, v.victim, v.role, v.tier, v.impact, str(v.data_types) || 'none reported', v.count_method]),
    [0.07, 0.15, 0.13, 0.1, 0.2, 0.14, 0.21]));
  if (rows('figures').length) {
    body.push(H2(L.figures));
    body.push(table(['ID', 'Figure', 'Value', 'Status', 'Method and caveats'],
      rows('figures').map((f) => [f.figure_id, f.label, `${str(f.value)} ${str(f.unit)}`.trim(), f.status, f.note]),
      [0.07, 0.25, 0.13, 0.12, 0.43]));
  }

  /* ---------- TTPs ---------- */
  body.push(H1(L.chain));
  body.push(P(`Techniques are mapped to MITRE ATT&CK ${str(S.attack_version) || '(version not recorded)'}. ` +
    'The chain shows the phases in order; the matrix shows the same techniques by tactic. Border colour shows occurrence.'));
  body.push(image('attack-chain', 624, 'Attack chain'));
  body.push(image('attack-matrix', 600, 'ATT&CK matrix'));
  const techLink = (v, size = 18) => [new Paragraph({ children: [new ExternalHyperlink({ link: `https://attack.mitre.org/techniques/${str(v).replace('.', '/')}/`,
    children: [new TextRun({ text: str(v), style: 'Hyperlink', size })] })] })];
  const ttpCell = (v, i) => (i === 0 && str(v) !== 'Unmapped' ? techLink(v) : v);
  body.push(table(['Technique', 'Name', 'Tactic', 'How this attacker used it', 'Occurrence', 'Confidence', 'Events', 'Claims'],
    rows('ttps').map((r) => [r.technique_id, r.name, (ttpDomain(r) === 'ics' ? 'ics: ' : '') + str(r.tactic), r.how_used, r.occurrence, r.confidence, r.event_ids, r.claim_ids]),
    [0.12, 0.14, 0.12, 0.24, 0.11, 0.1, 0.08, 0.09], ttpCell));
  const mitRows = [];
  const seenTech = new Set();
  for (const r of rows('ttps')) {
    const tid = str(r.technique_id);
    if (tid === 'Unmapped' || seenTech.has(tid)) continue;
    seenTech.add(tid);
    const ms = mitigationsFor(r);
    if (ms.length) mitRows.push([tid, ms]);
  }
  if (mitRows.length) {
    body.push(H2(L.mitigations));
    body.push(note('From the ATT&CK knowledge base, not from the reporting. Use them to check coverage; the actions chapter holds what the sources support.'));
    body.push(table(['Technique', 'Mitigations'], mitRows.map(([tid, ms]) => [tid, ms]), [0.15, 0.85], (v, i) => {
      if (i === 0) return techLink(v);
      return [new Paragraph({ children: v.flatMap(([m, n], k) => [
        new ExternalHyperlink({ link: `https://attack.mitre.org/mitigations/${m}/`, children: [new TextRun({ text: m, style: 'Hyperlink', size: 18 })] }),
        new TextRun({ text: ` ${n}${k < v.length - 1 ? '; ' : ''}`, size: 18 })]) })];
    }));
  }

  /* ---------- SOC hand-off ---------- */
  const sw = rows('software'), kc = [...rows('killchain')].sort((a, b) => Number(a.order) - Number(b.order));
  if (sw.length || kc.length) {
    body.push(H1(L.soc));
    body.push(P('Fields drawn from the sources cite their claims. Anything starting "Analyst guidance:" is not in the ' +
      'sources and should be checked against local logging before use. A log stream that must be turned on first says so.'));
    body.push(H2(L.software));
    const cves = sw.filter((p) => str(p.cve));
    if (!cves.length) body.push(P('No CVE or software vulnerability is reported, so there is no patch target.'));
    if (sw.length) body.push(table(['ID', 'Software', 'Version', 'Role', 'How', 'Claims'],
      sw.map((p) => [p.software_id, p.software, p.version, p.role, p.how, p.claim_ids]), [0.07, 0.22, 0.1, 0.18, 0.31, 0.12]));
    if (cves.length) {
      body.push(spacer());
      body.push(table(['CVE', 'Software', 'Affected', 'Fixed in', 'Advisory'],
        cves.map((p) => [p.cve, p.software, p.affected_versions, p.fixed_version, p.advisory_source]), [0.18, 0.27, 0.2, 0.15, 0.2]));
    }
    const fields = [['tactic', 'Tactic'], ['techniques', 'Techniques'], ['process', 'Process (image and path)'],
      ['action', 'Action'], ['logs', 'Logs'], ['parent', 'Parent'], ['artefacts', 'Artefacts'], ['network', 'Network (defanged)'],
      ['detections', 'Detections'], ['hunt', 'Hunt'], ['claim_ids', 'Claims']];
    for (const k of kc) {
      body.push(H3(`${str(k.order)}. ${str(k.stage)} (${str(k.observed)})`));
      body.push(table(['Field', 'Value'], fields.map(([f, label]) => [label, str(k[f]) || NA]), [0.25, 0.75]));
      body.push(spacer());
    }
  } else if (str(S.soc_note)) {
    body.push(H1(L.soc));
    body.push(P(S.soc_note));
  }

  /* ---------- Attribution ---------- */
  body.push(H1(L.attribution));
  body.push(P(S.attribution_statement));
  const attr = rows('attribution');
  const hyps = attr.filter((a) => a.kind === 'Hypothesis');
  const evid = attr.filter((a) => a.kind === 'Signal' || a.kind === 'Evidence');
  if (hyps.length) {
    body.push(H2(L.hyps));
    body.push(table(['ID', 'Hypothesis', 'Likelihood', 'Confidence', 'For', 'Against'],
      hyps.map((a) => [a.row_id, a.party, a.likelihood, a.confidence, a.for_signals || a.for_evidence, a.against_signals || a.against_evidence]),
      [0.07, 0.18, 0.12, 0.11, 0.26, 0.26]));
  }
  if (hyps.length >= 2) {
    const cites = (text) => new Set(str(text).match(/\b[SCH]\d{2,}\b/g) || []);
    const fs_ = hyps.map((h) => cites(h.for_signals || h.for_evidence)), as_ = hyps.map((h) => cites(h.against_signals || h.against_evidence));
    let ev = evid.map((e) => ({ id: str(e.row_id), label: str(e.party), refs: [str(e.row_id), ...idList(e.claim_ids)] }));
    if (!ev.length) { const all = new Set(); [...fs_, ...as_].forEach((s) => s.forEach((x) => all.add(x))); ev = [...all].sort().map((id) => ({ id, label: '', refs: [id] })); }
    const score = hyps.map(() => 0);
    const data = ev.map((e) => [`${e.id} ${e.label}`.trim(), ...hyps.map((h, i) => {
      const f = e.refs.some((x) => fs_[i].has(x)), a = e.refs.some((x) => as_[i].has(x));
      if (a) score[i] += 1;
      return f && a ? 'C/I' : f ? 'C' : a ? 'I' : '-';
    })]);
    data.push(['Inconsistent items', ...score.map(String)]);
    body.push(H2(L.ach));
    body.push(note('C: consistent (cited for the hypothesis). I: inconsistent (cited against it). -: not applicable. The hypothesis with the fewest I marks survives best.'));
    const wEach = 0.7 / hyps.length;
    body.push(table(['Signal', ...hyps.map((h) => `${h.row_id} ${h.party}`)], data, [0.3, ...hyps.map(() => wEach)]));
  }
  if (evid.length) {
    body.push(H2(L.signals));
    body.push(table(['ID', 'Signal', 'What it shows', 'Limits'],
      evid.map((a) => [a.row_id, a.party, a.position, a.limits]), [0.07, 0.2, 0.4, 0.33]));
  }
  body.push(H2(L.diamond));
  body.push(image('diamond', 460, 'Diamond Model'));
  body.push(table(['Vertex', 'What the reporting describes'],
    ['Adversary', 'Capability', 'Infrastructure', 'Victim'].map((v) => [v, str((attr.find((a) => a.kind === 'Diamond' && a.party === v) || {}).position) || NA]),
    [0.2, 0.8]));
  const stm = attr.filter((a) => a.kind === 'Statement');
  if (stm.length) {
    body.push(H2(L.said));
    body.push(table(['ID', 'Party', 'Position'], stm.map((a) => [a.row_id, a.party, a.position]), [0.08, 0.25, 0.67]));
  }

  /* ---------- Actions, watch, gaps ---------- */
  body.push(H1(L.actionsCh));
  body.push(H2(L.exposure));
  body.push(P(S.exposure));
  const statusText = (g) => (str(g.status) === 'Closed' ? `Closed by ${str(g.closed_by)}` : 'Open' + (String(g.blocking) === 'true' ? ' (blocking)' : ''));
  body.push(H2(L.actions));
  body.push(table(['ID', 'Action', 'How', 'Owner'], gaps.filter((g) => g.kind === 'Action').map((g) => [g.item_id, g.item, g.next_step, g.owner]),
    [0.07, 0.3, 0.5, 0.13]));
  body.push(H2(L.watch));
  body.push(table(['ID', 'Watch for', 'Why', 'How'], gaps.filter((g) => g.kind === 'Watch').map((g) => [g.item_id, g.item, g.why, g.next_step]),
    [0.07, 0.31, 0.27, 0.35]));
  body.push(H2(L.gaps));
  body.push(table(['ID', 'Gap', 'Why it matters', 'What would close it', 'Status'],
    gaps.filter((g) => g.kind === 'Gap').sort((a, b) => (str(a.status) === 'Closed') - (str(b.status) === 'Closed'))
      .map((g) => [g.item_id, g.item, g.why, g.next_step, statusText(g)]),
    [0.07, 0.27, 0.24, 0.27, 0.15]));

  /* ---------- Claims and sources ---------- */
  body.push(H1(L.sourcesCh));
  if (rows('conflicts').length) {
    body.push(H2(L.conflicts));
    body.push(table(['ID', 'Topic', 'Position A', 'Position B', 'Resolution'],
      rows('conflicts').map((k) => [k.conflict_id, k.topic, k.position_a, k.position_b, k.resolution]), [0.07, 0.15, 0.24, 0.24, 0.3]));
  }
  body.push(H2(L.register));
  const srcCell = (v, i, r) => {
    if (i === 0) return [new Paragraph({ children: [new Bookmark({ id: `src_${str(v)}`, children: [new TextRun({ text: str(v), size: 18 })] })] })];
    if (i === 1 && r.url) return [new Paragraph({ children: [new ExternalHyperlink({ link: r.url, children: [new TextRun({ text: str(v), style: 'Hyperlink', size: 18 })] })] })];
    return v;
  };
  const srcRows = rows('sources').map((x) => Object.assign([x.source_id, x.title, x.publisher, fmtDate(x.date), x.reliability, x.position, x.originator, x.interest, x.retrieval],
    { url: safeUrl(x.url) }));
  body.push(table(['ID', 'Title', 'Publisher', 'Date', 'Rel.', 'Position', 'Originator', 'Interest', 'Retrieval'], srcRows,
    [0.06, 0.24, 0.13, 0.1, 0.05, 0.1, 0.13, 0.1, 0.09], srcCell));
  body.push(H2(L.scope));
  body.push(P(S.scope));
  body.push(H2(L.validation));
  body.push(P(str(S.validation) || NA));

  /* ---------- Appendix: ledger with bookmarks ---------- */
  body.push(H1(L.appendix));
  body.push(P('One fact per row, in the analyst\'s words. Status labels: Confirmed means two or more independent originators, or the victim or an authority speaking about its own actions; ' +
    'Reported means one credible originator, and an allegation against someone not convicted stays here; Actor-asserted means the attacker said it about itself, which shows only that the claim was made; ' +
    'Assessed is an analytic judgment; Superseded means later reporting replaced it; Unknown is a gap that matters.'));
  const ledCell = (v, i) => i === 0
    ? [new Paragraph({ children: [new Bookmark({ id: `claim_${str(v)}`, children: [new TextRun({ text: str(v), bold: true, size: 18 })] })] })]
    : v;
  body.push(table(['ID', 'Topic', 'Claim', 'Status', 'Cred.', 'Sources', 'Corroboration or basis'],
    ledger.map((c) => [c.claim_id, c.topic, c.claim, c.status + (str(c.superseded_by) ? ` by ${str(c.superseded_by)}` : ''), c.credibility, c.source_ids,
      str(c.corroboration) || str(c.basis)]),
    [0.07, 0.12, 0.33, 0.13, 0.07, 0.1, 0.18], ledCell));
}

/* ---------- document ---------- */
const doc = new Document({
  creator: 'track-cyberattack', title: EXEC ? L.exec(str(S.attack)) : L.title(str(S.attack)),
  styles: {
    default: { document: { run: { font: FONT, size: 21 } } },
    paragraphStyles: [
      { id: 'Title', name: 'Title', basedOn: 'Normal', run: { font: FONT, size: 44, color: '1A1A1A' }, paragraph: { spacing: { after: 120 } } },
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: FONT, size: 32, bold: true, color: '1A1A1A' }, paragraph: { spacing: { before: 240, after: 160 }, outlineLevel: 0, keepNext: true } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: FONT, size: 25, bold: true, color: '333333' }, paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 1, keepNext: true } },
      { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: FONT, size: 22, bold: true, color: '333333' }, paragraph: { spacing: { before: 160, after: 80 }, outlineLevel: 2, keepNext: true } },
    ],
  },
  numbering: { config: [{ reference: 'kj', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 360, hanging: 360 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
      children: [new TextRun({ text: `${str(S.tlp)}  |  ${str(S.attack)}`, size: 16, color: '777777' })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ children: ['Page ', PageNumber.CURRENT, ' of ', PageNumber.TOTAL_PAGES], size: 16, color: '777777' })] })] }) },
    children: body,
  }],
});
Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(outPath, buf);
  console.log(`wrote ${outPath}${EXEC ? ' (executive brief)' : ''}${usedSvg ? '; SVG images embedded with PNG fallbacks' : ''}`);
}).catch((e) => { console.error('Report build failed:', e.message); process.exit(1); });
