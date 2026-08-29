#!/usr/bin/env python3
"""Build five image-derived Taiwan reports and five US reports.

The supplied images are used only to define candidate membership.  Their
supply-chain labels are hypotheses, not proof of orders or instructions.
"""

from __future__ import annotations

import csv
import html
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_crash_risk_candidate_reports_20260717 as base
import build_google_capex_beneficiaries_report as google
import build_us_custom_23_report as us23
import build_us_reports_20260702 as themes
import build_us_stock_analysis_report as us20
import build_us_watchlist_integrated_report as core


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
RUN_DATE = os.environ.get("RUN_DATE", "2026-08-30")
TW_BASIS_DATE = os.environ.get("TW_BASIS_DATE", "2026-08-28")
US_BASIS_DATE = os.environ.get("US_BASIS_DATE", "2026-08-28")
TW_SUFFIX = TW_BASIS_DATE.replace("-", "")


NEW_US_CONFIG = {
    "SMCI": base.profile(
        "Super Micro Computer", "AI 伺服器 / Rack integration",
        "把 CPU、GPU、記憶體、網路與散熱零件組成可直接部署的 AI 伺服器和整櫃系統。",
        "AI 伺服器與液冷整櫃需求可推升營收，但供應、治理與毛利率必須一起驗證。",
        "客戶集中、會計與治理、競爭、GPU 供應、低毛利及高營運資金需求。",
        ["DELL"], (12, 17, 22, 28),
        "AI server revenue、rack shipments、gross margin、inventory/receivables。",
    ),
    "AEIS": base.profile(
        "Advanced Energy Industries", "精密電源 / 資料中心電源",
        "製造把市電轉成設備所需穩定電力的精密電源，客戶涵蓋資料中心、半導體設備與工業市場。",
        "AI 伺服器功率密度提高，可增加高效率電源的單機價值。",
        "資料中心客戶集中、半導體設備週期、庫存、價格競爭與整合執行。",
        ["MPWR"], (16, 21, 26, 32),
        "Data-center revenue、design wins、gross margin、inventory。",
    ),
    "SANM": base.profile(
        "Sanmina", "電子製造服務 / 系統組裝",
        "替品牌客戶製造通訊、雲端、工業與醫療設備，收入來自代工和系統整合。",
        "雲端硬體與網路設備外包增加，可提高產能利用率與產品組合。",
        "客戶集中、低毛利、訂單波動、庫存與營運資金。",
        ["FLEX"], (10, 14, 18, 23),
        "Communications/cloud revenue、new programs、margin、cash conversion。",
    ),
    "AMKR": base.profile(
        "Amkor Technology", "半導體封裝與測試",
        "在晶片製造完成後，替晶片加上封裝、電氣連接並測試是否正常。",
        "先進封裝與高效能運算晶片增加，可提高封裝複雜度與單顆價值。",
        "半導體週期、客戶集中、資本支出、產能利用率與價格競爭。",
        ["ASX"], (12, 16, 20, 25),
        "Advanced packaging mix、utilization、capex、gross margin。",
    ),
    "INTC": base.profile(
        "Intel", "CPU / 晶圓代工 / 先進封裝",
        "設計個人電腦與伺服器 CPU，也投資晶圓代工和先進封裝，希望替外部客戶製造晶片。",
        "製程改善、伺服器產品與外部代工訂單若兌現，可帶來營運槓桿。",
        "製程延誤、龐大資本支出、競爭、代工客戶不足、毛利率與現金流。",
        ["AMD"], (10, 15, 20, 26),
        "Process milestones、data-center share、foundry backlog、FCF。",
    ),
}


IR_OVERRIDES = {
    "SMCI": "https://ir.supermicro.com/",
    "AEIS": "https://ir.advancedenergy.com/",
    "SANM": "https://ir.sanmina.com/",
    "AMKR": "https://ir.amkor.com/",
    "INTC": "https://www.intc.com/",
}


