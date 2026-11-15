(() => {
  const canvas = document.querySelector('#telemetry-chart');
  if (!canvas) return;

  const sources = { idle: 'data/idle.csv', mixed: 'data/mixed-comfyui.csv' };
  const series = {};
  const metricSelect = document.querySelector('#metric-select');
  const summary = document.querySelector('#chart-summary');
  const tooltip = document.querySelector('#chart-tooltip');
  const unitLabel = document.querySelector('#chart-unit');
  const context = canvas.getContext('2d');
  let capture = 'mixed';
  let activePoints = [];
  let fallbackMode = false;
  let keyboardPointIndex = -1;

  const metricMeta = {
    temperature_c: { label: 'Temperature', unit: '°C', color: '#59aeff' },
    utilization_pct: { label: 'GPU utilization', unit: '%', color: '#59aeff' },
    memory_used_mib: { label: 'VRAM used', unit: 'MiB', color: '#59aeff' },
    power_w: { label: 'GPU-reported power', unit: 'W', color: '#59aeff' },
  };

  function parseSampleRows(rows) {
    return rows.map(row => ({
      time: Date.parse(row.timestamp_utc),
      timestamp: row.timestamp_utc,
      temperature_c: Number(row.temperature_c),
      utilization_pct: Number(row.utilization_pct),
      memory_used_mib: Number(row.memory_used_mib),
      power_w: Number(row.power_w),
    })).filter(row => Number.isFinite(row.time));
  }

  function parseCsv(text) {
    const rows = text.replace(/^\uFEFF/, '').trim().split(/\r?\n/);
    const headers = rows.shift().split(',').map(x => x.replace(/^"|"$/g, ''));
    const values = rows.map(line => {
      const values = line.replace(/^"|"$/g, '').split('","').map(v => v.replace(/""/g, '"'));
      return Object.fromEntries(headers.map((key, i) => [key, values[i]]));
    });
    return parseSampleRows(values);
  }

  function fmt(value) {
    return new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(value);
  }

  function resizeCanvas() {
    const box = canvas.getBoundingClientRect();
    if (!box.width || !box.height) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(box.width * dpr);
    canvas.height = Math.round(box.height * dpr);
    context.setTransform(dpr, 0, 0, dpr, 0, 0);
    draw();
  }

  function draw() {
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    if (!width || !height || !Object.keys(series).length) return;
    const metric = metricSelect.value;
    const meta = metricMeta[metric];
    const shown = capture === 'both' ? ['mixed', 'idle'] : [capture];
    const plotted = shown.flatMap(key => (series[key] || []).map(row => ({ ...row, capture: key, value: row[metric] })));
    if (!plotted.length) return;
    const maxElapsed = Math.max(...shown.map(key => (series[key]?.at(-1)?.time ?? 0) - (series[key]?.[0]?.time ?? 0)), 1);
    let low = Math.min(...plotted.map(p => p.value));
    let high = Math.max(...plotted.map(p => p.value));
    if (low === high) high = low + 1;
    const margin = { top: 20, right: 22, bottom: 39, left: 56 };
    const plotWidth = width - margin.left - margin.right;
    const plotHeight = height - margin.top - margin.bottom;
    const yPad = Math.max((high - low) * 0.12, 1);
    low -= yPad;
    high += yPad;
    context.clearRect(0, 0, width, height);
    context.font = '10px "DM Mono", Consolas, monospace';
    context.lineWidth = 1;
    context.strokeStyle = '#233243';
    context.fillStyle = '#8192a4';
    context.textAlign = 'right';
    context.textBaseline = 'middle';
    for (let tick = 0; tick <= 4; tick++) {
      const y = margin.top + plotHeight * tick / 4;
      const value = high - (high - low) * tick / 4;
      context.beginPath(); context.moveTo(margin.left, y); context.lineTo(width - margin.right, y); context.stroke();
      context.fillText(fmt(value), margin.left - 8, y);
    }
    context.textAlign = 'center';
    context.textBaseline = 'top';
    for (let tick = 0; tick <= 4; tick++) {
      const elapsed = maxElapsed * tick / 4;
      const x = margin.left + plotWidth * tick / 4;
      context.fillText(`${Math.round(elapsed / 60)}:${String(Math.round(elapsed % 60)).padStart(2, '0')}`, x, height - margin.bottom + 11);
    }
    context.fillStyle = '#73869a';
    context.font = '9px "DM Mono", Consolas, monospace';
    context.fillText('ELAPSED TIME · MM:SS', margin.left + plotWidth / 2, height - 12);
    activePoints = [];
    for (const key of shown) {
      const rows = series[key] || [];
      if (!rows.length) continue;
      const color = key === 'mixed' ? '#59aeff' : '#a7b3c0';
      const origin = rows[0].time;
      context.beginPath();
      context.strokeStyle = color;
      context.lineWidth = key === capture || capture === 'both' ? 2 : 1.6;
      rows.forEach((row, index) => {
        const x = margin.left + ((row.time - origin) / maxElapsed) * plotWidth;
        const y = margin.top + (1 - (row[metric] - low) / (high - low)) * plotHeight;
        if (index === 0) context.moveTo(x, y); else context.lineTo(x, y);
        activePoints.push({ x, y, row, value: row[metric], capture: key });
      });
      context.stroke();
      rows.forEach(row => {
        const x = margin.left + ((row.time - origin) / maxElapsed) * plotWidth;
        const y = margin.top + (1 - (row[metric] - low) / (high - low)) * plotHeight;
        context.beginPath(); context.fillStyle = color; context.arc(x, y, 2, 0, Math.PI * 2); context.fill();
      });
    }
    const all = plotted.map(p => p.value);
    const first = shown.includes('mixed') ? 'Mixed trial' : 'Idle baseline';
    const ranges = shown.map(key => {
      const values = (series[key] || []).map(r => r[metric]);
      return `${key === 'mixed' ? 'Mixed trial' : 'Idle baseline'} ${fmt(Math.min(...values))}–${fmt(Math.max(...values))} ${meta.unit} · ${values.length} samples`;
    });
    summary.textContent = `${first} · ${meta.label}: ${fmt(Math.min(...all))}–${fmt(Math.max(...all))} ${meta.unit} · ${ranges.join(' | ')}${fallbackMode ? ' · source-matched local fallback' : ''}`;
    unitLabel.textContent = `${meta.label.toUpperCase()} / ${meta.unit}`;
    canvas.setAttribute('aria-label', `${meta.label} over elapsed time. ${ranges.join('. ')}. Use left and right arrow keys to inspect individual samples; the full measurement data can be downloaded as CSV.`);
  }

  function showTooltip(point) {
    if (!point) return;
    const rect = canvas.getBoundingClientRect();
    const nearest = point;
    const meta = metricMeta[metricSelect.value];
    const label = nearest.capture === 'mixed' ? 'Mixed trial' : 'Idle baseline';
    const stamp = nearest.row.timestamp.replace('T', ' ').replace('Z', ' UTC');
    tooltip.textContent = `${label} · ${meta.label}: ${fmt(nearest.value)} ${meta.unit} · ${stamp}`;
    tooltip.hidden = false;
    const left = Math.max(7, Math.min(rect.width - 205, nearest.x + 12));
    const top = Math.max(7, Math.min(rect.height - 64, nearest.y - 38));
    tooltip.style.left = `${left}px`;
    tooltip.style.top = `${top}px`;
  }

  function showPoint(event) {
    if (!activePoints.length) return;
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    let nearest = null;
    let distance = 18;
    for (const point of activePoints) {
      const d = Math.hypot(point.x - x, point.y - y);
      if (d < distance) { nearest = point; distance = d; }
    }
    if (!nearest) { tooltip.hidden = true; return; }
    showTooltip(nearest);
  }

  async function load() {
    try {
      try {
        await Promise.all(Object.entries(sources).map(async ([key, path]) => {
          const response = await fetch(path);
          if (!response.ok) throw new Error(`Could not load ${path} (${response.status})`);
          series[key] = parseCsv(await response.text());
          if (series[key].length !== 59) throw new Error(`${path}: expected 59 preserved samples; found ${series[key].length}`);
        }));
      } catch (fetchError) {
        const bundled = window.KTT_TELEMETRY_DATA;
        if (!bundled?.idle || !bundled?.mixed) throw fetchError;
        series.idle = parseSampleRows(bundled.idle);
        series.mixed = parseSampleRows(bundled.mixed);
        if (series.idle.length !== 59 || series.mixed.length !== 59) throw new Error('Bundled fallback does not contain both complete 59-sample captures.');
        fallbackMode = true;
      }
      resizeCanvas();
    } catch (error) {
      summary.textContent = `Interactive data unavailable: ${error.message}. Use the CSV downloads and static charts in the report.`;
      canvas.setAttribute('aria-label', 'Interactive chart data could not be loaded. Static report charts and CSV downloads are available.');
    }
  }

  document.querySelectorAll('.capture-button').forEach(button => {
    button.addEventListener('click', () => {
      capture = button.dataset.capture;
      document.querySelectorAll('.capture-button').forEach(item => item.classList.toggle('active', item === button));
      draw();
      tooltip.hidden = true;
    });
  });
  metricSelect.addEventListener('change', () => { draw(); tooltip.hidden = true; });
  canvas.addEventListener('pointermove', showPoint);
  canvas.addEventListener('pointerleave', () => { tooltip.hidden = true; });
  canvas.addEventListener('focus', () => {
    keyboardPointIndex = 0;
    showTooltip(activePoints[keyboardPointIndex]);
  });
  canvas.addEventListener('keydown', event => {
    if (!activePoints.length || !['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
    event.preventDefault();
    keyboardPointIndex = Math.max(0, Math.min(activePoints.length - 1, keyboardPointIndex + (event.key === 'ArrowRight' ? 1 : -1)));
    showTooltip(activePoints[keyboardPointIndex]);
  });
  window.addEventListener('resize', resizeCanvas, { passive: true });
  load();
})();
