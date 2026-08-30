#!/usr/bin/env python3
"""Create a fresh Taiwan FY consensus snapshot from Yahoo earningsTrend.

The output never reads prior analyst estimates.  It records the capture date
separately from the formal-close price basis and retains analyst counts, ranges,
revision fields, and the direct source URL.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]


def curl(args: list[str]) -> bytes:
    completed = subprocess.run(
        ["curl", "-sSL", "--retry", "2", "--retry-all-errors", "--max-time", "30", *args],
        check=True,
        capture_output=True,
    )
    return completed.stdout


def raw(value):
    return value.get("raw") if isinstance(value, dict) else value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stocks", required=True)
    parser.add_argument("--basis-date", required=True)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    codes = [code.strip() for code in args.stocks.split(",") if code.strip()]
    candidate_path = args.candidates if args.candidates.is_absolute() else ROOT / args.candidates
    target = args.out if args.out.is_absolute() else ROOT / args.out
    with candidate_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = {row["股票代號 / Ticker"]: row for row in csv.DictReader(handle)}

    capture_date = date.today().isoformat()
    payload = {
        "basis_date": args.basis_date,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "method": "fresh Yahoo earningsTrend API snapshot; no prior analyst estimates reused",
        "tickers": {},
    }
    with tempfile.TemporaryDirectory(prefix="tw_yahoo_consensus_") as tmp:
        cookie = Path(tmp) / "cookie.txt"
        curl(["-c", str(cookie), "-A", "Mozilla/5.0", "https://fc.yahoo.com", "-o", "/dev/null"])
        crumb = curl(["-b", str(cookie), "-A", "Mozilla/5.0", "https://query1.finance.yahoo.com/v1/test/getcrumb"]).decode().strip()
        for code in codes:
            row = rows.get(code) or {}
            market = row.get("市場 / Market")
            suffix = "TW" if market == "TWSE" else "TWO"
            symbol = f"{code}.{suffix}"
            source_url = f"https://finance.yahoo.com/quote/{symbol}/analysis/"
            endpoint = (
                f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}"
                f"?modules=earningsTrend&crumb={quote(crumb)}"
            )
            entry = {
                "stock_id": code,
                "stock_name": row.get("公司名稱 / Company") or "",
                "evidence_items": [],
                "eps_estimates": {"consensus": {}, "broker": {}},
            }
            try:
                body = curl(["-b", str(cookie), "-A", "Mozilla/5.0", endpoint])
                result = (((json.loads(body).get("quoteSummary") or {}).get("result") or [{}])[0])
                trends = ((result.get("earningsTrend") or {}).get("trend") or [])
                annual = {item.get("period"): item for item in trends if item.get("period") in {"0y", "+1y"}}
                for period, item in annual.items():
                    year = str(item.get("endDate") or "")[:4]
                    estimate = item.get("earningsEstimate") or {}
                    avg = raw(estimate.get("avg"))
                    count = raw(estimate.get("numberOfAnalysts"))
                    if not year or avg is None or count is None or int(count) < 3:
                        continue
                    entry["eps_estimates"]["consensus"][year] = {
                        "median_eps": float(avg),
                        "analyst_count": int(count),
                        "low_eps": raw(estimate.get("low")),
                        "high_eps": raw(estimate.get("high")),
                        "source": "Yahoo Finance earningsTrend analyst consensus",
                        "source_url": source_url,
                        "source_date": capture_date,
                        "source_age_days": 0,
                        "point_in_time_status": (
                            "POINT_IN_TIME_ON_OR_BEFORE_BASIS"
                            if capture_date <= args.basis_date
                            else "CURRENT_SNAPSHOT_CAPTURED_AFTER_PRICE_BASIS"
                        ),
                        "period": period,
                    }
                    trend = item.get("epsTrend") or {}
                    evidence = {
                        "id": f"yahoo-{code}-{year}-{capture_date}",
                        "evidence_type": "forward_eps_consensus",
                        "estimate_year": int(year),
                        "eps": float(avg),
                        "analyst_count": int(count),
                        "source_date": capture_date,
                        "source_age_days": 0,
                        "source_title": f"Yahoo Finance {symbol} earningsTrend {period}",
                        "source_url": source_url,
                        "source_nature": "aggregated analyst consensus",
                        "source_quality": "A",
                        "raw_text_excerpt": (
                            f"{year} EPS average {avg}; analysts {count}; low {raw(estimate.get('low'))}; "
                            f"high {raw(estimate.get('high'))}; 30d ago {raw(trend.get('30daysAgo'))}"
                        ),
                        "used_for_EPS_used": True,
                        "excluded_reason": "",
                    }
                    entry["evidence_items"].append(evidence)
                status = "AVAILABLE" if entry["eps_estimates"]["consensus"] else "PUBLIC_CONSENSUS_UNAVAILABLE"
                error = ""
            except Exception as exc:  # noqa: BLE001
                status = "FETCH_FAILED"
                error = str(exc)
            entry["eps_collection"] = {
                "collection_status": status,
                "searched_at": capture_date,
                "basis_date": args.basis_date,
                "source_url": source_url,
                "point_in_time_status": (
                    "POINT_IN_TIME_ON_OR_BEFORE_BASIS"
                    if capture_date <= args.basis_date
                    else "CURRENT_SNAPSHOT_CAPTURED_AFTER_PRICE_BASIS"
                ),
                "error_message": error,
                "rules_path": "docs/tw_eps_used_rules.md",
            }
            payload["tickers"][code] = entry
            print(code, status, sorted(entry["eps_estimates"]["consensus"]), flush=True)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()