IMAGE_GROUPS = [
    {
        "index": 1,
        "slug": "tesla_dojo_supply_chain",
        "theme": "Tesla Dojo、Dell、HPE 伺服器供應鏈",
        "tw": "2317 3231 2356 2324 2330 3661 3443 3189 3711 2449 6510 2301".split(),
        "us": "TSLA DELL HPE SMCI AVGO".split(),
        "excluded": "三星電子、三星電機屬韓股；CoolIT、Motivair 未單獨上市。",
    },
    {
        "index": 2,
        "slug": "power_cooling_supply_chain",
        "theme": "九家客戶共同供應商：電源與散熱",
        "tw": "2308 2301 3533 3017 3324 6230 2317 2382 8996 3653 2421 2330 6213 6274 2383 2368 3044 5469 4958".split(),
        "us": "FLEX AEIS TEL APH VRT".split(),
        "excluded": "麥格米特屬中國股、鴻騰精密屬港股；古河電工與日本電產屬日股；Boyd、CoolIT、Motivair、訊凱未單獨上市。",
    },
    {
        "index": 3,
        "slug": "server_nine_customer_supply_chain",
        "theme": "野村伺服器九大客戶供應鏈",
        "tw": "2382 2317 6669 3231 2356 2324 2345 8210 3017 2059 6584 6805 2308 2301 6781 3211 3533 3324 3653 8996 2421 6230 2454 3661 3443 3037 8046 3189 4958 2330 3711 2303 2449 6223 6510 6515 6683 2383 6213 6274 2368 3044 5469 5439".split(),
        "us": "CLS FLEX JBL FN SANM SMCI DELL CSCO ANET AEIS TEL APH VRT MRVL AVGO AMKR INTC".split(),
        "excluded": "三星、Panasonic、日本電產、古河電工、AT&S 等屬其他市場；訊凱、新光電氣、晶兆成、東培、IDI 等未單獨上市或非台美股。",
    },
    {
        "index": 4,
        "slug": "aws_microsoft_meta_custom_silicon",
        "theme": "AWS、Microsoft、Meta 自研晶片台廠組裝鏈",
        "tw": "2382 2317 2356 6669 2345 8210 3017 2059 6584 6805 2301 6781 2308 3211 3037 3661 3443 2330 3711 2303 2449 6223 2383 4958 6274 2368 5439".split(),
        "us": "AMZN MSFT META FN JBL FLEX CLS CSCO ANET MRVL AVGO AMKR INTC".split(),
        "excluded": "Panasonic、三星電機及中國／香港供應商屬其他市場；晶兆成、東培等未單獨上市。",
    },
    {
        "index": 5,
        "slug": "google_tpu_gpu_supply_chain",
        "theme": "Google TPU、NVIDIA GPU、AMD 伺服器組裝鏈",
        "tw": "2382 2356 2317 3231 6669 8210 3017 2059 2454 3443 3037 8046 4958 3189 2330 3711 2303 2449 6510 6223 6683 6515 2383 2368".split(),
        "us": "GOOGL NVDA AMD CLS FLEX SANM AVGO MRVL INTC AMKR".split(),
        "excluded": "Panasonic、AT&S、揖斐電、斗山及中國／香港供應商屬其他市場；新光電氣、晶兆成、東培、IDI 等未單獨上市。",
    },
]


def image_overlay_html(group: dict, market: str, rows: list[tuple[str, str]]) -> str:
    table = "".join(
        f"<tr><td><strong>{html.escape(code)}</strong></td><td>{html.escape(name)}</td>"
        f"<td>圖片候選；須由本報 EPS、估值與 thesis evidence 驗證</td></tr>"
        for code, name in rows
    )
    basis = TW_BASIS_DATE if market == "台股" else US_BASIS_DATE
    return f"""
    <section class="card image-source-overlay">
      <h2>圖片 {group['index']} 名單辨識與研究邊界</h2>
      <p><strong>圖片主題：</strong>{html.escape(group['theme'])}。</p>
      <p><strong>本報市場：</strong>{market}；正式收盤基準 {basis}。圖片只用來建立候選名單，不能證明供應關係、訂單、營收占比或未來 EPS。</p>
      <p><strong>排除項目：</strong>{html.escape(group['excluded'])}</p>
      <table><thead><tr><th>代號</th><th>公司</th><th>研究定位</th></tr></thead><tbody>{table}</tbody></table>
    </section>
    """.strip() + "\n"


