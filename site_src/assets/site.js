const FEEDBACK_LIMIT = 500;
const DEFAULT_ISSUE_URL = "https://github.com/ScikitLin/stock-analysis-site/issues/new";
const TW_INSIGHT_DEFAULT = "2317";
const TW_METRICS = {
  score: { label: "Research priority", unit: "", decimals: 1 },
  valuation: { label: "Valuation asymmetry", unit: "", decimals: 1 },
  growth3m: { label: "3M revenue YoY", unit: "%", decimals: 1 },
  rs60: { label: "60D relative strength", unit: "%", decimals: 1 },
  quality: { label: "Quality cash flow", unit: "", decimals: 1 },
  liquidity: { label: "Liquidity flow", unit: "", decimals: 1 },
  theme: { label: "Industry theme", unit: "", decimals: 1 },
  risk: { label: "Risk penalty", unit: "", decimals: 1 },
  ret20: { label: "20D return", unit: "%", decimals: 1 },
  ret60: { label: "60D return", unit: "%", decimals: 1 },
  rangePos: { label: "52W range position", unit: "%", decimals: 1 },
  pe: { label: "P/E", unit: "x", decimals: 1 },
  pb: { label: "P/B", unit: "x", decimals: 1 },
  divYield: { label: "Dividend yield", unit: "%", decimals: 1 }
};
const INDUSTRY_PALETTE = ["#27745f", "#326f87", "#9a7433", "#5a7a4d", "#7d6a9d", "#a55353", "#40847e", "#806f3a"];

const state = {
  reports: [],
  metadata: {},
  query: "",
  market: "all",
  type: "all",
  sort: "date-desc",
  tag: "all",
  page: "reports",
  candidates: [],
  selectedTicker: TW_INSIGHT_DEFAULT,
  insightView: "growth"
};

const elements = {
  siteTitle: document.querySelector("#siteTitle"),
  siteDescription: document.querySelector("#siteDescription"),
  disclaimer: document.querySelector("#disclaimer"),
  reportCount: document.querySelector("#reportCount"),
  latestDate: document.querySelector("#latestDate"),
  twCount: document.querySelector("#twCount"),
  usCount: document.querySelector("#usCount"),
  symbolCount: document.querySelector("#symbolCount"),
  typeCount: document.querySelector("#typeCount"),
  sourceFolder: document.querySelector("#sourceFolder"),
  searchInput: document.querySelector("#searchInput"),
  marketFilter: document.querySelector("#marketFilter"),
  marketButtons: document.querySelectorAll("[data-market-button]"),
  typeFilter: document.querySelector("#typeFilter"),
  sortFilter: document.querySelector("#sortFilter"),
  resetButton: document.querySelector("#resetButton"),
  tagList: document.querySelector("#tagList"),
  resultCount: document.querySelector("#resultCount"),
  generatedAt: document.querySelector("#generatedAt"),
  reportGrid: document.querySelector("#reportGrid"),
  emptyState: document.querySelector("#emptyState"),
  feedbackOpen: document.querySelector("#feedbackOpen"),
  feedbackFloating: document.querySelector("#feedbackFloating"),
  feedbackOverlay: document.querySelector("#feedbackOverlay"),
  feedbackPanel: document.querySelector("#feedbackPanel"),
  feedbackClose: document.querySelector("#feedbackClose"),
  feedbackForm: document.querySelector("#feedbackForm"),
  feedbackCategory: document.querySelector("#feedbackCategory"),
  feedbackSubject: document.querySelector("#feedbackSubject"),
  feedbackMessage: document.querySelector("#feedbackMessage"),
  feedbackCounter: document.querySelector("#feedbackCounter"),
  feedbackCopy: document.querySelector("#feedbackCopy"),
  feedbackStatus: document.querySelector("#feedbackStatus"),
  pageLinks: document.querySelectorAll("[data-page-link]"),
  pagePanels: document.querySelectorAll("[data-page-panel]"),
  twInsightsPanel: document.querySelector("#twInsightsPanel"),
  twCandidateDate: document.querySelector("#twCandidateDate"),
  twTickerInput: document.querySelector("#twTickerInput"),
  twTickerList: document.querySelector("#twTickerList"),
  twInsightChart: document.querySelector("#twInsightChart"),
  twStockPanel: document.querySelector("#twStockPanel"),
  insightViewButtons: document.querySelectorAll("[data-insight-view]")
};

