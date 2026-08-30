#!/usr/bin/env python3
"""Collect US forward EPS and FETS/RES evidence from public forecast pages.

The output is an overlay JSON consumed by build_us_watchlist_integrated_report.py.
It is intentionally conservative: unavailable / PRO-only fields stay missing.
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
import subprocess
import time
from datetime import datetime, timezone


BASE = pathlib.Path("/Users/linwj/Documents/股票分析")


def fetch(url: str) -> str:
    """Fetch with the host trust store used by curl.

    The standalone Python runtime on this host does not ship a complete CA
    bundle.  Using curl preserves TLS verification without disabling SSL.
    """
    completed = subprocess.run(
        [
            "curl", "-fsSL", "--max-time", "30",
            "-A", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "-H", "Accept: text/html,application/xhtml+xml",
            url,
        ],
        check=True,
        capture_output=True,
    )
    return completed.stdout.decode("utf-8", errors="replace")


def token_value(token: str):
    token = token.strip()
    if token in {"null", "void 0", "undefined", ""}:
        return None
    if token.startswith('"') and token.endswith('"'):
        value = token[1:-1]
        return None if value == "[PRO]" else value
    try:
        return float(token)
    except ValueError:
        return token


def parse_array(block: str, field: str) -> list:
    match = re.search(rf"{re.escape(field)}:\[([^\]]*)\]", block)
    if not match:
        return []
    tokens = re.findall(r'"[^"]*"|null|void 0|undefined|-?\d+(?:\.\d+)?(?:e[+-]?\d+)?', match.group(1))
    return [token_value(token) for token in tokens]


def parse_last_date(block: str) -> int | None:
    match = re.search(r"lastDate:(\d+)", block)
    return int(match.group(1)) if match else None


def parse_table_blocks(html: str) -> tuple[str, str]:
    annual = re.search(r"table:\{annual:\{(.*?)\},quarterly:\{", html, re.S)
    quarterly = re.search(r"\},quarterly:\{(.*?)\}\}\},estimatesCharts", html, re.S)
    return (annual.group(1) if annual else "", quarterly.group(1) if quarterly else "")


def parse_eps_chart(html: str) -> dict:
    match = re.search(
        r"estimatesCharts:\{eps:\{\"([0-9-]+)\":\{no:(\d+),avg:([\d.]+),low:([\d.]+),high:([\d.]+)\}",
        html,
    )
    if not match:
        return {}
    return {
        "date": match.group(1),
        "analyst_count": int(match.group(2)),
        "avg": float(match.group(3)),
        "low": float(match.group(4)),
        "high": float(match.group(5)),
    }


def parse_price_targets(html: str) -> dict:
    match = re.search(
        r"targets:\{low:([\d.]+),high:([\d.]+),count:(\d+),median:([\d.]+),average:([\d.]+),updated:\"([0-9-]+)\"",
        html,
    )
    if not match:
        return {}
    return {
        "low": float(match.group(1)),
        "high": float(match.group(2)),
        "count": int(match.group(3)),
        "median": float(match.group(4)),
        "average": float(match.group(5)),
        "updated": match.group(6),
    }


def parse_current_ratings(html: str) -> dict:
    match = re.search(
        r"currentRatings:\{source:\"([^\"]+)\",consensus:\"([^\"]+)\",score:([\d.]+),count:(\d+),strongBuy:(\d+),buy:(\d+),hold:(\d+),sell:(\d+),strongSell:(\d+)",
        html,
    )
    if not match:
        return {}
    return {
        "source": match.group(1),
        "consensus": match.group(2),
        "score": float(match.group(3)),
        "count": int(match.group(4)),
        "strong_buy": int(match.group(5)),
        "buy": int(match.group(6)),
        "hold": int(match.group(7)),
        "sell": int(match.group(8)),
        "strong_sell": int(match.group(9)),
    }


def finite(value) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value)


def margin(revenue: float | None, numerator: float | None) -> float | None:
    return numerator / revenue * 100 if finite(revenue) and revenue and finite(numerator) else None


def fmt_pct(value: float | None) -> str:
    return "N/A" if not finite(value) else f"{value:.1f}%"


def fmt_billion(value: float | None) -> str:
    return "N/A" if not finite(value) else f"{value/1e9:.2f}B"


def first_estimate_index(values: list, last_date: int | None) -> int | None:
    if last_date is None:
        return None
    for idx in range(last_date + 1, len(values)):
        if values[idx] is not None:
            return idx
    return None


def evidence_row(ticker: str, evidence_type: str, date: str, description: str, url: str, level: str = "A") -> dict:
    return {
        "type": evidence_type,
        "date": date,
        "description": description,
        "source_url": url,
        "source_title": f"StockAnalysis {ticker} forecast",
        "direction": "positive",
        "level": level,
        "origin_id": f"{date}|{url}|{evidence_type}",
        "verification": "Forecast page parsed from embedded public Svelte data",
    }


def collect_ticker(ticker: str, basis_date: str) -> dict:
    url = f"https://stockanalysis.com/stocks/{ticker.lower()}/forecast/"
    html = fetch(url)
    annual_block, quarterly_block = parse_table_blocks(html)
    annual = {
        "fiscal_year": parse_array(annual_block, "fiscalYear"),
        "dates": parse_array(annual_block, "dates"),
        "eps": parse_array(annual_block, "eps"),
        "adjusted_eps": parse_array(annual_block, "adjustedEps"),
        "adjusted_eps_growth": parse_array(annual_block, "adjustedEpsGrowth"),
        "revenue": parse_array(annual_block, "revenue"),
        "revenue_growth": parse_array(annual_block, "revenueGrowth"),
        "analysts": parse_array(annual_block, "analysts"),
        "gross_margin": parse_array(annual_block, "grossMargin"),
        "free_cash_flow": parse_array(annual_block, "freeCashFlow"),
        "operating_income": parse_array(annual_block, "operatingIncome"),
        "last_date": parse_last_date(annual_block),
    }
    quarterly = {
        "fiscal_year": parse_array(quarterly_block, "fiscalYear"),
        "fiscal_quarter": parse_array(quarterly_block, "fiscalQuarter"),
        "dates": parse_array(quarterly_block, "dates"),
        "adjusted_eps": parse_array(quarterly_block, "adjustedEps"),
        "adjusted_eps_growth": parse_array(quarterly_block, "adjustedEpsGrowth"),
        "revenue": parse_array(quarterly_block, "revenue"),
        "revenue_growth": parse_array(quarterly_block, "revenueGrowth"),
        "analysts": parse_array(quarterly_block, "analysts"),
        "gross_margin": parse_array(quarterly_block, "grossMargin"),
        "free_cash_flow": parse_array(quarterly_block, "freeCashFlow"),
        "operating_income": parse_array(quarterly_block, "operatingIncome"),
        "last_date": parse_last_date(quarterly_block),
    }
    eps_chart = parse_eps_chart(html)
    targets = parse_price_targets(html)
    ratings = parse_current_ratings(html)

    fy1_idx = first_estimate_index(annual["adjusted_eps"], annual["last_date"])
    fy2_idx = first_estimate_index(annual["adjusted_eps"][fy1_idx + 1:] if fy1_idx is not None else [], -1)
    if fy2_idx is not None and fy1_idx is not None:
        fy2_idx += fy1_idx + 1

    eps = {}
    evidence = []
    source_date = targets.get("updated") or basis_date
    if fy1_idx is not None:
        fy1_eps = annual["adjusted_eps"][fy1_idx] or annual["eps"][fy1_idx]
        fy1_year = annual["fiscal_year"][fy1_idx] if fy1_idx < len(annual["fiscal_year"]) else None
        fy1_analysts = annual["analysts"][fy1_idx] if fy1_idx < len(annual["analysts"]) else None
        eps.update({
            "fy1_consensus_eps": fy1_eps,
            "fy1_consensus_year": fy1_year,
            "fy1_analyst_count": fy1_analysts or eps_chart.get("analyst_count"),
            "fy1_consensus_eps_basis": f"StockAnalysis forecast annual adjusted EPS for FY{fy1_year}",
            "forward_eps_source_url": url,
            "forward_eps_source_date": source_date,
            "fy1_consensus_source_date": source_date,
            "fy1_point_in_time_status": (
                "POINT_IN_TIME_ON_OR_BEFORE_BASIS" if source_date <= basis_date else "CURRENT_SNAPSHOT_CAPTURED_AFTER_PRICE_BASIS"
            ),
        })
        growth = annual["adjusted_eps_growth"][fy1_idx] if fy1_idx < len(annual["adjusted_eps_growth"]) else None
        if finite(fy1_eps):
            evidence.append(evidence_row(
                ticker,
                "eps_validation",
                source_date,
                f"FY{fy1_year} adjusted EPS consensus {fy1_eps:.2f}; YoY growth {fmt_pct(growth)} ; analysts {fy1_analysts or eps_chart.get('analyst_count') or 'N/A'}",
                url,
            ))
    if fy2_idx is not None:
        fy2_eps = annual["adjusted_eps"][fy2_idx] or annual["eps"][fy2_idx]
        fy2_year = annual["fiscal_year"][fy2_idx] if fy2_idx < len(annual["fiscal_year"]) else None
        eps.update({
            "fy2_consensus_eps": fy2_eps,
            "fy2_consensus_year": fy2_year,
            "fy2_analyst_count": annual["analysts"][fy2_idx] if fy2_idx < len(annual["analysts"]) else None,
            "fy2_consensus_eps_basis": f"StockAnalysis forecast annual adjusted EPS for FY{fy2_year}",
            "fy2_consensus_source_date": source_date,
            "fy2_point_in_time_status": (
                "POINT_IN_TIME_ON_OR_BEFORE_BASIS" if source_date <= basis_date else "CURRENT_SNAPSHOT_CAPTURED_AFTER_PRICE_BASIS"
            ),
        })
    if eps_chart.get("avg"):
        eps.update({
            "ntm_consensus_eps": eps_chart["avg"],
            "ntm_consensus_year": eps_chart["date"][:4],
            "ntm_analyst_count": eps_chart.get("analyst_count"),
            "ntm_consensus_eps_basis": f"StockAnalysis EPS estimates chart for {eps_chart['date']}",
            "ntm_consensus_source_date": source_date,
            "ntm_point_in_time_status": (
                "POINT_IN_TIME_ON_OR_BEFORE_BASIS" if source_date <= basis_date else "CURRENT_SNAPSHOT_CAPTURED_AFTER_PRICE_BASIS"
            ),
            "eps_estimate_low": eps_chart.get("low"),
            "eps_estimate_high": eps_chart.get("high"),
        })

    if fy1_idx is not None:
        revenue = annual["revenue"][fy1_idx] if fy1_idx < len(annual["revenue"]) else None
        revenue_growth = annual["revenue_growth"][fy1_idx] if fy1_idx < len(annual["revenue_growth"]) else None
        analysts = annual["analysts"][fy1_idx] if fy1_idx < len(annual["analysts"]) else None
        if finite(revenue) and finite(revenue_growth):
            evidence.append(evidence_row(
                ticker,
                "revenue_acceleration",
                source_date,
                f"FY{annual['fiscal_year'][fy1_idx]} revenue consensus {fmt_billion(revenue)}; YoY growth {fmt_pct(revenue_growth)} ; analysts {analysts or 'N/A'}",
                url,
            ))

        gross_margin = annual["gross_margin"][fy1_idx] if fy1_idx < len(annual["gross_margin"]) else None
        last_idx = annual["last_date"]
        last_gross_margin = annual["gross_margin"][last_idx] if last_idx is not None and last_idx < len(annual["gross_margin"]) else None
        op_margin = margin(revenue, annual["operating_income"][fy1_idx] if fy1_idx < len(annual["operating_income"]) else None)
        last_revenue = annual["revenue"][last_idx] if last_idx is not None and last_idx < len(annual["revenue"]) else None
        last_op_margin = margin(last_revenue, annual["operating_income"][last_idx] if last_idx is not None and last_idx < len(annual["operating_income"]) else None)
        if finite(gross_margin) and finite(last_gross_margin) and gross_margin >= last_gross_margin:
            evidence.append(evidence_row(
                ticker,
                "margin_improvement",
                source_date,
                f"FY consensus gross margin {fmt_pct(gross_margin)} vs last actual {fmt_pct(last_gross_margin)}; operating margin {fmt_pct(op_margin)} vs {fmt_pct(last_op_margin)}",
                url,
                "B",
            ))

        fcf = annual["free_cash_flow"][fy1_idx] if fy1_idx < len(annual["free_cash_flow"]) else None
        last_fcf = annual["free_cash_flow"][last_idx] if last_idx is not None and last_idx < len(annual["free_cash_flow"]) else None
        fcf_margin = margin(revenue, fcf)
        last_fcf_margin = margin(last_revenue, last_fcf)
        if finite(fcf_margin) and (last_fcf_margin is None or fcf_margin >= last_fcf_margin):
            evidence.append(evidence_row(
                ticker,
                "fcf_improvement",
                source_date,
                f"FY consensus FCF margin {fmt_pct(fcf_margin)} vs last actual {fmt_pct(last_fcf_margin)} ; FCF {fmt_billion(fcf)}",
                url,
                "B",
            ))

    return {
        "ticker": ticker,
        "collection_status": "AVAILABLE" if eps else "PUBLIC_CONSENSUS_UNAVAILABLE",
        "forecast_url": url,
        "source": "StockAnalysis forecast embedded data",
        "source_date": source_date,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "eps": eps,
        "targets": targets,
        "ratings": ratings,
        "evidence": evidence,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tickers", nargs="+", required=True)
    parser.add_argument("--basis-date", required=True)
    parser.add_argument("--out")
    parser.add_argument("--sleep", type=float, default=0.3)
    args = parser.parse_args()
    out = pathlib.Path(args.out) if args.out else BASE / f"data/us_forward_eps_evidence_{args.basis_date.replace('-', '')}.json"
    payload = {
        "basis_date": args.basis_date,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "source": "StockAnalysis forecast pages",
        "tickers": {},
    }
    for ticker in args.tickers:
        try:
            payload["tickers"][ticker] = collect_ticker(ticker, args.basis_date)
            print("ok", ticker)
        except Exception as exc:  # noqa: BLE001
            payload["tickers"][ticker] = {
                "ticker": ticker,
                "collection_status": "FETCH_FAILED",
                "error": str(exc),
                "captured_at": datetime.now(timezone.utc).isoformat(),
            }
            print("err", ticker, exc)
        time.sleep(args.sleep)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(out)


if __name__ == "__main__":
    main()
