// Runtime smoke test for HTTP and local-file chart paths using Node built-ins.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = __dirname;
const appSource = fs.readFileSync(path.join(root, 'site.js'), 'utf8');
const fallbackSource = fs.readFileSync(path.join(root, 'data', 'telemetry-fallback.js'), 'utf8');

function createPage(networkAllowed) {
  const handlers = new Map();
  let latestArc = null;
  let drawCount = 0;
  const buttons = ['mixed', 'idle', 'both'].map(capture => ({
    dataset: { capture },
    classList: { toggle() {} },
    addEventListener(name, callback) { handlers.set(`button:${capture}:${name}`, callback); },
  }));
  const context2d = {
    setTransform() {}, clearRect() {}, beginPath() {}, moveTo() {}, lineTo() {}, stroke() {}, fillText() {}, fill() {},
    arc(x, y) { latestArc = { x, y }; drawCount++; },
  };
  const canvas = {
    clientWidth: 720, clientHeight: 310, width: 0, height: 0, attrs: {},
    getBoundingClientRect: () => ({ width: 720, height: 310, left: 0, top: 0 }),
    getContext: () => context2d,
    setAttribute(name, value) { this.attrs[name] = value; },
    addEventListener(name, callback) { handlers.set(`canvas:${name}`, callback); },
  };
  const metric = { value: 'temperature_c', addEventListener(name, callback) { handlers.set(`metric:${name}`, callback); } };
  const summary = { textContent: '' };
  const tooltip = { hidden: true, textContent: '', style: {} };
  const unit = { textContent: '' };
  const document = {
    querySelector(selector) {
      return ({ '#telemetry-chart': canvas, '#metric-select': metric, '#chart-summary': summary, '#chart-tooltip': tooltip, '#chart-unit': unit })[selector] ?? null;
    },
    querySelectorAll(selector) { return selector === '.capture-button' ? buttons : []; },
  };
  const fetch = async file => {
    if (!networkAllowed) throw new TypeError('fetch blocked by file origin');
    return { ok: true, text: async () => fs.readFileSync(path.join(root, file), 'utf8') };
  };
  const window = { devicePixelRatio: 1, addEventListener() {} };
  const runtime = { document, fetch, window, Intl, Number, Math, Date, String, Object, Promise };
  vm.runInNewContext(fallbackSource, runtime);
  vm.runInNewContext(appSource, runtime);
  return { handlers, buttons, metric, summary, tooltip, latest: () => latestArc, count: () => drawCount };
}

async function exercise(mode, networkAllowed) {
  const page = createPage(networkAllowed);
  await new Promise(resolve => setImmediate(resolve));
  assert.match(page.summary.textContent, /Mixed trial.*64 °C/);
  assert.match(page.summary.textContent, /59 samples/);
  assert.ok(page.count() > 0, `${mode}: chart should draw the measured samples`);
  if (mode === 'local-file') assert.match(page.summary.textContent, /source-matched local fallback/);

  page.metric.value = 'memory_used_mib';
  page.handlers.get('metric:change')();
  assert.match(page.summary.textContent, /VRAM used.*11,571 MiB/);
  page.handlers.get('button:both:click')();
  assert.match(page.summary.textContent, /Mixed trial.*Idle baseline/);
  page.handlers.get('canvas:focus')();
  const firstKeyboardSample = page.tooltip.textContent;
  page.handlers.get('canvas:keydown')({ key: 'ArrowRight', preventDefault() {} });
  assert.notEqual(page.tooltip.textContent, firstKeyboardSample, `${mode}: arrow key should advance to another sample`);
  const point = page.latest();
  page.handlers.get('canvas:pointermove')({ clientX: point.x, clientY: point.y });
  assert.equal(page.tooltip.hidden, false, `${mode}: recorded sample tooltip should appear`);
  assert.match(page.tooltip.textContent, /UTC/);
  page.handlers.get('button:idle:click')();
  assert.match(page.summary.textContent, /Idle baseline.*1,815 MiB/);
}

(async () => {
  await exercise('HTTP', true);
  await exercise('local-file', false);
  console.log('PASS: HTTP and file-origin chart paths load the same 118 CSV-derived samples; drawing, capture/metric controls, and UTC sample tooltip work.');
})().catch(error => { console.error(error); process.exitCode = 1; });