function normalize(value) {
  return String(value || "").toLowerCase().trim();
}

function unique(values) {
  return Array.from(new Set(values.filter(Boolean)));
}

function formatDate(value) {
  if (!value) return "未標日期";
  return value;
}

function formatGeneratedAt(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return `更新時間 ${date.toLocaleString("zh-TW", { hour12: false })}`;
}

function createOption(select, value, label) {
  const option = document.createElement("option");
  option.value = value;
  option.textContent = label;
  select.appendChild(option);
}

function buildFilters() {
  const markets = unique(state.reports.map((report) => report.market));
  const types = unique(state.reports.map((report) => report.type));
  const marketLabels = new Map(state.reports.map((report) => [report.market, report.marketLabel]));
  const typeLabels = new Map(state.reports.map((report) => [report.type, report.typeLabel]));

  if (elements.marketFilter) {
    markets.sort().forEach((market) => createOption(elements.marketFilter, market, marketLabels.get(market) || market));
  }
  types.sort().forEach((type) => createOption(elements.typeFilter, type, typeLabels.get(type) || type));
}

function updateStats(metadata) {
  const latest = state.reports.map((report) => report.date).filter(Boolean).sort().at(-1) || "--";
  const symbols = unique(state.reports.flatMap((report) => report.symbols || []));
  const types = unique(state.reports.map((report) => report.type));
  const sourceDir = metadata.sourceDir || metadata.publishedFolder || "published_reports";

  document.title = metadata.siteTitle || "股票研究資料分析庫";
  elements.siteTitle.textContent = metadata.siteTitle || "股票研究資料分析庫";
  elements.siteDescription.textContent = metadata.siteDescription || "以資料完整性、估值情境與風控紀律整理的公開個股研究索引。";
  elements.disclaimer.textContent = metadata.disclaimer || elements.disclaimer.textContent;
  elements.reportCount.textContent = state.reports.length;
  elements.latestDate.textContent = latest;
  elements.twCount.textContent = state.reports.filter((report) => report.market === "tw").length;
  elements.usCount.textContent = state.reports.filter((report) => report.market === "us").length;
  elements.symbolCount.textContent = symbols.length;
  elements.typeCount.textContent = types.length;
  elements.generatedAt.textContent = formatGeneratedAt(metadata.generatedAt);
  elements.sourceFolder.textContent = `${sourceDir.replace(/\/$/, "")}/`;
}

function hydrateCandidates(payload) {
  const columns = payload?.columns || [];
  return (payload?.rows || []).map((row) => {
    const item = {};
    columns.forEach((column, index) => {
      item[column] = row[index];
    });
    return item;
  }).filter((item) => item.ticker && item.name);
}

function median(values) {
  const sorted = values.filter((value) => Number.isFinite(value)).sort((a, b) => a - b);
  if (!sorted.length) return null;
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
}

function quantile(values, ratio) {
  const sorted = values.filter((value) => Number.isFinite(value)).sort((a, b) => a - b);
  if (!sorted.length) return null;
  const position = (sorted.length - 1) * ratio;
  const base = Math.floor(position);
  const rest = position - base;
  const next = sorted[base + 1];
  return next === undefined ? sorted[base] : sorted[base] + rest * (next - sorted[base]);
}

