/* track-cyberattack standalone runtime.
   tracker_tool.py html inlines this file into one page with the fixed dashboard template and the attack tracker rows,
   so the dashboard opens offline in any browser and looks the same outside claude.ai. It provides:
   1. the design tokens the template reads (light and dark),
   2. a small stand-in for the parts of D3 the template uses, when the CDN copy cannot load (offline),
   3. the Dashboard runtime calls the template makes (dash.calc, dash.data, dash.draw, dash.onData, dash.setLink,
      dash.colors), computed from the embedded rows. Nothing is fetched and nothing is stored. */
(function () {
  'use strict';

  /* ---------- 1. design tokens ---------- */
  var css = [
    ':root{--cds-pad-xs:4px;--cds-pad-sm:8px;--cds-pad-md:12px;--cds-pad-lg:20px;--cds-gap-xs:4px;--cds-gap-sm:8px;',
    '--cds-gap-md:16px;--cds-gap-lg:24px;--cds-font-size-title:28px;--cds-font-size-heading:17px;--cds-font-size-body:15px;',
    '--cds-font-size-caption:13px;--cds-font-weight-medium:600;--cds-radius:8px;--cds-dur-slow:.6s;',
    '--font-anthropic-sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;',
    '--font-anthropic-serif:Georgia,"Times New Roman",serif;',
    '--color-bg:#f4f3ee;--color-panel:#ffffff;--color-fg:#1f1e1d;--color-fg-muted:#6b6a66;--color-border-line:#dedcd5;',
    '--color-ok:#2e7d4f;--color-warn:#b45f06;--color-bad:#b3261e;--cds-chart-muted:#a3a29c;--cds-chart-grid:#ebe9e3;',
    '--cds-chart-axis:#a3a29c;--cds-surface-popover:#ffffff;--cds-border:#dedcd5;',
    '--cds-shadow-popover:0 4px 16px rgba(0,0,0,.12);--cds-text-secondary:#6b6a66;color-scheme:light}',
    '@media (prefers-color-scheme:dark){:root{--color-bg:#1d1c1a;--color-panel:#262624;--color-fg:#ecebe6;',
    '--color-fg-muted:#a6a49d;--color-border-line:#3a3936;--color-ok:#6cc08b;--color-warn:#f0a44b;--color-bad:#f2867e;',
    '--cds-chart-muted:#77756f;--cds-chart-grid:#33322f;--cds-chart-axis:#77756f;--cds-surface-popover:#2f2e2b;',
    '--cds-border:#3a3936;--cds-text-secondary:#a6a49d;color-scheme:dark}}',
    'html,body{margin:0;background:var(--color-bg);color:var(--color-fg)}',
    '#dash-root{padding:var(--cds-pad-lg) 16px;box-sizing:border-box}',
    '.dash-skeleton{min-height:3rem;background:var(--cds-chart-grid);border-radius:var(--cds-radius)}',
    '.lx-export-tlp{max-width:1180px;margin:0 auto var(--cds-gap-sm);font:600 12px var(--font-anthropic-sans);',
    'letter-spacing:.04em;color:var(--color-fg-muted)}',
    '.lx-export-tools{max-width:1180px;margin:var(--cds-gap-md) auto 0;font:13px var(--font-anthropic-sans)}',
    '@media print{.lx-tabs,.lx-btn,.lx-search,.lx-toggle,.lx-export-tools{display:none}.lx-page{display:block!important}',
    '.lx-page[hidden]{display:block!important}.lx-scroll{max-height:none;overflow:visible}}'
  ].join('');
  var style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);

  /* ---------- 2. a small D3 stand-in (only what the template calls) ---------- */
  function miniD3() {
    var SVG_NS = 'http://www.w3.org/2000/svg';
    var SVG_TAGS = { svg: 1, g: 1, line: 1, text: 1, rect: 1, circle: 1, path: 1, title: 1, polygon: 1 };
    function Sel(nodes) { this.nodes = nodes; }
    Sel.prototype.append = function (tag) {
      return new Sel(this.nodes.map(function (n) {
        var inSvg = SVG_TAGS[tag] && (tag === 'svg' || n.namespaceURI === SVG_NS);
        var el = inSvg ? document.createElementNS(SVG_NS, tag) : document.createElement(tag);
        n.appendChild(el);
        return el;
      }));
    };
    Sel.prototype.attr = function (k, v) { this.nodes.forEach(function (n) { n.setAttribute(k, v); }); return this; };
    Sel.prototype.style = function (k, v) { this.nodes.forEach(function (n) { n.style.setProperty(k, v); }); return this; };
    Sel.prototype.text = function (v) { this.nodes.forEach(function (n) { n.textContent = v; }); return this; };
    Sel.prototype.on = function (ev, fn) { this.nodes.forEach(function (n) { n.addEventListener(ev, fn); }); return this; };
    Sel.prototype.node = function () { return this.nodes[0]; };
    var num = function (a, f) { return a.map(f || function (x) { return x; }).filter(function (x) { return x != null && !isNaN(x); }); };
    return {
      select: function (el) { return new Sel([typeof el === 'string' ? document.querySelector(el) : el]); },
      max: function (a, f) { var v = num(a, f); return v.length ? Math.max.apply(null, v) : undefined; },
      min: function (a, f) { var v = num(a, f); return v.length ? Math.min.apply(null, v) : undefined; },
      rollup: function (a, reduce, key) {
        var groups = new Map();
        a.forEach(function (x) { var k = key(x); if (!groups.has(k)) groups.set(k, []); groups.get(k).push(x); });
        var out = new Map(); groups.forEach(function (v, k) { out.set(k, reduce(v)); });
        return out;
      },
      format: function (spec) {
        var dec = /\.(\d)f/.exec(spec); var d = dec ? Number(dec[1]) : 0;
        return function (v) {
          return Number(v).toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d, useGrouping: spec.indexOf(',') === 0 });
        };
      },
      scaleLinear: function (domain, range) {
        var d0 = domain[0], d1 = domain[1], r0 = range[0], r1 = range[1];
        return function (x) { return d1 === d0 ? r0 : r0 + (x - d0) * (r1 - r0) / (d1 - d0); };
      },
      pointer: function (event, el) {
        var r = el.getBoundingClientRect();
        return [event.clientX - r.left, event.clientY - r.top];
      }
    };
  }

  /* ---------- 3. the Dashboard runtime ---------- */
  var raw = [];
  try { raw = JSON.parse(document.getElementById('tracker-data').textContent); } catch (e) { console.error('No tracker data', e); }
  var calcs = {}, draws = {}, dataCbs = [], cache = {}, ready = false;
  function compute(id) {
    if (Object.prototype.hasOwnProperty.call(cache, id)) return cache[id];
    if (id === 'tracker') return (cache[id] = raw);
    var c = calcs[id];
    if (!c) return undefined;
    return (cache[id] = c.fn.apply(null, (c.inputs || []).map(compute)));
  }
  function run(name) {
    var fn = draws[name];
    if (!fn) return;
    document.querySelectorAll('[data-draw="' + name + '"]').forEach(function (el) {
      try { fn(el); } catch (e) { console.error('draw ' + name + ' failed', e); }
      el.removeAttribute('data-dash-source-state');
    });
  }
  window.dash = {
    colors: ['#2a78d6', '#d97706', '#7c5cc4', '#2e9e6b', '#c2410c', '#0e9aa7', '#a23b72', '#5f6b7a'],
    calc: function (name, def) { calcs[name] = def; cache = {}; },
    data: function (id) {
      try {
        var d = compute(id);
        return d === undefined ? { status: 'missing', data: null } : { status: 'ok', data: d };
      } catch (e) { console.error('calc ' + id + ' failed', e); return { status: 'error', data: null }; }
    },
    draw: function (name, fn) { if (fn) { draws[name] = fn; if (ready) run(name); } else if (ready) run(name); },
    onData: function (cb) { dataCbs.push(cb); if (ready) cb(); },
    setLink: function (id) { try { history.replaceState(null, '', '#' + id); } catch (e) { /* file:// may refuse */ } }
  };

  function start() {
    if (!window.d3) window.d3 = miniD3();
    ready = true;
    dataCbs.forEach(function (cb) { try { cb(); } catch (e) { console.error(e); } });
    Object.keys(draws).forEach(run);
    var tools = document.createElement('p');
    tools.className = 'lx-export-tools';
    var a = document.createElement('a');
    a.textContent = 'Download the attack tracker rows (JSON)';
    a.href = URL.createObjectURL(new Blob([JSON.stringify(raw, null, 1)], { type: 'application/json' }));
    a.download = 'tracker-rows.json';
    tools.appendChild(a);
    (document.getElementById('dash-root') || document.body).appendChild(tools);
    var t;
    window.addEventListener('resize', function () { clearTimeout(t); t = setTimeout(function () { run('lanes'); }, 150); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else setTimeout(start, 0);
})();