def image_overlay_md(group: dict, market: str, rows: list[tuple[str, str]]) -> str:
    basis = TW_BASIS_DATE if market == "台股" else US_BASIS_DATE
    lines = [
        f"## 圖片 {group['index']} 名單辨識與研究邊界", "",
        f"- 圖片主題：{group['theme']}。",
        f"- 本報市場：{market}；正式收盤基準 {basis}。",
        "- 圖片只用來建立候選名單，不能證明供應關係、訂單、營收占比或未來 EPS。",
        f"- 排除項目：{group['excluded']}", "",
        "| 代號 | 公司 | 研究定位 |", "|---|---|---|",
    ]
    lines.extend(f"| {code} | {name} | 圖片候選；須由本報 EPS、估值與 thesis evidence 驗證 |" for code, name in rows)
    return "\n".join(lines) + "\n"


def build_tw_reports() -> list[Path]:
    candidate_path = OUTPUT / f"tw_stock_candidates_{TW_SUFFIX}.csv"
    with candidate_path.open(encoding="utf-8-sig", newline="") as handle:
        candidates = {row["股票代號 / Ticker"]: row for row in csv.DictReader(handle)}
    outputs: list[Path] = []
    for group in IMAGE_GROUPS:
        missing = [code for code in group["tw"] if code not in candidates]
        if missing:
            raise RuntimeError(f"image {group['index']} missing TW candidates: {missing}")
        stem = f"tw_image{group['index']}_{group['slug']}_{len(group['tw'])}"
        env = os.environ.copy()
        env.update({
            "RUN_DATE": TW_BASIS_DATE,
            "CANDIDATE_CODES": ",".join(group["tw"]),
            "CANDIDATE_COUNT": "0",
            "OUTPUT_PREFIX": stem,
            "REPORT_TITLE": f"圖片 {group['index']} 台股重新分析：{group['theme']}（{len(group['tw'])} 檔）",
            "REQUIRE_FULL_TW_RESEARCH": "0",
            "TW_EPS_REALTIME_COLLECT": "0",
            "TW_EPS_RESEARCH_REFRESH": "0",
            "TW_EPS_LEGACY_SEARCH": "0",
        })
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/write_tw_stock_analysis_framework_report.py")],
            cwd=ROOT, env=env, check=True,
        )
        rows = [(code, candidates[code]["公司名稱 / Company"]) for code in group["tw"]]
        html_path = OUTPUT / f"{stem}_{TW_SUFFIX}.html"
        md_path = OUTPUT / f"{stem}_{TW_SUFFIX}.md"
        html_text = html_path.read_text(encoding="utf-8").replace(
            '<main class="page-content">',
            '<main class="page-content">' + image_overlay_html(group, "台股", rows), 1,
        )
        html_path.write_text(html_text, encoding="utf-8")
        md_text = md_path.read_text(encoding="utf-8").replace(
            "## 專案流程記憶", image_overlay_md(group, "台股", rows) + "\n## 專案流程記憶", 1,
        )
        md_path.write_text(md_text, encoding="utf-8")
        outputs.extend([html_path, md_path])
    return outputs


def resolve_us_maps(universe: list[str]):
    configs = [NEW_US_CONFIG, base.EXTRA_US_CONFIG, google.CONFIG, us23.CONFIG, us20.CONFIG, themes.THEME_CONFIG, core.CONFIG]
    urls = [google.IR_URLS, us23.IR_URLS, us20.IR_URLS, core.IR_URLS]
    crosses = [google.RESEARCH_CROSSCHECKS, us23.RESEARCH_CROSSCHECKS, us20.RESEARCH_CROSSCHECKS, core.RESEARCH_CROSSCHECKS]
    indirects = [google.INDIRECT_SOURCES, us23.INDIRECT_SOURCES, us20.INDIRECT_SOURCES, core.INDIRECT_SOURCES]
    config, ir_urls, cross, indirect = {}, {}, {}, {}
    for ticker in universe:
        item = next((source[ticker] for source in configs if ticker in source), None)
        if item is None:
            raise KeyError(f"missing US profile: {ticker}")
        item = dict(item)
        item["peers"] = [peer for peer in item.get("peers", []) if peer not in universe][:1]
        config[ticker] = item
        ir = IR_OVERRIDES.get(ticker) or next(
            (source[ticker] for source in urls if ticker in source),
            f"https://stockanalysis.com/stocks/{ticker.lower()}/",
        )
        ir_urls[ticker] = ir
        cross[ticker] = next(
            (source[ticker] for source in crosses if ticker in source),
            (US_BASIS_DATE, "圖片供應鏈關係須由公司最新財報或 IR 重新驗證", ir),
        )
        indirect[ticker] = next(
            (source[ticker] for source in indirects if ticker in source),
            (US_BASIS_DATE, "圖片與產業需求只作候選訊號，不等同已取得訂單", ir),
        )
    return config, ir_urls, cross, indirect