function axisExtent(values, low = 0.04, high = 0.96) {
  let min = quantile(values, low);
  let max = quantile(values, high);
  if (!Number.isFinite(min) || !Number.isFinite(max)) return [0, 1];
  if (min === max) {
    min -= 1;
    max += 1;
  }
  const pad = (max - min) * 0.08;
  return [min - pad, max + pad];
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function scale(value, domain, range) {
  const [d0, d1] = domain;
  const [r0, r1] = range;
  if (!Number.isFinite(value) || d0 === d1) return (r0 + r1) / 2;
  return r0 + ((clamp(value, d0, d1) - d0) / (d1 - d0)) * (r1 - r0);
}

function formatMetric(value, metricKey) {
  if (!Number.isFinite(value)) return "--";
  const metric = TW_METRICS[metricKey] || { unit: "", decimals: 1 };
  const decimals = metric.decimals ?? 1;
  const formatted = value.toLocaleString("zh-TW", {
    maximumFractionDigits: decimals,
    minimumFractionDigits: Math.abs(value) < 10 && decimals ? 1 : 0
  });
  return metric.unit === "x" ? `${formatted}x` : `${formatted}${metric.unit || ""}`;
}

function formatMarketCap(value) {
  if (!Number.isFinite(value)) return "--";
  if (Math.abs(value) >= 1_0000_0000_0000) return `${(value / 1_0000_0000_0000).toFixed(1)} 兆`;
  if (Math.abs(value) >= 1_0000_0000) return `${(value / 1_0000_0000).toFixed(1)} 億`;
  return value.toLocaleString("zh-TW", { maximumFractionDigits: 0 });
}

function selectedCandidate() {
  return state.candidates.find((item) => item.ticker === state.selectedTicker) || state.candidates[0] || null;
}

function findCandidate(query) {
  const value = normalize(query);
  if (!value) return null;
  return state.candidates.find((item) => normalize(item.ticker) === value)
    || state.candidates.find((item) => normalize(item.name) === value)
    || state.candidates.find((item) => normalize(`${item.ticker} ${item.name}`).includes(value));
}

function industryColor(industry) {
  const industries = unique(state.candidates.map((item) => item.industry)).sort((a, b) => a.localeCompare(b, "zh-Hant"));
  const index = industries.indexOf(industry);
  return INDUSTRY_PALETTE[(index < 0 ? 0 : index) % INDUSTRY_PALETTE.length];
}

function renderTags() {
  const tagCounts = new Map();
  state.reports.forEach((report) => {
    (report.tags || []).forEach((tag) => tagCounts.set(tag, (tagCounts.get(tag) || 0) + 1));
  });

  const tags = Array.from(tagCounts.entries()).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0], "zh-Hant"));
  elements.tagList.replaceChildren();

  const allButton = document.createElement("button");
  allButton.type = "button";
  allButton.className = `tag-button${state.tag === "all" ? " is-active" : ""}`;
  allButton.textContent = "全部";
  allButton.addEventListener("click", () => {
    state.tag = "all";
    render();
  });
  elements.tagList.appendChild(allButton);

  tags.forEach(([tag, count]) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `tag-button${state.tag === tag ? " is-active" : ""}`;
    button.textContent = `${tag} ${count}`;
    button.addEventListener("click", () => {
      state.tag = state.tag === tag ? "all" : tag;
      render();
    });
    elements.tagList.appendChild(button);
  });
}

function reportMatches(report) {
  const query = normalize(state.query);
  const haystack = normalize([
    report.title,
    report.summary,
    report.marketLabel,
    report.typeLabel,
    report.sourceFile,
    ...(report.symbols || []),
    ...(report.symbolNames || []).map((item) => `${item.symbol} ${item.name}`),
    ...(report.tags || [])
  ].join(" "));

  if (state.market !== "all" && report.market !== state.market) return false;
  if (state.type !== "all" && report.type !== state.type) return false;
  if (state.tag !== "all" && !(report.tags || []).includes(state.tag)) return false;
  if (query && !haystack.includes(query)) return false;
  return true;
}

function sortReports(reports) {
  return [...reports].sort((a, b) => {
    if (state.sort === "date-asc") return (a.date || "").localeCompare(b.date || "") || a.title.localeCompare(b.title, "zh-Hant");
    if (state.sort === "title-asc") return a.title.localeCompare(b.title, "zh-Hant");
    return (b.date || "").localeCompare(a.date || "") || a.title.localeCompare(b.title, "zh-Hant");
  });
}

function renderSymbolPills(report) {
  const symbols = (report.symbolNames && report.symbolNames.length)
    ? report.symbolNames
    : (report.symbols || []).map((symbol) => ({ symbol, name: "" }));

  return symbols.slice(0, 12).map((item) => {
    const label = item.name ? `${item.symbol} ${item.name}` : item.symbol;
    return `<span class="symbol-pill">${escapeHtml(label)}</span>`;
  }).join("");
}

