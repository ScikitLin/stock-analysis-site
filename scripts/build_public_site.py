#!/usr/bin/env python3
"""Build the public static stock-report site from published HTML files."""

from __future__ import annotations

import fnmatch
import html
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from validate_trading_dashboard_data import validate_payload


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "site.config.json"
SITE_SRC = ROOT / "site_src"
TRADING_DATA_PATH = ROOT / "data" / "trading" / "trading_dashboard_data.json"


MARKET_LABELS = {
    "tw": "台股",
    "us": "美股",
    "mixed": "跨市場",
    "other": "其他",
}

TYPE_LABELS = {
    "custom": "指定個股",
    "top10": "Top 10 個股",
    "multi": "多檔個股",
    "single": "單檔個股",
    "detailed": "詳細分析",
    "framework": "個股分析框架",
    "other": "其他報告",
}


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def reset_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def strip_blocks(text: str) -> str:
    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    return text


def clean_html_text(text: str) -> str:
    text = strip_blocks(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def extract_tag_text(raw: str, tag: str) -> str:
    match = re.search(rf"<{tag}\b[^>]*>(.*?)</{tag}>", raw, flags=re.I | re.S)
    if not match:
        return ""
    return clean_html_text(match.group(1))


def extract_date(filename: str, text: str) -> str:
    candidates = re.findall(r"(20\d{2})[-_]?([01]\d)[-_]?([0-3]\d)", filename)
    if not candidates:
        candidates = re.findall(r"(20\d{2})[-_/]([01]\d)[-_/]([0-3]\d)", text)
    if not candidates:
        return ""
    year, month, day = candidates[-1]
    return f"{year}-{month}-{day}"


def classify_market(filename: str, title: str) -> str:
    name = filename.lower()
    if name.startswith("tw_") or "台股" in title:
        return "tw"
    if name.startswith("us_") or "美股" in title:
        return "us"
    if "跨市場" in title:
        return "mixed"
    return "other"


def classify_type(filename: str, title: str, symbols: list[str]) -> str:
    name = filename.lower()
    if "custom" in name or "指定" in title:
        return "custom"
    if "top10" in name or "前 10" in title or "Top 10" in title:
        return "top10"
    if "detailed" in name or "詳細" in title:
        return "detailed"
    if "multi" in name or len(symbols) > 1:
        return "multi"
    if len(symbols) == 1:
        return "single"
    if "framework" in name or "框架" in title:
        return "framework"
    return "other"


def ordered_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def extract_tw_symbol_names(raw: str) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    for code, name in re.findall(
        r'data-code="(\d{4})"[^>]*>\s*<span>[^<]*</span>\s*<strong>([^<]+)</strong>',
        raw,
        flags=re.I | re.S,
    ):
        results.append({"symbol": code, "name": clean_html_text(name)})

    for code, name in re.findall(
        r'<article[^>]+data-code="(\d{4})"[^>]*>\s*<h2>.*?\b\1\s+([^<\-\s]+)',
        raw,
        flags=re.I | re.S,
    ):
        results.append({"symbol": code, "name": clean_html_text(name)})

    for code, name in re.findall(
        r"<tr>\s*<td>\d+</td>\s*<td>(\d{4})</td>\s*<td>([^<]+)</td>",
        raw,
        flags=re.I | re.S,
    ):
        results.append({"symbol": code, "name": clean_html_text(name)})

    for code, name in re.findall(
        r"<h[2-4][^>]*>\s*\d+\.\s*(\d{4})\s+([^<\-]+)",
        raw,
        flags=re.I | re.S,
    ):
        results.append({"symbol": code, "name": clean_html_text(name)})

    unique: dict[str, dict[str, str]] = {}
    for item in results:
        unique.setdefault(item["symbol"], item)
    return list(unique.values())


def extract_us_symbol_names(raw: str) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    pattern = r'ticker:\s*"([A-Z][A-Z0-9.\-]{0,7})"[\s\S]{0,500}?company:\s*"([^"]+)"'
    for ticker, company in re.findall(pattern, raw):
        results.append({"symbol": ticker, "name": html.unescape(company)})
    return results


def extract_symbols(raw: str, filename: str, title: str) -> tuple[list[str], list[dict[str, str]]]:
    symbol_names = extract_tw_symbol_names(raw) + extract_us_symbol_names(raw)
    symbols = [item["symbol"] for item in symbol_names]
    symbols += re.findall(r'data-code="(\d{4})"', raw)
    symbols += re.findall(r"\b(\d{4})\s+[\u4e00-\u9fffA-Za-z][^。\n<]{0,18}", clean_html_text(raw))
    symbols += re.findall(r'ticker:\s*"([A-Z][A-Z0-9.\-]{0,7})"', raw)

    lower_name = filename.lower()
    symbols += re.findall(r"(?<!\d)(\d{4})(?!\d)", lower_name)
    if lower_name.startswith("us_"):
        filename_tokens = re.findall(r"_([a-z]{2,6})(?=_|\.html$)", lower_name)
        symbols += [token.upper() for token in filename_tokens if token not in {"stock", "analysis", "framework", "multi", "report", "bdc"}]
    symbols += re.findall(r"\b[A-Z]{2,6}\b", title)

    symbols = ordered_unique(symbols)
    known = {item["symbol"] for item in symbol_names}
    for symbol in symbols:
        if symbol not in known:
            symbol_names.append({"symbol": symbol, "name": ""})
            known.add(symbol)
    return symbols, symbol_names


def extract_summary(raw: str, title: str) -> str:
    text = clean_html_text(raw)
    markers = ["一句話結論", "框架結論", "快速結論", "前置閘門總結"]
    for marker in markers:
        index = text.find(marker)
        if index >= 0:
            summary = text[index + len(marker): index + len(marker) + 220].strip(" ：:-")
            if summary:
                return shorten(summary)
    if title and text.startswith(title):
        text = text[len(title):].strip()
    return shorten(text)


def shorten(text: str, limit: int = 150) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def build_tags(market: str, report_type: str, filename: str, title: str) -> list[str]:
    tags = [MARKET_LABELS.get(market, market), TYPE_LABELS.get(report_type, report_type)]
    name = filename.lower()
    if "framework" in name or "框架" in title:
        tags.append("分析框架")
    if "stock_analysis_framework" in name:
        tags.append("Bear/Base/Bull")
    if "top10" in name:
        tags.append("候選池")
    if "custom" in name:
        tags.append("自選清單")
    if "detailed" in name:
        tags.append("詳細版")
    return ordered_unique(tags)


def should_include(path: Path, include_patterns: list[str], exclude_patterns: list[str]) -> bool:
    name = path.name
    included = any(fnmatch.fnmatch(name, pattern) for pattern in include_patterns)
    excluded = any(fnmatch.fnmatch(name, pattern) for pattern in exclude_patterns)
    return included and not excluded


def collect_reports(config: dict) -> list[dict]:
    source_dir = ROOT / config.get("sourceDir", "output")
    include_patterns = config.get("includeHtml", ["*.html"])
    exclude_patterns = config.get("excludeHtml", [])
    reports: list[dict] = []

    for source_path in sorted(source_dir.glob("*.html")):
        if not should_include(source_path, include_patterns, exclude_patterns):
            continue
        raw = source_path.read_text(encoding="utf-8")
        title = extract_tag_text(raw, "title") or extract_tag_text(raw, "h1") or source_path.stem
        h1 = extract_tag_text(raw, "h1")
        symbols, symbol_names = extract_symbols(raw, source_path.name, title)
        market = classify_market(source_path.name, title)
        report_type = classify_type(source_path.name, title, symbols)
        date = extract_date(source_path.name, raw)
        reports.append(
            {
                "id": source_path.stem,
                "title": title,
                "heading": h1,
                "summary": extract_summary(raw, title),
                "date": date,
                "market": market,
                "marketLabel": MARKET_LABELS.get(market, market),
                "type": report_type,
                "typeLabel": TYPE_LABELS.get(report_type, report_type),
                "symbols": symbols,
                "symbolNames": symbol_names,
                "tags": build_tags(market, report_type, source_path.name, title),
                "sourceFile": source_path.name,
                "url": f"reports/{source_path.name}",
                "bytes": source_path.stat().st_size,
            }
        )
    return reports


def copy_site_assets(public_dir: Path) -> None:
    if not SITE_SRC.exists():
        raise FileNotFoundError(f"Missing site source directory: {SITE_SRC}")
    shutil.copytree(SITE_SRC, public_dir, dirs_exist_ok=True)


REPORT_HOME_SNIPPET = """
<a class="report-home-button" href="../index.html" aria-label="回首頁">← 回首頁</a>
<style>
.report-home-button {
  position: fixed;
  right: 18px;
  top: 18px;
  z-index: 9999;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 92px;
  min-height: 42px;
  padding: 10px 14px;
  border-radius: 999px;
  background: #0f172a;
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.22);
  font: 700 14px/1.2 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  text-decoration: none;
}
.report-home-button:hover,
.report-home-button:focus {
  background: #1d4ed8;
  color: #fff;
  outline: none;
}
@media (max-width: 720px) {
  .report-home-button {
    right: 12px;
    top: 12px;
    min-width: 84px;
    min-height: 40px;
    padding: 9px 12px;
  }
}
</style>
"""


def add_report_home_button(html_text: str) -> str:
    if "report-home-button" in html_text:
        return html_text
    if "</body>" in html_text:
        return html_text.replace("</body>", REPORT_HOME_SNIPPET + "\n</body>", 1)
    return html_text + REPORT_HOME_SNIPPET


def copy_reports(config: dict, public_dir: Path, reports: list[dict]) -> None:
    source_dir = ROOT / config.get("sourceDir", "output")
    report_dir = public_dir / "reports"
    reset_dir(report_dir)
    for report in reports:
        source_path = source_dir / report["sourceFile"]
        target_path = report_dir / report["sourceFile"]
        html_text = source_path.read_text(encoding="utf-8")
        target_path.write_text(add_report_home_button(html_text), encoding="utf-8")

    charts_dir = source_dir / "charts"
    if charts_dir.exists():
        shutil.copytree(charts_dir, report_dir / "charts", dirs_exist_ok=True)


def chart_label(path: Path) -> str:
    stem = path.stem.replace("_", " ")
    stem = re.sub(r"^\d+\s+", "", stem)
    stem = re.sub(r"\s+20\d{6}$", "", stem)
    replacements = {
        "tw candidate research map": "TW candidate research map",
        "tw candidate valuation growth matrix": "TW valuation x growth matrix",
        "tw candidate industry signal breadth": "TW industry signal breadth",
    }
    cleaned = re.sub(r"\s+", " ", stem).strip()
    return replacements.get(cleaned, cleaned)


def collect_chart_previews(config: dict) -> list[dict]:
    source_dir = ROOT / config.get("sourceDir", "published_reports")
    charts_dir = source_dir / "charts"
    if not charts_dir.exists():
        return []

    image_exts = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
    charts: list[dict] = []
    for path in sorted(charts_dir.iterdir()):
        if path.suffix.lower() not in image_exts or not path.is_file():
            continue
        charts.append(
            {
                "file": path.name,
                "label": chart_label(path),
                "url": f"reports/charts/{path.name}",
                "bytes": path.stat().st_size,
            }
        )
    candidate_charts = [chart for chart in charts if re.match(r"^\d{2}_tw_candidate_", chart["file"])]
    return candidate_charts or charts


def write_metadata(config: dict, public_dir: Path, reports: list[dict], chart_previews: list[dict]) -> None:
    source_dir = config.get("sourceDir", "published_reports")
    metadata = {
        "siteTitle": config.get("siteTitle", "股票研究資料分析庫"),
        "siteDescription": config.get("siteDescription", "以資料完整性、估值情境與風控紀律整理的公開個股研究索引。"),
        "disclaimer": config.get("disclaimer", ""),
        "feedbackIssueUrl": config.get("feedbackIssueUrl", ""),
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceDir": source_dir,
        "publishedFolder": source_dir,
        "chartPreviews": chart_previews,
        "reportCount": len(reports),
        "reports": sorted(reports, key=lambda item: (item.get("date", ""), item.get("title", "")), reverse=True),
    }
    (public_dir / "reports.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    data_js = "window.STOCK_REPORTS = " + json.dumps(metadata, ensure_ascii=False, indent=2) + ";\n"
    (public_dir / "assets" / "reports-data.js").write_text(data_js, encoding="utf-8")
    (public_dir / ".nojekyll").write_text("", encoding="utf-8")


def write_trading_data(public_dir: Path) -> None:
    if not TRADING_DATA_PATH.exists():
        return
    with TRADING_DATA_PATH.open("r", encoding="utf-8") as handle:
        payload = validate_payload(json.load(handle))
    data_js = "window.TRADING_DASHBOARD = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n"
    (public_dir / "assets" / "trading-data.js").write_text(data_js, encoding="utf-8")


def main() -> None:
    config = load_config()
    public_dir = ROOT / config.get("publicDir", "docs")
    reports = collect_reports(config)
    chart_previews = collect_chart_previews(config)
    public_dir.mkdir(parents=True, exist_ok=True)
    copy_site_assets(public_dir)
    copy_reports(config, public_dir, reports)
    write_metadata(config, public_dir, reports, chart_previews)
    write_trading_data(public_dir)
    print(f"Built {len(reports)} reports into {public_dir.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
