#!/usr/bin/env python3
"""Validate trading dashboard data and emit the static JS payload."""

from __future__ import annotations

import argparse
import copy
import json
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "trading" / "trading_dashboard_data.json"
SITE_ASSET_PATH = ROOT / "site_src" / "assets" / "trading-data.js"
DOCS_ASSET_PATH = ROOT / "docs" / "assets" / "trading-data.js"


def load_data() -> dict:
    with DATA_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def tolerance(currency: str) -> float:
    return 0.02 if currency == "USD" else 0.5


def check_close(label: str, actual: float, expected: float, currency: str, checks: list[dict]) -> None:
    diff = actual - expected
    ok = abs(diff) <= tolerance(currency)
    checks.append(
        {
            "label": label,
            "ok": ok,
            "actual": round(actual, 4),
            "expected": round(expected, 4),
            "diff": round(diff, 4),
        }
    )


def pct_close(label: str, actual: float, expected: float, checks: list[dict]) -> None:
    diff = actual - expected
    checks.append(
        {
            "label": label,
            "ok": abs(diff) <= 0.02,
            "actual": round(actual, 4),
            "expected": round(expected, 4),
            "diff": round(diff, 4),
        }
    )


def completed_order(order: dict) -> bool:
    return float(order.get("shares") or 0) > 0 and order.get("action") in {"buy", "sell"}


def order_price(order: dict) -> float | None:
    value = order.get("fillPrice", order.get("price"))
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def date_key(date_value: str) -> int:
    return int(date_value.replace("-", ""))


def group_realized_by_date(realized_trades: list[dict]) -> list[dict]:
    by_date: dict[str, float] = defaultdict(float)
    for trade in realized_trades:
        by_date[trade["sellDate"]] += float(trade["realizedPnl"])
    return [{"date": date, "realizedPnl": amount} for date, amount in sorted(by_date.items())]


def build_contributions(market: dict) -> list[dict]:
    rows: dict[str, dict] = {}
    for trade in market.get("realizedTrades", []):
        symbol = trade["symbol"]
        rows.setdefault(
            symbol,
            {"symbol": symbol, "name": trade.get("name", symbol), "realizedPnl": 0.0, "unrealizedPnl": 0.0},
        )
        rows[symbol]["realizedPnl"] += float(trade.get("realizedPnl") or 0)
    for position in market.get("positions", []):
        symbol = position["symbol"]
        rows.setdefault(
            symbol,
            {"symbol": symbol, "name": position.get("name", symbol), "realizedPnl": 0.0, "unrealizedPnl": 0.0},
        )
        rows[symbol]["name"] = position.get("name", rows[symbol]["name"])
        rows[symbol]["unrealizedPnl"] += float(position.get("unrealizedPnl") or 0)
    result = []
    for item in rows.values():
        item["totalPnl"] = item["realizedPnl"] + item["unrealizedPnl"]
        result.append(item)
    return sorted(result, key=lambda item: (-item["totalPnl"], item["symbol"]))


def build_equity_series(market: dict) -> list[dict]:
    initial = float(market["initialCapital"])
    summary = market["summary"]
    realized_by_date = group_realized_by_date(market.get("realizedTrades", []))
    if not realized_by_date:
        return [
            {
                "date": market["currentDate"],
                "realizedPnl": float(summary.get("realizedPnl") or 0),
                "unrealizedPnl": float(summary.get("unrealizedPnl") or 0),
                "equity": float(summary.get("currentAssets") or initial),
            }
        ]

    first_date = min(
        [trade.get("buyDate") for trade in market.get("realizedTrades", []) if trade.get("buyDate")]
        + [market["orders"][0]["date"] if market.get("orders") else realized_by_date[0]["date"]]
    )
    cumulative = 0.0
    series = [{"date": first_date, "realizedPnl": 0.0, "unrealizedPnl": 0.0, "equity": initial}]
    for row in realized_by_date:
        cumulative += row["realizedPnl"]
        unrealized = float(summary["unrealizedPnl"]) if row["date"] == market["currentDate"] else 0.0
        series.append(
            {
                "date": row["date"],
                "realizedPnl": cumulative,
                "unrealizedPnl": unrealized,
                "equity": initial + cumulative + unrealized,
            }
        )
    if series[-1]["date"] != market["currentDate"]:
        series.append(
            {
                "date": market["currentDate"],
                "realizedPnl": float(summary["realizedPnl"]),
                "unrealizedPnl": float(summary["unrealizedPnl"]),
                "equity": float(summary["currentAssets"]),
            }
        )
    return series