function renderReportCard(report) {
  const card = document.createElement("a");
  card.className = "report-card";
  card.href = report.url;
  card.innerHTML = `
    <div class="card-top">
      <span class="badge ${escapeHtml(report.market)}">${escapeHtml(report.marketLabel)}</span>
      <time>${escapeHtml(formatDate(report.date))}</time>
    </div>
    <h2>${escapeHtml(report.title)}</h2>
    <p class="summary">${escapeHtml(report.summary)}</p>
    <div class="symbol-list">${renderSymbolPills(report)}</div>
    <div class="card-tags">${(report.tags || []).slice(0, 6).map((tag) => `<span class="mini-tag">${escapeHtml(tag)}</span>`).join("")}</div>
    <div class="card-bottom">
      <p class="card-source">${escapeHtml(report.sourceFile)}</p>
      <span class="badge">${escapeHtml(report.typeLabel)}</span>
    </div>
  `;
  return card;
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeAttribute(value) {
  return escapeHtml(value).replaceAll("`", "&#096;");
}

function buildTickerList() {
  if (!elements.twTickerList) return;
  const fragment = document.createDocumentFragment();
  state.candidates
    .slice()
    .sort((a, b) => (b.score || 0) - (a.score || 0) || a.ticker.localeCompare(b.ticker, "zh-Hant"))
    .forEach((item) => {
      const option = document.createElement("option");
      option.value = `${item.ticker} ${item.name}`;
      option.label = `${item.industry} · ${formatMetric(item.score, "score")}`;
      fragment.appendChild(option);
    });
  elements.twTickerList.replaceChildren(fragment);
}

function initializeCandidates() {
  state.candidates = hydrateCandidates(window.TW_CANDIDATES || {});
  if (!state.candidates.find((item) => item.ticker === state.selectedTicker)) {
    state.selectedTicker = state.candidates.slice().sort((a, b) => (b.score || 0) - (a.score || 0))[0]?.ticker || "";
  }
  if (elements.twCandidateDate) {
    elements.twCandidateDate.textContent = window.TW_CANDIDATES?.generatedAt || "--";
  }
  buildTickerList();
}

function scoreColor(value) {
  const ratio = clamp(((value || 0) - 30) / 55, 0, 1);
  const hue = 38 + ratio * 112;
  const light = 40 - ratio * 8;
  return `hsl(${hue} 44% ${light}%)`;
}

function circleRadius(item, capDomain) {
  const value = Math.log10(Math.max(item.marketCap || 1, 1));
  return scale(value, capDomain, [3.4, 10]);
}

function renderAxisTicks(domain, range, vertical = false) {
  return Array.from({ length: 5 }, (_, index) => {
    const value = domain[0] + ((domain[1] - domain[0]) * index) / 4;
    const position = scale(value, domain, range);
    if (vertical) {
      return `
        <g class="axis-tick">
          <line x1="78" x2="814" y1="${position}" y2="${position}"></line>
          <text x="66" y="${position + 4}" text-anchor="end">${formatMetric(value, "")}</text>
        </g>
      `;
    }
    return `
      <g class="axis-tick">
        <line x1="${position}" x2="${position}" y1="54" y2="420"></line>
        <text x="${position}" y="448" text-anchor="middle">${formatMetric(value, "")}</text>
      </g>
    `;
  }).join("");
}

function scatterConfig() {
  if (state.insightView === "momentum") {
    return {
      title: "Momentum x Quality Field",
      x: "rs60",
      y: "quality",
      xLabel: "60D relative strength percentile",
      yLabel: "Quality cash-flow score"
    };
  }
  return {
    title: "Growth x Valuation Field",
    x: "growth3m",
    y: "valuation",
    xLabel: "3M revenue YoY",
    yLabel: "Valuation asymmetry score"
  };
}

function renderScatterInsight() {
  const config = scatterConfig();
  const rows = state.candidates.filter((item) => Number.isFinite(item[config.x]) && Number.isFinite(item[config.y]));
  const selected = selectedCandidate();
  const xDomain = axisExtent(rows.map((item) => item[config.x]), 0.04, 0.96);
  const yDomain = axisExtent(rows.map((item) => item[config.y]), 0.04, 0.96);
  const capValues = rows.map((item) => Math.log10(Math.max(item.marketCap || 1, 1)));
  const capDomain = axisExtent(capValues, 0.05, 0.95);
  const selectedPoint = selected && Number.isFinite(selected[config.x]) && Number.isFinite(selected[config.y])
    ? {
      x: scale(selected[config.x], xDomain, [78, 814]),
      y: scale(selected[config.y], yDomain, [420, 54])
    }
    : null;

  elements.twInsightChart.innerHTML = `
    <svg class="insight-svg" viewBox="0 0 860 500" aria-label="${escapeAttribute(config.title)}">
      <rect class="plot-bg" x="78" y="54" width="736" height="366"></rect>
      <text class="chart-title" x="78" y="28">${escapeHtml(config.title)}</text>
      <text class="chart-subtitle" x="78" y="47">All candidates · bubble size by market cap · color by research priority</text>
      ${renderAxisTicks(xDomain, [78, 814])}
      ${renderAxisTicks(yDomain, [420, 54], true)}
      <line class="axis-line" x1="78" x2="814" y1="420" y2="420"></line>
      <line class="axis-line" x1="78" x2="78" y1="54" y2="420"></line>
      <text class="axis-label" x="446" y="486" text-anchor="middle">${escapeHtml(config.xLabel)}</text>
      <text class="axis-label" x="18" y="237" transform="rotate(-90 18 237)" text-anchor="middle">${escapeHtml(config.yLabel)}</text>
      <g class="points">
        ${rows.map((item) => {
          const isSelected = selected?.ticker === item.ticker;
          const cx = scale(item[config.x], xDomain, [78, 814]);
          const cy = scale(item[config.y], yDomain, [420, 54]);
          return `
            <circle class="insight-point${isSelected ? " is-selected" : ""}" data-ticker="${escapeAttribute(item.ticker)}"
              cx="${cx.toFixed(2)}" cy="${cy.toFixed(2)}" r="${circleRadius(item, capDomain).toFixed(2)}"
              fill="${scoreColor(item.score)}">
              <title>${escapeHtml(`${item.ticker} ${item.name} · ${item.industry} · ${TW_METRICS[config.x].label}: ${formatMetric(item[config.x], config.x)} · ${TW_METRICS[config.y].label}: ${formatMetric(item[config.y], config.y)}`)}</title>
            </circle>
          `;
        }).join("")}
      </g>
      ${selectedPoint ? `
        <g class="selected-label">
          <line x1="${selectedPoint.x}" y1="${selectedPoint.y}" x2="${Math.min(790, selectedPoint.x + 54)}" y2="${Math.max(68, selectedPoint.y - 34)}"></line>
          <rect x="${Math.min(650, selectedPoint.x + 58)}" y="${Math.max(55, selectedPoint.y - 51)}" width="145" height="38"></rect>
          <text x="${Math.min(662, selectedPoint.x + 68)}" y="${Math.max(78, selectedPoint.y - 27)}">${escapeHtml(`${selected.ticker} ${selected.name}`)}</text>
        </g>
      ` : ""}
    </svg>
  `;

  elements.twInsightChart.querySelectorAll("[data-ticker]").forEach((point) => {
    point.addEventListener("click", () => selectCandidate(point.dataset.ticker));
  });
}

function industryAggregates() {
  const groups = new Map();
  state.candidates.forEach((item) => {
    if (!item.industry || item.industry === "未分類") return;
    if (!groups.has(item.industry)) groups.set(item.industry, []);
    groups.get(item.industry).push(item);
  });
  return Array.from(groups.entries()).map(([industry, rows]) => ({
    industry,
    count: rows.length,
    score: median(rows.map((item) => item.score)),
    growth3m: median(rows.map((item) => item.growth3m)),
    valuation: median(rows.map((item) => item.valuation)),
    rs60: median(rows.map((item) => item.rs60)),
    quality: median(rows.map((item) => item.quality)),
    risk: median(rows.map((item) => item.risk))
  })).filter((item) => item.count >= 8);
}

function heatColor(value, domain, metric) {
  if (!Number.isFinite(value)) return "#edf2ef";
  const ratio = clamp((value - domain[0]) / (domain[1] - domain[0] || 1), 0, 1);
  if (metric === "risk") {
    return `hsl(6 42% ${90 - ratio * 38}%)`;
  }
  return `hsl(${145 - ratio * 90} 42% ${90 - ratio * 38}%)`;
}

function renderIndustryHeatmap() {
  const selected = selectedCandidate();
  const metrics = ["score", "growth3m", "valuation", "rs60", "quality", "risk"];
  let rows = industryAggregates()
    .sort((a, b) => (b.score || 0) - (a.score || 0))
    .slice(0, 18);
  if (selected?.industry && selected.industry !== "未分類" && !rows.find((item) => item.industry === selected.industry)) {
    const selectedIndustry = industryAggregates().find((item) => item.industry === selected.industry);
    if (selectedIndustry) rows = rows.slice(0, 17).concat(selectedIndustry);
  }
  const domains = Object.fromEntries(metrics.map((metric) => [metric, axisExtent(rows.map((item) => item[metric]), 0, 1)]));
  const rowHeight = 34;
  const top = 78;
  const left = 168;
  const cellWidth = 98;
  const height = top + rows.length * rowHeight + 42;

  elements.twInsightChart.innerHTML = `
    <svg class="insight-svg heatmap-svg" viewBox="0 0 860 ${height}" aria-label="Industry signal heatmap">
      <text class="chart-title" x="32" y="30">Industry Signal Heatmap</text>
      <text class="chart-subtitle" x="32" y="50">Median signals by industry · selected industry outlined</text>
      ${metrics.map((metric, index) => `
        <text class="heat-head" x="${left + index * cellWidth + cellWidth / 2}" y="72" text-anchor="middle">${escapeHtml(TW_METRICS[metric].label)}</text>
      `).join("")}
      ${rows.map((row, rowIndex) => `
        <g class="${selected?.industry === row.industry ? "heat-row is-selected" : "heat-row"}">
          <text class="heat-label" x="32" y="${top + rowIndex * rowHeight + 22}">${escapeHtml(row.industry)} (${row.count})</text>
          ${metrics.map((metric, metricIndex) => {
            const value = row[metric];
            const x = left + metricIndex * cellWidth;
            const y = top + rowIndex * rowHeight;
            return `
              <rect x="${x}" y="${y}" width="${cellWidth - 6}" height="28" rx="5" fill="${heatColor(value, domains[metric], metric)}"></rect>
              <text class="heat-value" x="${x + (cellWidth - 6) / 2}" y="${y + 18}" text-anchor="middle">${escapeHtml(formatMetric(value, metric))}</text>
            `;
          }).join("")}
        </g>
      `).join("")}
    </svg>
  `;
}

function peerMedian(candidate, metric) {
  const peers = state.candidates.filter((item) => item.industry === candidate.industry && item.ticker !== candidate.ticker);
  return median(peers.map((item) => item[metric]));
}

function compareRange(metric) {
  if (metric === "score") return [0, 100];
  if (metric === "valuation" || metric === "quality") return [0, 20];
  if (metric === "risk") return [0, 24];
  return axisExtent(state.candidates.map((item) => item[metric]), 0.05, 0.95);
}

function renderStockPanel() {
  const candidate = selectedCandidate();
  if (!candidate) {
    elements.twStockPanel.innerHTML = "<p class=\"muted\">No candidate data</p>";
    return;
  }
  const metrics = ["score", "growth3m", "valuation", "rs60", "quality", "risk"];
  elements.twStockPanel.innerHTML = `
    <div class="stock-panel-head">
      <span>${escapeHtml(candidate.industry)}</span>
      <h3>${escapeHtml(candidate.ticker)} ${escapeHtml(candidate.name)}</h3>
      <p>${escapeHtml(candidate.tier || "Candidate")}</p>
    </div>
    <div class="stock-stat-grid">
      <div><span>Close</span><strong>${formatMetric(candidate.close, "")}</strong></div>
      <div><span>Market cap</span><strong>${formatMarketCap(candidate.marketCap)}</strong></div>
      <div><span>P/E</span><strong>${formatMetric(candidate.pe, "pe")}</strong></div>
      <div><span>P/B</span><strong>${formatMetric(candidate.pb, "pb")}</strong></div>
    </div>
    <div class="compare-list">
      ${metrics.map((metric) => {
        const value = candidate[metric];
        const peer = peerMedian(candidate, metric);
        const domain = compareRange(metric);
        const valuePct = scale(value, domain, [0, 100]);
        const peerPct = Number.isFinite(peer) ? scale(peer, domain, [0, 100]) : null;
        return `
          <div class="compare-item">
            <div>
              <span>${escapeHtml(TW_METRICS[metric].label)}</span>
              <strong>${escapeHtml(formatMetric(value, metric))}</strong>
            </div>
            <div class="compare-track">
              <i style="width:${valuePct.toFixed(1)}%"></i>
              ${peerPct === null ? "" : `<b style="left:${peerPct.toFixed(1)}%" title="Industry median ${escapeAttribute(formatMetric(peer, metric))}"></b>`}
            </div>
            <small>Industry median ${escapeHtml(formatMetric(peer, metric))}</small>
          </div>
        `;
      }).join("")}
    </div>
  `;
}

function renderTwInsights() {
  if (!elements.twInsightsPanel) return;
  const visible = state.market === "tw" && state.candidates.length > 0;
  elements.twInsightsPanel.hidden = !visible;
  if (!visible) return;

  const candidate = selectedCandidate();
  if (candidate && document.activeElement !== elements.twTickerInput) {
    elements.twTickerInput.value = `${candidate.ticker} ${candidate.name}`;
  }
  elements.insightViewButtons.forEach((button) => {
    button.classList.toggle("is-active", button.dataset.insightView === state.insightView);
  });
  if (state.insightView === "industry") {
    renderIndustryHeatmap();
  } else {
    renderScatterInsight();
  }
  renderStockPanel();
}

function selectCandidate(value) {
  const candidate = typeof value === "string"
    ? state.candidates.find((item) => item.ticker === value) || findCandidate(value)
    : value;
  if (!candidate) return;
  state.selectedTicker = candidate.ticker;
  if (elements.twTickerInput) {
    elements.twTickerInput.value = `${candidate.ticker} ${candidate.name}`;
  }
  renderTwInsights();
}

function render() {
  renderTags();
  updateMarketButtons();
  const filtered = sortReports(state.reports.filter(reportMatches));
  elements.reportGrid.replaceChildren(...filtered.map(renderReportCard));
  elements.emptyState.hidden = filtered.length > 0;
  elements.resultCount.textContent = `${filtered.length} / ${state.reports.length} 份報告`;
  renderTwInsights();
}

function updateMarketButtons() {
  elements.marketButtons.forEach((button) => {
    button.classList.toggle("is-active", button.dataset.marketButton === state.market);
  });
}

function setMarket(market) {
  state.market = ["all", "tw", "us"].includes(market) ? market : "all";
  if (elements.marketFilter) elements.marketFilter.value = state.market;
  render();
}

function bindFilters() {
  elements.searchInput.addEventListener("input", (event) => {
    state.query = event.target.value;
    render();
  });
  elements.marketButtons.forEach((button) => {
    button.addEventListener("click", () => setMarket(button.dataset.marketButton));
  });
  if (elements.marketFilter) {
    elements.marketFilter.addEventListener("change", (event) => setMarket(event.target.value));
  }
  elements.typeFilter.addEventListener("change", (event) => {
    state.type = event.target.value;
    render();
  });
  elements.sortFilter.addEventListener("change", (event) => {
    state.sort = event.target.value;
    render();
  });
  elements.resetButton.addEventListener("click", () => {
    state.query = "";
    state.market = "all";
    state.type = "all";
    state.sort = "date-desc";
    state.tag = "all";
    elements.searchInput.value = "";
    if (elements.marketFilter) elements.marketFilter.value = "all";
    elements.typeFilter.value = "all";
    elements.sortFilter.value = "date-desc";
    render();
  });
}

function bindTwInsights() {
  if (!elements.twInsightsPanel) return;
  elements.insightViewButtons.forEach((button) => {
    button.addEventListener("click", () => {
      state.insightView = button.dataset.insightView || "growth";
      renderTwInsights();
    });
  });
  elements.twTickerInput.addEventListener("change", () => {
    selectCandidate(findCandidate(elements.twTickerInput.value));
  });
  elements.twTickerInput.addEventListener("input", () => {
    const candidate = findCandidate(elements.twTickerInput.value);
    const value = normalize(elements.twTickerInput.value);
    const optionLabel = normalize(`${candidate?.ticker} ${candidate?.name}`);
    if (candidate && (value === normalize(candidate.ticker) || value === normalize(candidate.name) || value === optionLabel)) {
      selectCandidate(candidate);
    }
  });
  elements.twTickerInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      selectCandidate(findCandidate(elements.twTickerInput.value));
    }
  });
}

