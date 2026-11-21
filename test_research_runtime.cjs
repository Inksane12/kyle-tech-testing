// No-dependency runtime checks for research snapshot rendering and hub filters.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = __dirname;
const source = fs.readFileSync(path.join(root, 'research.js'), 'utf8');
const csv = fs.readFileSync(path.join(root, 'data', 'blender-4.4.0-optix-gpu.csv'), 'utf8');
const handlers = new Map();
const chart = { innerHTML: '' };
const search = { value: '', addEventListener(name, callback) { handlers.set(`search:${name}`, callback); } };
const empty = { hidden: true };
const cards = [
  { dataset: { category: 'gpu', search: 'gpu graphics blender' }, textContent: 'Blender GPU comparison', hidden: false },
  { dataset: { category: 'systems', search: 'mini pc processor' }, textContent: 'Mini PC guide', hidden: false },
  { dataset: { category: 'windows', search: 'windows networking' }, textContent: 'Windows compatibility', hidden: false },
];
const chips = ['all', 'gpu', 'systems', 'windows'].map(filter => ({
  dataset: { filter }, classList: { toggle() {} }, attrs: {},
  setAttribute(name, value) { this.attrs[name] = value; },
  addEventListener(name, callback) { handlers.set(`chip:${filter}:${name}`, callback); },
}));
const document = {
  getElementById(id) { return ({ 'benchmark-chart': chart, 'research-search': search, 'research-empty': empty })[id] ?? null; },
  querySelectorAll(selector) { return selector === '.research-card' ? cards : selector === '.filter-chip' ? chips : []; },
};
const runtime = {
  document,
  fetch: async () => ({ ok: true, text: async () => csv }),
  Number, Math, Intl, Promise, String, Object,
};

vm.runInNewContext(source, runtime);

(async () => {
  await new Promise(resolve => setImmediate(resolve));
  assert.equal((chart.innerHTML.match(/class="benchmark-row"/g) || []).length, 7);
  assert.match(chart.innerHTML, /9,163\.59/);
  assert.match(chart.innerHTML, /n=1,151/);
  handlers.get('chip:gpu:click')();
  assert.equal(cards[0].hidden, false);
  assert.equal(cards[1].hidden, true);
  assert.equal(empty.hidden, true);
  search.value = 'not-a-topic';
  handlers.get('search:input')();
  assert.equal(cards.every(card => card.hidden), true);
  assert.equal(empty.hidden, false);
  console.log('PASS: seven CSV-backed GPU bars render with score/sample count; category and text search filters behave; empty state appears.');
})().catch(error => { console.error(error); process.exitCode = 1; });
