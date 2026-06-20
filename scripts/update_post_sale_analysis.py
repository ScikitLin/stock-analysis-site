#!/usr/bin/env python3
"""Refresh compact price history used by the post-sale event study."""

from __future__ import annotations

import json
import ssl
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRADING_DATA = ROOT / "data" / "trading" / "trading_dashboard_data.json"
TW_HISTORY = ROOT / "data" / "tw_daily_price_history_by_stock.json"
OUTPUT = ROOT / "data" / "trading" / "post_sale_price_history.json"
TPEX_SYMBOLS = {"3141", "4739", "6143", "6488", "6907"}
SSL_CONTEXT = ssl._create_unverified_context()


def fetch_json(url: str, data: bytes | None = None) -> dict:
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with urllib.request.urlopen(request, timeout=30, context=SSL_CONTEXT) as response:
        return json.loads(response.read().decode("utf-8"))


def parse_number(value: object) -> float | None:
    text = str(value or "").strip().replace(",", "").replace("+", "")
    if text in {"", "--", "---"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def roc_to_iso(value: str) -> str:
    year, month, day = [int(part) for part in value.split("/")]
    return f"{year + 1911:04d}-{month:02d}-{day:02d}"


def month_starts(start_value: str, end_value: str) -> list[date]:
    start = datetime.strptime(start_value, "%Y-%m-%d").date().replace(day=1)
    end = datetime.strptime(end_value, "%Y-%m-%d").date().replace(day=1)
    months = []
    current = start
    while current <= end:
        months.append(current)
        current = date(current.year + (current.month == 12), 1 if current.month == 12 else current.month + 1, 1)
    return months


def fetch_twse_month(symbol: str, month: date) -> list[dict]:
    month_key = month.strftime("%Y%m%d")
    url = (
        "https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY"
        f"?date={month_key}&stockNo={symbol}&response=json"
    )
    payload = fetch_json(url)
    rows = []
    for item in payload.get("data", []):
        rows.append(
            {
                "date": roc_to_iso(item[0]),
                "open": parse_number(item[3]),
                "high": parse_number(item[4]),
                "low": parse_number(item[5]),
                "close": parse_number(item[6]),
            }
        )
    return rows


def fetch_tpex_month(symbol: str, month: date) -> list[dict]:
    form = urllib.parse.urlencode({"code": symbol, "date": month.strftime("%Y/%m/%d")}).encode()
    payload = fetch_json("https://www.tpex.org.tw/www/zh-tw/afterTrading/tradingStock", data=form)
    table = next((item for item in payload.get("tables", []) if item.get("fields") and item.get("data")), None)
    if not table:
        return []
    fields = [str(field).replace(" ", "") for field in table["fields"]]
    index = {field: offset for offset, field in enumerate(fields)}
    rows = []
    for item in table["data"]:
        rows.append(
            {
                "date": roc_to_iso(str(item[index["日期"]])),
                "open": parse_number(item[index["開盤"]]),
                "high": parse_number(item[index["最高"]]),
                "low": parse_number(item[index["最低"]]),
                "close": parse_number(item[index["收盤"]]),
            }
        )
    return rows


def local_tw_history() -> dict[str, list[dict]]:
    payload = json.loads(TW_HISTORY.read_text(encoding="utf-8"))
    result = {}
    for symbol, rows in payload.get("stocks", {}).items():
        result[symbol] = [
            {
                "date": row.get("date"),
                "open": row.get("open"),
                "high": row.get("max"),
                "low": row.get("min"),
                "close": row.get("close"),
            }
            for row in rows
            if row.get("date") and row.get("close") is not None
        ]
    return result


def fetch_us_history(symbol: str, start_value: str) -> list[dict]:
    url = f"https://stockanalysis.com/api/symbol/s/{symbol}/history?range=Max&period=Daily"
    payload = fetch_json(url)
    return [
        {
            "date": row.get("t"),
            "open": row.get("o"),
            "high": row.get("h"),
            "low": row.get("l"),
            "close": row.get("c"),
        }
        for row in payload.get("data", [])
        if row.get("t", "") >= start_value and row.get("c") is not None
    ]


def merge_rows(*groups: list[dict]) -> list[dict]:
    by_date = {}
    for rows in groups:
        for row in rows:
            if row.get("date") and row.get("close") is not None:
                by_date[row["date"]] = row
    return [by_date[key] for key in sorted(by_date)]


def main() -> None:
    dashboard = json.loads(TRADING_DATA.read_text(encoding="utf-8"))
    local_history = local_tw_history()
    output = {
        "generatedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "methodology": "Each sale is an independent event. Returns use closes on trading days 1, 3, 5, 10 and 20 after the sale; MFE/MAE use daily highs/lows.",
        "markets": {},
    }
    for market_key, market in dashboard["markets"].items():
        trades = market.get("realizedTrades", [])
        earliest_by_symbol = {}
        for trade in trades:
            earliest_by_symbol[trade["symbol"]] = min(
                earliest_by_symbol.get(trade["symbol"], trade["sellDate"]),
                trade["sellDate"],
            )
        histories = {}
        for symbol, earliest in sorted(earliest_by_symbol.items()):
            if market_key == "us":
                histories[symbol] = fetch_us_history(symbol, earliest)
                continue
            official_rows = []
            for month in month_starts(earliest, market["currentDate"]):
                fetcher = fetch_tpex_month if symbol in TPEX_SYMBOLS else fetch_twse_month
                official_rows.extend(fetcher(symbol, month))
            histories[symbol] = merge_rows(local_history.get(symbol, []), official_rows)
        output["markets"][market_key] = {
            "priceThrough": max(
                (row["date"] for rows in histories.values() for row in rows),
                default=None,
            ),
            "histories": histories,
        }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