function setActivePage(page, options = {}) {
  const nextPage = page === "profile" ? "profile" : "reports";
  state.page = nextPage;

  elements.pagePanels.forEach((panel) => {
    const active = panel.dataset.pagePanel === nextPage;
    panel.hidden = !active;
    panel.classList.toggle("is-active", active);
  });

  elements.pageLinks.forEach((link) => {
    const active = link.dataset.pageLink === nextPage;
    link.classList.toggle("is-active", active);
    if (link.getAttribute("role") === "tab") {
      link.setAttribute("aria-selected", active ? "true" : "false");
    }
  });

  if (options.updateHash !== false && window.location.hash !== `#${nextPage}`) {
    history.pushState(null, "", `#${nextPage}`);
  }
  if (options.scroll !== false) {
    document.querySelector("main")?.scrollIntoView({ block: "start" });
  }
}

function bindPageNavigation() {
  elements.pageLinks.forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      setActivePage(link.dataset.pageLink, { scroll: true });
    });
  });

  window.addEventListener("hashchange", () => {
    setActivePage(window.location.hash.replace("#", ""), { updateHash: false, scroll: false });
  });

  setActivePage(window.location.hash.replace("#", ""), { updateHash: false, scroll: false });
}

function setFeedbackOpen(open) {
  elements.feedbackPanel.hidden = !open;
  elements.feedbackOverlay.hidden = !open;
  document.body.classList.toggle("is-locked", open);
  if (open) {
    elements.feedbackMessage.focus();
  }
}