def add_drawdown(series: list[dict]) -> tuple[list[dict], float, float]:
    peak = -math.inf
    max_drawdown = 0.0
    max_drawdown_pct = 0.0
    enriched = []
    for point in series:
        equity = float(point["equity"])
        peak = max(peak, equity)
        drawdown = equity - peak
        drawdown_pct = 0.0 if peak == 0 else (drawdown / peak) * 100
        max_drawdown = min(max_drawdown, drawdown)
        max_drawdown_pct = min(max_drawdown_pct, drawdown_pct)
        next_point = dict(point)
        next_point["drawdown"] = drawdown
        next_point["drawdownPct"] = drawdown_pct
        enriched.append(next_point)
    return enriched, max_drawdown, max_drawdown_pct


def build_realized_stats(market: dict, max_drawdown: float, max_drawdown_pct: float) -> dict:
    trades = market.get("realizedTrades", [])
    wins = [float(trade["realizedPnl"]) for trade in trades if float(trade["realizedPnl"]) > 0]
    losses = [float(trade["realizedPnl"]) for trade in trades if float(trade["realizedPnl"]) < 0]
    win_sum = sum(wins)
    loss_sum = sum(losses)
    return {
        "tradeCount": len(trades),
        "winCount": len(wins),
        "lossCount": len(losses),
        "winRatePct": (len(wins) / len(trades) * 100) if trades else 0,
        "avgWin": win_sum / len(wins) if wins else 0,
        "avgLoss": loss_sum / len(losses) if losses else 0,
        "profitFactor": win_sum / abs(loss_sum) if loss_sum else None,
        "bestTrade": max((float(trade["realizedPnl"]) for trade in trades), default=0),
        "worstTrade": min((float(trade["realizedPnl"]) for trade in trades), default=0),
        "maxDrawdown": max_drawdown,
        "maxDrawdownPct": max_drawdown_pct,
    }


