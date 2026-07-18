#!/usr/bin/env python3
"""Build six sector-grouped crash-risk stock reports for 2026-07-17."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_google_capex_beneficiaries_report as google
import build_us_custom_23_report as us23
import build_us_reports_20260702 as themes
import build_us_stock_analysis_report as us20
import build_us_watchlist_integrated_report as core


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
RUN_DATE = "2026-07-17"
TW_SUFFIX = "20260717"
US_BASIS_DATE = "2026-07-17"
REUTERS_CHIP_URL = "https://live.euronext.com/en/financial-news/stocks-sink-chip-rout-deepens-oil-set-weekly-gain"
AP_MARKET_URL = "https://apnews.com/article/65449e9565fba441a617f9517e097f5a"


TW_GROUPS = [
    {
        "stem": "tw_crash_risk_semiconductor_22",
        "title": "台股崩盤風險候選：半導體、IC 設計與設備 22 檔",
        "codes": "2330 2454 3711 3443 3661 3034 2379 3529 6488 5274 4966 5269 6415 1560 3583 3413 3131 6196 6223 6515 6531 6683".split(),
        "ratings": "A+ A A B+ C+ A- A- C+ B B+ B B+ B B B B+ C+ B C+ C+ C+ C".split(),
    },
    {
        "stem": "tw_crash_risk_ai_infrastructure_22",
        "title": "台股崩盤風險候選：AI 伺服器、網通、PCB、散熱與光通訊 22 檔",
        "codes": "2317 2382 3231 6669 2376 2345 6285 2368 3037 6274 2308 6412 3017 3324 3706 3653 6805 2059 8210 6442 4979 3363".split(),
        "ratings": "A+ A A- B+ A- B+ A- B+ B C+ A+ A- B C+ B+ B+ C+ B+ B+ C+ C C".split(),
    },
    {
        "stem": "tw_crash_risk_power_energy_defensive_21",
        "title": "台股崩盤風險候選：電網、能源、原物料與防禦現金流 21 檔",
        "codes": "1504 1519 1513 1609 1608 1503 1514 1612 6505 1301 1303 1101 1102 9958 2006 2015 1708 1216 2912 2886 5871".split(),
        "ratings": "A- B B+ B C B B C B B B B B B+ B C+ C+ A- A- A- B".split(),
    },
]


US_GROUPS = [
    {
        "stem": "us_crash_risk_semiconductor_22",
        "title": "美股崩盤風險候選：AI 晶片、半導體設備與 EDA 22 檔",
        "tickers": "NVDA AVGO AMD MRVL KLAC AMAT LRCX ASML TSM MU ARM QCOM TER TXN NXPI MPWR MCHP ON WDC STX SNPS CDNS".split(),
        "ratings": "A+ A B C+ A A- A- A- A B+ C+ B+ B+ A- B+ B+ B B B B A A".split(),
    },
    {
        "stem": "us_crash_risk_cloud_network_22",
        "title": "美股崩盤風險候選：雲端、網路、光通訊、伺服器與冷卻 22 檔",
        "tickers": "GOOGL MSFT AMZN META ORCL ANET CSCO TEL FN GLW COHR LITE CIEN DELL HPE CLS FLEX JBL VRT ETN PWR FIX".split(),
        "ratings": "A+ A+ A A B+ A- B A- B+ B C+ C+ C+ B B B+ B B B+ A A- B+".split(),
    },
    {
        "stem": "us_crash_risk_energy_grid_22",
        "title": "美股崩盤風險候選：電力、能源、電網、工程與國防 22 檔",
        "tickers": "GEV CEG VST NRG NEE CCJ LEU XOM CVX COP LNG EQT SLB BKR HUBB NVT EME MOD JCI TT RTX GE".split(),
        "ratings": "B+ B+ B B A- B+ C A- A- A- B+ B B+ B+ A- B+ A- B A- A A- A-".split(),
    },
]


def rating_bucket(rating: str) -> str:
    if rating.startswith("A"):
        return "大跌後核心候選；仍須分批並通過 thesis 檢查"
    if rating.startswith("B"):
        return "公司值得追蹤；等待估值或技術面安全邊際"
    return "高波動／高預期；只宜小部位，不因單日大跌攤平"


def common_macro_html(market: str, rows: list[tuple[str, str, str, str]]) -> str:
    basis = "2026-07-17 官方收盤" if market == "台股" else "2026-07-17 正式收盤"
    table_rows = "".join(
        f"<tr><td><strong>{html.escape(code)}</strong></td><td>{html.escape(name)}</td>"
        f"<td>{html.escape(industry)}</td><td><strong>{html.escape(rating)}</strong></td>"
        f"<td>{html.escape(rating_bucket(rating))}</td></tr>"
        for code, name, industry, rating in rows
    )
    return f"""
    <section class="card crash-risk-overlay">
      <h2>崩盤風險與評級覆蓋層</h2>
      <p><strong>價格基準：</strong>{basis}。7/17 全球晶片賣壓屬事件期，新增部位一律採 De-risk 節奏；本表評級不是買賣分數。</p>
      <p><strong>初步診斷：</strong>台股急跌超過 6% 且晶片股全球同步修正，但台積電 Q2 獲利仍優於預期、ASML 亦上調 2026 銷售展望，因此目前先視為估值重定價、槓桿與擁擠部位去化，尚不能直接判定 AI 基本面反轉。只有 hyperscaler 資本支出、半導體訂單／指引、HBM／先進封裝利用率或網路設備 bookings 連續轉弱，才升級為基本面反轉。</p>
      <p><strong>能源與通膨：</strong>7/17 Brent 約 85.95 美元、單日約 +2%；中東衝突若持續限制荷莫茲或紅海流量，能源、運費、保險與原料成本會壓低非能源公司的 margin，並透過通膨與利率延長壓縮長久期成長股倍數。能源股也不是無條件避險，需求衰退、政策、hedge 與停機仍可能抵銷高油價。</p>
      <p><strong>執行規則：</strong>第一批 20% 僅在跌停打開或出現承接；第二批 25% 須再有 5–8% 價格折讓；第三批 25% 等連兩日不創低或站回短均；最後 30% 等營收、財報或指引確認 thesis 未受傷。高波動 C 類不使用機械式攤平。</p>
      <p><a href="{REUTERS_CHIP_URL}">7/17 全球晶片賣壓與台股急跌來源</a>｜<a href="{AP_MARKET_URL}">7/17 油價、AI 股與中東衝突來源</a></p>
      <table><thead><tr><th>代號</th><th>公司</th><th>產業</th><th>評級</th><th>大跌時定位</th></tr></thead><tbody>{table_rows}</tbody></table>
    </section>
    """.strip() + "\n"


def common_macro_md(rows: list[tuple[str, str, str, str]]) -> str:
    lines = [
        "## 崩盤風險與 A/B/C 評級覆蓋層",
        "",
        "- **市場狀態：De-risk。** 7/17 官方收盤已納入；先視為估值重定價與擁擠部位去化，尚不能直接判定 AI 基本面反轉。",
        "- **基本面反轉閘門：** hyperscaler 資本支出、半導體訂單／指引、HBM／先進封裝利用率或網路設備 bookings 若連續轉弱，才升級為 thesis 破壞。",
        "- **能源／通膨：** 中東衝突若持續推升油價、運費與保險，將壓低非能源 margin 並延長高利率；能源股仍受需求、政策、hedge 與停機風險約束。",
        "- **分批：** 20%／25%／25%／30%；C 類不因跌停或單日長黑機械式攤平。",
        "",
        "| 代號 | 公司 | 產業 | 評級 | 大跌時定位 |",
        "|---|---|---|---|---|",
    ]
    lines.extend(f"| {c} | {n} | {i} | {r} | {rating_bucket(r)} |" for c, n, i, r in rows)
    lines.extend(["", f"來源：{REUTERS_CHIP_URL}；{AP_MARKET_URL}", ""])
    return "\n".join(lines)


def build_tw_reports() -> list[Path]:
    candidate_path = OUTPUT / f"tw_stock_candidates_{TW_SUFFIX}.csv"
    with candidate_path.open(encoding="utf-8-sig", newline="") as fh:
        candidates = {row["股票代號 / Ticker"]: row for row in csv.DictReader(fh)}
    outputs: list[Path] = []
    for group in TW_GROUPS:
        assert len(group["codes"]) == len(group["ratings"]) <= 25
        env = os.environ.copy()
        env.update({
            "RUN_DATE": RUN_DATE,
            "CANDIDATE_CODES": ",".join(group["codes"]),
            "CANDIDATE_COUNT": "0",
            "OUTPUT_PREFIX": group["stem"],
            "REPORT_TITLE": group["title"],
            "REQUIRE_FULL_TW_RESEARCH": "0",
            "TW_EPS_REALTIME_COLLECT": "0",
            "TW_EPS_RESEARCH_REFRESH": "0",
            "TW_EPS_LEGACY_SEARCH": "0",
        })
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/write_tw_stock_analysis_framework_report.py")],
            cwd=ROOT,
            env=env,
            check=True,
        )
        rows = []
        for code, rating in zip(group["codes"], group["ratings"]):
            row = candidates[code]
            rows.append((code, row["公司名稱 / Company"], row["產業名稱 / Industry"] or "產業分類待補", rating))
        html_path = OUTPUT / f"{group['stem']}_{TW_SUFFIX}.html"
        md_path = OUTPUT / f"{group['stem']}_{TW_SUFFIX}.md"
        html_text = html_path.read_text(encoding="utf-8")
        html_text = html_text.replace(
            '<main class="page-content">',
            '<main class="page-content">' + common_macro_html("台股", rows),
            1,
        )
        html_path.write_text(html_text, encoding="utf-8")
        md_text = md_path.read_text(encoding="utf-8")
        md_text = md_text.replace("## 專案流程記憶", common_macro_md(rows) + "\n## 專案流程記憶", 1)
        md_path.write_text(md_text, encoding="utf-8")
        outputs.extend([html_path, md_path])
    return outputs


def profile(company, industry, business, thesis, bear, peers, mult, catalyst, priority="優先研究"):
    return {
        "company": company,
        "industry": industry,
        "business": business,
        "thesis": thesis,
        "bear": bear,
        "peers": peers,
        "mult": mult,
        "action": "只在估值、技術與基本面閘門同時通過後分批研究",
        "priority": priority,
        "memo_depth": "deep",
        "catalyst": catalyst,
        "rerating_evidence": [],
    }


EXTRA_US_CONFIG = {
    "AMD": profile("Advanced Micro Devices", "CPU / AI GPU", "提供資料中心 CPU、AI GPU、PC 與嵌入式晶片。", "Instinct 與 EPYC 可擴大 AI／資料中心市占，但軟體、生態與供應執行須持續驗證。", "AI GPU 市占不及預期、毛利率、供應、出口限制與高估值。", ["INTC"], (20, 27, 34, 42), "Instinct revenue、EPYC share、gross margin、AI software adoption。"),
    "MSFT": profile("Microsoft", "雲端 / 企業軟體 / AI", "以 Azure、Microsoft 365、Windows、資安與 Copilot 取得 recurring revenue。", "Azure 與企業軟體護城河最完整，AI 變現可分散單一模型風險。", "CapEx 回報不及預期、Copilot 採用、雲端競爭、監管與高基期。", ["SAP"], (24, 29, 34, 40), "Azure growth、AI revenue、Copilot seats、capex/FCF。"),
    "AMZN": profile("Amazon", "雲端 / 電商", "AWS 雲端與全球電商平台並行，另有廣告與物流網路。", "AWS AI 基建與零售效率改善形成雙引擎。", "AI CapEx 回收慢、零售 margin、競爭、監管與消費放緩。", ["WMT"], (24, 30, 36, 43), "AWS growth、AI backlog、retail margin、FCF。"),
    "META": profile("Meta Platforms", "社群廣告 / AI 平台", "經營 Facebook、Instagram、WhatsApp 與廣告平台。", "AI 推薦與廣告效率可直接轉為收入，現金流較純 AI 基建股完整。", "CapEx 過快、廣告週期、監管、模型商品化與 Reality Labs 虧損。", ["PINS"], (20, 25, 30, 36), "Ad impressions/pricing、AI engagement、capex、FCF。"),
    "ORCL": profile("Oracle", "企業資料庫 / 雲端基礎設施", "提供資料庫、企業應用與 OCI 雲端。", "AI 雲端合約與既有資料庫客戶可推升 backlog，但建置資本需求高。", "CapEx、供電與 GPU 交付、客戶集中、負債與競爭。", ["SAP"], (18, 23, 28, 34), "OCI growth、RPO、AI capacity、capex/FCF。"),
    "ADI": profile("Analog Devices", "類比 / 工業半導體", "提供工業、汽車、通訊與消費電子用類比晶片。", "高品質類比組合可受惠工業復甦與資料中心電源管理。", "工業庫存、汽車週期、中國需求與高品質溢價收縮。", [], (20, 24, 28, 32), "Industrial orders、inventory、auto content、gross margin。"),
    "TXN": profile("Texas Instruments", "類比 / 嵌入式半導體", "大量供應工業與汽車用類比、嵌入式晶片。", "自有晶圓廠與廣泛產品線利於週期復甦，但短期折舊壓力高。", "產能過剩、工業低迷、價格競爭、中國與 FCF 壓力。", [], (18, 22, 26, 30), "Industrial demand、utilization、gross margin、capex/FCF。"),
    "NXPI": profile("NXP Semiconductors", "汽車 / 工業半導體", "提供汽車 MCU、雷達、連接與工業晶片。", "汽車電子含量與 edge processing 支持成長。", "汽車去庫存、中國、價格壓力、客戶集中與週期。", [], (16, 20, 24, 28), "Auto revenue、inventory、design wins、margin。"),
    "MPWR": profile("Monolithic Power Systems", "電源管理晶片", "提供資料中心、汽車、工業與消費電子的高效率電源管理晶片。", "AI 伺服器功率密度提高可擴大單機內容。", "大客戶集中、競爭、產品驗證、估值與供應執行。", [], (28, 34, 40, 48), "Enterprise data revenue、AI content、gross margin、customer mix。"),
    "MCHP": profile("Microchip Technology", "MCU / 類比", "提供工業、汽車與航太用 MCU、類比及連接晶片。", "去庫存結束後具高營運槓桿，但負債與低谷能見度較差。", "庫存調整延長、工業需求、負債、價格競爭與 FCF。", [], (14, 18, 22, 26), "Bookings、inventory、factory utilization、debt reduction。"),
    "ON": profile("onsemi", "車用 / 工業功率半導體", "提供電動車、工業自動化與電源轉換用功率和感測晶片。", "SiC 與高效率電源長期需求仍在，但需等汽車與工業庫存修復。", "EV 成長放緩、SiC 供給、價格競爭、產能利用率與客戶集中。", [], (14, 18, 22, 27), "Auto/industrial orders、SiC utilization、gross margin、inventory。"),
    "SNPS": profile("Synopsys", "EDA / 半導體 IP", "提供晶片設計軟體、驗證工具與半導體 IP。", "AI 與先進製程提高設計複雜度，recurring revenue 與切換成本高。", "出口限制、併購整合、客戶集中、設計週期與估值。", ["ANSS"], (30, 36, 42, 50), "Backlog、EDA growth、AI tools、margin/FCF。"),
    "CDNS": profile("Cadence Design Systems", "EDA / 系統設計", "提供晶片與電子系統設計、驗證及模擬軟體。", "先進晶片、chiplet 與 AI 設計提高工具價值。", "出口限制、客戶集中、估值、競爭與企業支出。", [], (30, 36, 42, 50), "Backlog、AI portfolio、recurring revenue、margin。"),
    "XOM": profile("Exxon Mobil", "綜合油氣", "整合上游、煉油、化工與 LNG 資產。", "高油價、低成本資源與資本紀律提供通膨對沖，但不是無風險避險。", "油價反轉、需求衰退、Guyana/Permian 執行、化工 margin 與政策。", [], (10, 13, 16, 19), "Production、realized price、refining margin、FCF/回購。"),
    "CVX": profile("Chevron", "綜合油氣", "經營全球油氣、煉油與 LNG。", "長週期資產與股東回報可受惠油價風險溢價。", "油價、專案延誤、併購整合、成本與政策。", [], (10, 13, 16, 19), "Production、LNG、capex、FCF/股利。"),
    "COP": profile("ConocoPhillips", "上游油氣", "聚焦全球原油與天然氣勘探生產。", "上游 beta 高，可直接受惠油價與資本紀律。", "油價下跌、資源品質、成本、整合與缺少下游緩衝。", [], (9, 12, 15, 18), "Production、realized price、unit cost、FCF。"),
    "LNG": profile("Cheniere Energy", "LNG 出口", "營運美國 LNG 液化與出口設施，多數收入來自長約。", "歐亞能源安全與長約提供現金流，但航道與工程風險仍在。", "設施停機、氣價 basis、合約、擴建成本與政策。", [], (12, 16, 20, 24), "Volumes、contracted capacity、Sabine/Corpus uptime、FCF。"),
    "EQT": profile("EQT", "天然氣生產", "是美國大型天然氣生產商，供應發電與 LNG 出口鏈。", "天然氣電力需求與 LNG 外銷可提高價格彈性。", "氣價下跌、hedge、管線 basis、槓桿與產量執行。", [], (9, 13, 17, 22), "Realized gas price、hedges、production、FCF/debt。"),
    "SLB": profile("SLB", "油田服務", "提供鑽井、完井、數位與海上油氣技術服務。", "中東與海上長週期投資可提高訂單能見度。", "油公司削減 CapEx、地緣營運風險、價格競爭與油價反轉。", [], (14, 18, 22, 26), "International revenue、digital、margin、FCF。"),
    "BKR": profile("Baker Hughes", "油田服務 / LNG 設備", "提供油田服務、LNG 渦輪與工業能源技術。", "LNG 設備與服務 backlog 分散純上游週期。", "LNG 專案延遲、油田服務價格、供應鏈、油價與執行。", [], (14, 18, 22, 26), "IET orders/backlog、LNG awards、margin、FCF。"),
}


def merged_us_maps():
    configs = [google.CONFIG, us23.CONFIG, us20.CONFIG, themes.THEME_CONFIG, core.CONFIG]
    urls = [google.IR_URLS, us23.IR_URLS, us20.IR_URLS, core.IR_URLS]
    crosses = [google.RESEARCH_CROSSCHECKS, us23.RESEARCH_CROSSCHECKS, us20.RESEARCH_CROSSCHECKS, core.RESEARCH_CROSSCHECKS]
    indirects = [google.INDIRECT_SOURCES, us23.INDIRECT_SOURCES, us20.INDIRECT_SOURCES, core.INDIRECT_SOURCES]
    universe = [ticker for group in US_GROUPS for ticker in group["tickers"]]
    config = {}
    ir_urls = {}
    cross = {}
    indirect = {}
    for ticker in universe:
        item = EXTRA_US_CONFIG.get(ticker)
        if item is None:
            item = next((source[ticker] for source in configs if ticker in source), None)
        if item is None:
            raise KeyError(f"missing US profile: {ticker}")
        item = dict(item)
        item["peers"] = [peer for peer in item.get("peers", []) if peer not in universe][:1]
        config[ticker] = item
        ir_urls[ticker] = next((source[ticker] for source in urls if ticker in source), f"https://stockanalysis.com/stocks/{ticker.lower()}/")
        cross[ticker] = next((source[ticker] for source in crosses if ticker in source), (US_BASIS_DATE, "公司財報與指引需於下一財報重新驗證", ir_urls[ticker]))
        indirect[ticker] = next((source[ticker] for source in indirects if ticker in source), (US_BASIS_DATE, "產業需求只作交叉訊號，不等同已取得訂單", ir_urls[ticker]))
    return universe, config, ir_urls, cross, indirect


FETCH_CACHE: dict[str, str] = {}
ORIGINAL_FETCH = core.fetch
FETCH_CACHE_DIR = Path(f"/private/tmp/us_crash_risk_fetch_cache_{US_BASIS_DATE.replace('-', '')}")


def cached_fetch(url: str) -> str:
    if url not in FETCH_CACHE:
        FETCH_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        path = FETCH_CACHE_DIR / (hashlib.sha256(url.encode("utf-8")).hexdigest() + ".txt")
        if path.exists() and path.stat().st_size:
            FETCH_CACHE[url] = path.read_text(encoding="utf-8", errors="ignore")
        else:
            FETCH_CACHE[url] = ORIGINAL_FETCH(url)
            path.write_text(FETCH_CACHE[url], encoding="utf-8")
    return FETCH_CACHE[url]


def ensure_us_snapshot(universe: list[str], path: Path) -> None:
    rows = {}
    if path.exists():
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("basis_date") == US_BASIS_DATE and all(t in payload.get("tickers", {}) for t in universe):
            return
        if payload.get("basis_date") == US_BASIS_DATE:
            rows = payload.get("tickers", {})
    for ticker in universe:
        if ticker in rows:
            continue
        stat = core.stats(ticker)
        history = core.history(ticker)
        basis = next((row for row in history if row.get("t") == US_BASIS_DATE), None)
        if basis is None:
            raise RuntimeError(f"{ticker}: missing formal close for {US_BASIS_DATE}")
        close = core.num(basis.get("c"))
        live_price = core.num(stat.get("stats_price"))
        ttm_eps = core.num(stat.get("Earnings Per Share (EPS)"))
        live_fpe = core.num(stat.get("Forward PE"))
        valuation_eps = live_price / live_fpe if live_price and live_fpe and live_fpe > 0 else None
        rows[ticker] = {
            "close": close,
            "pe": close / ttm_eps if close and ttm_eps and ttm_eps > 0 else None,
            "forward_pe": close / valuation_eps if close and valuation_eps and valuation_eps > 0 else None,
            "ttm_eps": ttm_eps,
            "valuation_eps": valuation_eps,
            "valuation_eps_basis": "2026-07-17 post-close snapshot implied EPS = captured price / captured Forward P/E; FY1/FY2 direct consensus are reported separately",
            "valuation_eps_type": "SAME_DAY_POST_CLOSE_IMPLIED" if valuation_eps else "UNAVAILABLE",
            "valuation_eps_confidence": "Medium" if valuation_eps else "Blocked",
            "source_url": stat["url"],
            "source_timestamp": stat.get("stats_timestamp"),
        }
        print("snapshot", ticker, close, rows[ticker]["forward_pe"], flush=True)
        path.write_text(json.dumps({
            "basis_date": US_BASIS_DATE,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "source": "partial checkpoint; 2026-07-17 formal close and post-close valuation snapshot",
            "tickers": rows,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        time.sleep(0.03)
    path.write_text(json.dumps({
        "basis_date": US_BASIS_DATE,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "source": "2026-07-17 StockAnalysis formal close and post-close valuation snapshot; no premarket price used as report price",
        "tickers": rows,
    }, ensure_ascii=False, indent=2), encoding="utf-8")


def build_us_reports() -> list[Path]:
    universe, config, ir_urls, cross, indirect = merged_us_maps()
    assert len(universe) == len(set(universe))
    core.fetch = cached_fetch
    snapshot = ROOT / "data/us_valuation_snapshot_crash_risk_20260717.json"
    ensure_us_snapshot(universe, snapshot)
    outputs = []
    for group in US_GROUPS:
        assert len(group["tickers"]) == len(group["ratings"]) <= 25
        tickers = group["tickers"]
        core.BASIS_DATE = US_BASIS_DATE
        core.RUN_DATE = RUN_DATE
        core.REPORT_TITLE = group["title"]
        core.TICKERS = tickers
        core.CONFIG = {ticker: config[ticker] for ticker in tickers}
        core.IR_URLS = {ticker: ir_urls[ticker] for ticker in tickers}
        core.RESEARCH_CROSSCHECKS = {ticker: cross[ticker] for ticker in tickers}
        core.INDIRECT_SOURCES = {ticker: indirect[ticker] for ticker in tickers}
        core.VALUATION_SNAPSHOT = snapshot
        core.FORWARD_EPS_EVIDENCE = ROOT / "data/us_forward_eps_evidence_20260717.json"
        core.PRIMARY_OUT = core.PRIMARY_DOC = core.PRIMARY_PUB = None
        core.PRIMARY_JSON = core.LEGACY_OUT = core.LEGACY_DOC = core.LEGACY_PUB = core.LEGACY_JSON = None
        data, stats_map, _ = core.build_data()
        rating_by_ticker = dict(zip(tickers, group["ratings"]))
        for item in data:
            item["crash_rating"] = rating_by_ticker[item["ticker"]]
        core.validate_report_consistency(data)
        report_html = core.build_html(data, stats_map)
        rows = [(ticker, config[ticker]["company"], config[ticker]["industry"], rating_by_ticker[ticker]) for ticker in tickers]
        report_html = report_html.replace("<main>", "<main>" + common_macro_html("美股", rows), 1)
        stem = f"{group['stem']}_{RUN_DATE.replace('-', '')}_basis_{US_BASIS_DATE}"
        html_path = OUTPUT / f"{stem}.html"
        json_path = OUTPUT / f"{stem}_data.json"
        html_path.write_text(report_html, encoding="utf-8")
        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        outputs.extend([html_path, json_path])
    return outputs


def validate_outputs(paths: list[Path]) -> None:
    missing = [str(path) for path in paths if not path.exists() or path.stat().st_size == 0]
    if missing:
        raise RuntimeError("missing outputs: " + ", ".join(missing))
    for group in TW_GROUPS:
        text = (OUTPUT / f"{group['stem']}_{TW_SUFFIX}.html").read_text(encoding="utf-8")
        if text.count('class="tab-button') != len(group["codes"]):
            raise RuntimeError(f"{group['stem']}: wrong TW stock count")
        if "De-risk" not in text or "崩盤風險與評級覆蓋層" not in text:
            raise RuntimeError(f"{group['stem']}: missing crash-risk overlay")
    for group in US_GROUPS:
        stem = f"{group['stem']}_{RUN_DATE.replace('-', '')}_basis_{US_BASIS_DATE}"
        text = (OUTPUT / f"{stem}.html").read_text(encoding="utf-8")
        if text.count('class="tab') < len(group["tickers"]):
            raise RuntimeError(f"{group['stem']}: wrong US stock count")
        if "崩盤風險與評級覆蓋層" not in text or US_BASIS_DATE not in text:
            raise RuntimeError(f"{group['stem']}: missing basis/risk overlay")


def main() -> None:
    paths = build_tw_reports()
    paths.extend(build_us_reports())
    validate_outputs(paths)
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