function updateFeedbackCounter() {
  const length = elements.feedbackMessage.value.length;
  elements.feedbackCounter.textContent = `${length} / ${FEEDBACK_LIMIT}`;
  elements.feedbackCounter.style.color = length > FEEDBACK_LIMIT * 0.9 ? "var(--amber)" : "";
}

function buildFeedbackPayload() {
  const category = elements.feedbackCategory.value;
  const subject = elements.feedbackSubject.value.trim();
  const message = elements.feedbackMessage.value.trim();
  const title = `[網站留言] ${subject || category}`;
  const body = [
    `分類：${category}`,
    subject ? `相關報告或股票：${subject}` : "",
    "",
    "留言內容：",
    message,
    "",
    `頁面：${window.location.href}`,
    `時間：${new Date().toISOString()}`
  ].filter((line) => line !== "").join("\n");

  return { title, body, message };
}

async function copyFeedbackBody(body) {
  if (navigator.clipboard && window.isSecureContext) {
    await navigator.clipboard.writeText(body);
    return;
  }
  const helper = document.createElement("textarea");
  helper.value = body;
  helper.setAttribute("readonly", "");
  helper.style.position = "fixed";
  helper.style.left = "-9999px";
  document.body.appendChild(helper);
  helper.select();
  document.execCommand("copy");
  helper.remove();
}

