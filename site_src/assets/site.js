const FEEDBACK_LIMIT = 500;
const DEFAULT_ISSUE_URL = "https://github.com/ScikitLin/stock-analysis-site/issues/new";

const state = {
  reports: [],
  metadata: {},
  query: "",
  market: "all",
  type: "all",
  sort: "date-desc",
  tag: "all",
  page: "reports"
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
  chartPreview: document.querySelector("#chartPreview"),
  searchInput: document.querySelector("#searchInput"),
  marketFilter: document.querySelector("#marketFilter"),
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
  pagePanels: document.querySelectorAll("[data-page-panel]")
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

  markets.sort().forEach((market) => createOption(elements.marketFilter, market, marketLabels.get(market) || market));
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

function renderChartPreviews(metadata) {
  const charts = (metadata.chartPreviews || []).slice(0, 3);
  elements.chartPreview.replaceChildren();

  if (!charts.length) {
    const empty = document.createElement("p");
    empty.textContent = "No chart assets published";
    elements.chartPreview.appendChild(empty);
    return;
  }

  charts.forEach((chart) => {
    const item = document.createElement("div");
    item.className = "chart-thumb";
    item.innerHTML = `
      <img src="${escapeAttribute(chart.url)}" alt="${escapeAttribute(chart.label || chart.file)}" loading="lazy">
      <span>${escapeHtml(chart.label || chart.file)}</span>
    `;
    elements.chartPreview.appendChild(item);
  });
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

function render() {
  renderTags();
  const filtered = sortReports(state.reports.filter(reportMatches));
  elements.reportGrid.replaceChildren(...filtered.map(renderReportCard));
  elements.emptyState.hidden = filtered.length > 0;
  elements.resultCount.textContent = `${filtered.length} / ${state.reports.length} 份報告`;
}

function bindFilters() {
  elements.searchInput.addEventListener("input", (event) => {
    state.query = event.target.value;
    render();
  });
  elements.marketFilter.addEventListener("change", (event) => {
    state.market = event.target.value;
    render();
  });
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
    elements.marketFilter.value = "all";
    elements.typeFilter.value = "all";
    elements.sortFilter.value = "date-desc";
    render();
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
  buildFilters();
  updateStats(metadata);
  renderChartPreviews(metadata);
  bindFilters();
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