def build_us_reports() -> list[Path]:
    universe = list(dict.fromkeys(ticker for group in IMAGE_GROUPS for ticker in group["us"]))
    config, ir_urls, cross, indirect = resolve_us_maps(universe)
    core.fetch = base.cached_fetch
    snapshot = ROOT / f"data/us_valuation_snapshot_portfolio_{US_BASIS_DATE.replace('-', '')}.json"
    base.ensure_us_snapshot(universe, snapshot)
    outputs: list[Path] = []
    for group in IMAGE_GROUPS:
        tickers = group["us"]
        core.BASIS_DATE = US_BASIS_DATE
        core.RUN_DATE = RUN_DATE
        core.REPORT_TITLE = f"圖片 {group['index']} 美股重新分析：{group['theme']}（{len(tickers)} 檔）"
        core.TICKERS = tickers
        core.CONFIG = {ticker: config[ticker] for ticker in tickers}
        core.IR_URLS = {ticker: ir_urls[ticker] for ticker in tickers}
        core.RESEARCH_CROSSCHECKS = {ticker: cross[ticker] for ticker in tickers}
        core.INDIRECT_SOURCES = {ticker: indirect[ticker] for ticker in tickers}
        core.VALUATION_SNAPSHOT = snapshot
        core.FORWARD_EPS_EVIDENCE = ROOT / f"data/us_forward_eps_evidence_{US_BASIS_DATE.replace('-', '')}.json"
        core.PRIMARY_OUT = core.PRIMARY_DOC = core.PRIMARY_PUB = None
        core.PRIMARY_JSON = core.LEGACY_OUT = core.LEGACY_DOC = core.LEGACY_PUB = core.LEGACY_JSON = None
        data, stats_map, _ = core.build_data()
        core.validate_report_consistency(data)
        rows = [(ticker, config[ticker]["company"]) for ticker in tickers]
        report_html = core.build_html(data, stats_map).replace(
            "<main>", "<main>" + image_overlay_html(group, "美股", rows), 1,
        )
        stem = f"us_image{group['index']}_{group['slug']}_{len(tickers)}_{RUN_DATE.replace('-', '')}_basis_{US_BASIS_DATE}"
        html_path = OUTPUT / f"{stem}.html"
        json_path = OUTPUT / f"{stem}_data.json"
        html_path.write_text(report_html, encoding="utf-8")
        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        outputs.extend([html_path, json_path])
    return outputs


def validate_outputs(paths: list[Path]) -> None:
    for path in paths:
        if not path.exists() or path.stat().st_size == 0:
            raise RuntimeError(f"missing output: {path}")
    for group in IMAGE_GROUPS:
        tw_stem = f"tw_image{group['index']}_{group['slug']}_{len(group['tw'])}_{TW_SUFFIX}"
        tw_text = (OUTPUT / f"{tw_stem}.html").read_text(encoding="utf-8")
        if tw_text.count('class="tab-button') != len(group["tw"]):
            raise RuntimeError(f"image {group['index']}: wrong TW count")
        us_stem = f"us_image{group['index']}_{group['slug']}_{len(group['us'])}_{RUN_DATE.replace('-', '')}_basis_{US_BASIS_DATE}"
        us_text = (OUTPUT / f"{us_stem}.html").read_text(encoding="utf-8")
        if len(set(__import__('re').findall(r'data-ticker="([A-Z0-9.-]+)"', us_text))) != len(group["us"]):
            raise RuntimeError(f"image {group['index']}: wrong US count")
        for text in (tw_text, us_text):
            if f"圖片 {group['index']} 名單辨識與研究邊界" not in text or "不能證明供應關係" not in text:
                raise RuntimeError(f"image {group['index']}: missing image boundary disclosure")


def main() -> None:
    outputs = build_tw_reports()
    outputs.extend(build_us_reports())
    validate_outputs(outputs)
    for path in outputs:
        print(path)


if __name__ == "__main__":
    main()