def validate_market(market_key: str, market: dict) -> dict:
    currency = market["currency"]
    summary = market["summary"]
    checks: list[dict] = []
    warnings: list[str] = []

    realized_sum = sum(float(trade.get("realizedPnl") or 0) for trade in market.get("realizedTrades", []))
    unrealized_sum = sum(float(position.get("unrealizedPnl") or 0) for position in market.get("positions", []))
    market_value_sum = sum(float(position.get("marketValue") or 0) for position in market.get("positions", []))
    cost_sum = sum(float(position.get("cost") or 0) for position in market.get("positions", []))
    total_pnl = realized_sum + unrealized_sum
    current_assets = float(market["initialCapital"]) + total_pnl
    cash = current_assets - market_value_sum
    total_return_pct = (total_pnl / float(market["initialCapital"])) * 100

    check_close("已實現損益合計", realized_sum, float(summary["realizedPnl"]), currency, checks)
    check_close("未實現損益合計", unrealized_sum, float(summary["unrealizedPnl"]), currency, checks)
    check_close("股票庫存市值合計", market_value_sum, float(summary["marketValue"]), currency, checks)
    check_close("總損益", total_pnl, float(summary["totalPnl"]), currency, checks)
    check_close("目前推估總資產", current_assets, float(summary["currentAssets"]), currency, checks)
    check_close("推估現金", cash, float(summary["cash"]), currency, checks)
    pct_close("總報酬率", total_return_pct, float(summary["totalReturnPct"]), checks)

    for position in market.get("positions", []):
        expected_unrealized = float(position["marketValue"]) - float(position["cost"])
        check_close(
            f"{position['symbol']} 庫存損益",
            expected_unrealized,
            float(position["unrealizedPnl"]),
            currency,
            checks,
        )

    if market.get("orderLogComplete"):
        net_shares: dict[str, float] = defaultdict(float)
        for order in market.get("orders", []):
            if not completed_order(order):
                continue
            sign = 1 if order["action"] == "buy" else -1
            net_shares[order["symbol"]] += sign * float(order["shares"])
        positions = {position["symbol"]: float(position["shares"]) for position in market.get("positions", [])}
        for symbol in sorted(set(net_shares) | set(positions)):
            actual = net_shares.get(symbol, 0.0)
            expected = positions.get(symbol, 0.0)
            checks.append(
                {
                    "label": f"{symbol} 完全成交股數對庫存",
                    "ok": abs(actual - expected) <= 0.0001,
                    "actual": actual,
                    "expected": expected,
                    "diff": actual - expected,
                }
            )
    else:
        warnings.append("成交/委託紀錄標記為不完整；不以流水股數反推目前庫存。")

    if market_key == "us":
        for trade in market.get("realizedTrades", []):
            matches = [
                order
                for order in market.get("orders", [])
                if order.get("action") == "sell"
                and order.get("symbol") == trade.get("symbol")
                and abs(float(order.get("shares") or 0) - float(trade.get("shares") or 0)) <= 0.0001
                and order_price(order) is not None
                and abs(order_price(order) - float(trade.get("sellPrice") or 0)) <= 0.02
            ]
            if matches and not any(order["date"] == trade["sellDate"] for order in matches):
                dates = ", ".join(sorted(order["date"] for order in matches))
                warning = f"{trade['symbol']} {trade['sellDate']} 已實現日期與成交紀錄日期不同；成交紀錄日期: {dates}"
                if warning not in warnings:
                    warnings.append(warning)

    equity_series, max_drawdown, max_drawdown_pct = add_drawdown(build_equity_series(market))
    contributions = build_contributions(market)
    computed = {
        "positionCost": cost_sum,
        "realizedByDate": group_realized_by_date(market.get("realizedTrades", [])),
        "equitySeries": equity_series,
        "contributions": contributions,
        "stats": build_realized_stats(market, max_drawdown, max_drawdown_pct),
    }

    return {
        "status": "pass" if all(check["ok"] for check in checks) and not warnings else "warning",
        "checks": checks,
        "warnings": warnings,
        "computed": computed,
    }


def validate_payload(data: dict) -> dict:
    result = copy.deepcopy(data)
    validations = {}
    for market_key, market in result.get("markets", {}).items():
        validation = validate_market(market_key, market)
        validations[market_key] = {key: value for key, value in validation.items() if key != "computed"}
        market["computed"] = validation["computed"]
        market["validation"] = validations[market_key]
    result["validation"] = validations
    return result


def write_asset(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "window.TRADING_DASHBOARD = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n"
    path.write_text(body, encoding="utf-8")


def print_report(payload: dict) -> None:
    for market_key, market in payload["markets"].items():
        validation = market["validation"]
        status = validation["status"]
        print(f"{market_key.upper()} validation: {status}")
        for check in validation["checks"]:
            mark = "OK" if check["ok"] else "NG"
            print(f"  [{mark}] {check['label']}: actual={check['actual']} expected={check['expected']} diff={check['diff']}")
        for warning in validation["warnings"]:
            print(f"  [WARN] {warning}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-assets", action="store_true", help="Write trading-data.js into site_src and docs assets.")
    args = parser.parse_args()

    payload = validate_payload(load_data())
    print_report(payload)
    failed = [
        check
        for market in payload["markets"].values()
        for check in market["validation"]["checks"]
        if not check["ok"]
    ]
    if args.write_assets:
        write_asset(payload, SITE_ASSET_PATH)
        if (ROOT / "docs" / "assets").exists():
            write_asset(payload, DOCS_ASSET_PATH)
        print(f"Wrote {SITE_ASSET_PATH.relative_to(ROOT)}")
        if DOCS_ASSET_PATH.exists():
            print(f"Wrote {DOCS_ASSET_PATH.relative_to(ROOT)}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