function issueUrl(payload) {
  const base = state.metadata.feedbackIssueUrl || DEFAULT_ISSUE_URL;
  const params = new URLSearchParams({
    title: payload.title,
    body: payload.body
  });
  return `${base}?${params.toString()}`;
}

function bindFeedback() {
  const openButtons = [elements.feedbackOpen, elements.feedbackFloating].filter(Boolean);
  openButtons.forEach((button) => button.addEventListener("click", () => setFeedbackOpen(true)));
  elements.feedbackClose.addEventListener("click", () => setFeedbackOpen(false));
  elements.feedbackOverlay.addEventListener("click", () => setFeedbackOpen(false));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !elements.feedbackPanel.hidden) setFeedbackOpen(false);
  });
  elements.feedbackMessage.addEventListener("input", updateFeedbackCounter);
  elements.feedbackCopy.addEventListener("click", async () => {
    const payload = buildFeedbackPayload();
    if (!payload.message) {
      elements.feedbackStatus.textContent = "請先輸入留言內容。";
      return;
    }
    await copyFeedbackBody(payload.body);
    elements.feedbackStatus.textContent = "已複製留言內容。";
  });
  elements.feedbackForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const payload = buildFeedbackPayload();
    if (!payload.message) {
      elements.feedbackStatus.textContent = "請先輸入留言內容。";
      return;
    }
    window.open(issueUrl(payload), "_blank", "noopener");
    elements.feedbackStatus.textContent = "已開啟 GitHub Issue 草稿。";
  });
  updateFeedbackCounter();
}

async function init() {
  const metadata = window.STOCK_REPORTS || await fetchMetadata();
  state.metadata = metadata;
  state.reports = metadata.reports || [];
  initializeCandidates();
  buildFilters();
  updateStats(metadata);
  bindFilters();
  bindTwInsights();
  bindPageNavigation();
  bindFeedback();
  render();
}

async function fetchMetadata() {
  const response = await fetch("reports.json");
  if (!response.ok) throw new Error(`reports.json ${response.status}`);
  return response.json();
}

init().catch((error) => {
  elements.resultCount.textContent = "報告索引載入失敗";
  elements.emptyState.hidden = false;
  elements.emptyState.querySelector("h2").textContent = "無法載入 reports.json";
  elements.emptyState.querySelector("p").textContent = error.message;
});
