"use strict";

(() => {
  const chart = document.getElementById("benchmark-chart");
  const search = document.getElementById("research-search");
  const cards = [...document.querySelectorAll(".research-card")];
  const empty = document.getElementById("research-empty");
  const chips = [...document.querySelectorAll(".filter-chip")];
  let activeFilter = "all";

  function renderChart(rows) {
    if (!rows.length) {
      chart.innerHTML = '<p class="chart-loading">No rows are available in the curated snapshot.</p>';
      return;
    }
    const max = Math.max(...rows.map((row) => Number(row.median_score_samples_per_min)));
    chart.innerHTML = rows.map((row) => {
      const score = Number(row.median_score_samples_per_min);
      const width = (score / max) * 100;
      const label = row.device_name.replace("NVIDIA GeForce ", "");
      return `<div class="benchmark-row"><span class="benchmark-device" title="${row.device_name}">${label}</span><span class="benchmark-track"><span class="benchmark-fill" style="width:${width.toFixed(2)}%"></span></span><span class="benchmark-value">${score.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span><span class="benchmark-count">n=${Number(row.benchmark_count).toLocaleString("en-US")}</span></div>`;
    }).join("");
  }

  function csvRows(csv) {
    const lines = csv.trim().split(/\r?\n/);
    const headers = lines.shift().split(",");
    return lines.map((line) => Object.fromEntries(line.split(",").map((value, index) => [headers[index], value])));
  }

  function filterCards() {
    const query = (search.value || "").trim().toLowerCase();
    let shown = 0;
    cards.forEach((card) => {
      const visible = (activeFilter === "all" || card.dataset.category === activeFilter) &&
        (!query || `${card.dataset.search} ${card.textContent}`.toLowerCase().includes(query));
      card.hidden = !visible;
      if (visible) shown += 1;
    });
    empty.hidden = shown !== 0;
  }

  if (chart) {
    fetch("data/blender-4.4.0-optix-gpu.csv")
      .then((response) => { if (!response.ok) throw new Error("Benchmark snapshot unavailable"); return response.text(); })
      .then((csv) => renderChart(csvRows(csv)))
      .catch(() => { chart.innerHTML = '<p class="chart-loading">Chart data could not be loaded. Download the <a href="data/blender-4.4.0-optix-gpu.csv">source snapshot</a>.</p>'; });
  }
  if (search) search.addEventListener("input", filterCards);
  chips.forEach((chip) => chip.addEventListener("click", () => {
    activeFilter = chip.dataset.filter;
    chips.forEach((item) => { const selected = item === chip; item.classList.toggle("is-active", selected); item.setAttribute("aria-pressed", String(selected)); });
    filterCards();
  }));
})();
