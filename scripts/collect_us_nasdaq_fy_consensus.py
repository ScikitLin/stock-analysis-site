#!/usr/bin/env python3
"""Merge Nasdaq FY1/FY2 analyst EPS consensus into a US evidence snapshot."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import time
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ADR_USD_REQUIRED = {"ASML", "TSM"}


def fetch_json(url: str) -> dict[str, Any]:
    completed = subprocess.run(
        [
            "curl", "-fsSL", "--max-time", "30",
            "-A", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "-H", "Accept: application/json, text/plain, */*",
            "-H", "Origin: https://www.nasdaq.com",
            url,
        ],
        check=True,
        capture_output=True,
    )
    return json.loads(completed.stdout)


def number(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def fiscal_year(label: str | None) -> str | None:
    if not label:
        return None
    token = str(label).strip().split()[-1]
    return token if token.isdigit() and len(token) == 4 else str(label).strip()


def merge_ticker(ticker: str, entry: dict[str, Any], basis_date: str) -> dict[str, Any]:
    endpoint = f"https://api.nasdaq.com/api/analyst/{ticker}/earnings-forecast"
    payload = fetch_json(endpoint)
    rows = (((payload.get("data") or {}).get("yearlyForecast") or {}).get("rows") or [])
    valid = [row for row in rows if number(row.get("consensusEPSForecast")) is not None]
    if len(valid) < 2:
        raise ValueError(f"Nasdaq returned {len(valid)} valid annual consensus rows")

    eps = entry.setdefault("eps", {})
    prior_fy1 = number(eps.get("fy1_consensus_eps"))
    source_url = f"https://www.nasdaq.com/market-activity/stocks/{ticker.lower()}/earnings"
    captured_date = date.today().isoformat()
    for label, row in (("fy1", valid[0]), ("fy2", valid[1])):
        value = number(row.get("consensusEPSForecast"))
        year = fiscal_year(row.get("fiscalEnd"))
        count = number(row.get("noOfEstimates"))
        values = {
            f"{label}_consensus_eps": value,
            f"{label}_consensus_year": year,
            f"{label}_analyst_count": count,
            f"{label}_consensus_eps_basis": (
                f"Nasdaq annual consensus EPS captured {captured_date} for fiscal year ending {row.get('fiscalEnd')}; "
                f"high {row.get('highEPSForecast')}, low {row.get('lowEPSForecast')}"
            ),
            f"{label}_consensus_source_url": source_url,
            f"{label}_consensus_source_date": captured_date,
            f"{label}_point_in_time_status": (
                "POINT_IN_TIME_ON_OR_BEFORE_BASIS"
                if captured_date <= basis_date
                else "CURRENT_SNAPSHOT_CAPTURED_AFTER_PRICE_BASIS"
            ),
        }
        if label == "fy1" and prior_fy1 is not None and ticker not in ADR_USD_REQUIRED:
            eps.update({f"nasdaq_{key}": value for key, value in values.items()})
        else:
            eps.update(values)
            if label == "fy1" and ticker in ADR_USD_REQUIRED:
                eps["fy1_currency_alignment"] = "Nasdaq ADR USD EPS selected; local-currency StockAnalysis EPS retained only as cross-check"

    eps.update(
        {
            "nasdaq_fy_consensus_captured_at": datetime.now(timezone.utc).isoformat(),
            "nasdaq_fy_consensus_endpoint": endpoint,
            "nasdaq_yearly_rows": valid[:3],
        }
    )
    if ticker in ADR_USD_REQUIRED:
        eps["stockanalysis_ntm_crosscheck_eps"] = eps.get("ntm_consensus_eps")
        eps["ntm_consensus_eps"] = None
        eps["ntm_consensus_year"] = None
        eps["ntm_analyst_count"] = None
        eps["ntm_consensus_eps_basis"] = None
        eps["ntm_consensus_status"] = "FISCAL_CURRENCY_MISMATCH"
    nasdaq_fy1 = number(eps.get("nasdaq_fy1_consensus_eps") or eps.get("fy1_consensus_eps"))
    if prior_fy1 and nasdaq_fy1:
        gap = nasdaq_fy1 / prior_fy1 - 1
        eps["stockanalysis_fy1_crosscheck_eps"] = prior_fy1
        eps["fy1_cross_source_gap_pct"] = gap * 100
        if abs(gap) > 0.15:
            eps["fy1_cross_source_warning"] = (
                f"Nasdaq FY1 differs from StockAnalysis FY1 by {gap:.1%}; "
                "check GAAP/non-GAAP and fiscal-year definitions before valuation use"
            )
    return entry


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tickers", nargs="+", required=True)
    parser.add_argument("--basis-date", required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--sleep", type=float, default=0.12)
    args = parser.parse_args()

    source = args.input if args.input.is_absolute() else ROOT / args.input
    target_arg = args.out or args.input
    target = target_arg if target_arg.is_absolute() else ROOT / target_arg
    payload = json.loads(source.read_text(encoding="utf-8"))
    if payload.get("basis_date") != args.basis_date:
        raise ValueError(f"evidence basis {payload.get('basis_date')} != {args.basis_date}")

    rows = payload.setdefault("tickers", {})
    for ticker in args.tickers:
        ticker = ticker.upper()
        entry = rows.setdefault(ticker, {"ticker": ticker})
        try:
            merge_ticker(ticker, entry, args.basis_date)
            print("ok", ticker, flush=True)
        except Exception as exc:  # noqa: BLE001
            entry["nasdaq_fy_consensus_error"] = str(exc)
            print("err", ticker, exc, flush=True)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        time.sleep(max(args.sleep, 0))

    payload["fy_consensus_source"] = "Nasdaq annual analyst earnings forecast; StockAnalysis FY1 retained as cross-check"
    payload["fy_consensus_refreshed_at"] = datetime.now(timezone.utc).isoformat()
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()
