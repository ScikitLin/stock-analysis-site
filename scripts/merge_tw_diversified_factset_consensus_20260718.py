#!/usr/bin/env python3
"""Merge verified CNYES/FactSet snapshots for the diversified Taiwan reports."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path


AS_OF = date(2026, 7, 18)
PATH = Path("data/tw_full_research_evidence.json")

# code: name, source date, analysts, 2026E, previous 2026E, 2027E, 2028E, URL
ROWS = {
    "6491": ("晶碩", "2026-05-25", 7, 24.86, 23.75, 27.52, None, "https://news.cnyes.com/news/id/6470056"),
    "6782": ("視陽", "2026-06-05", 7, 17.37, 16.94, 21.09, 21.47, "https://news.cnyes.com/news/print/6486413"),
    "6472": ("保瑞", "2026-06-05", 8, 20.28, 20.00, 40.30, None, "https://news.cnyes.com/news/id/6484688"),
    "6446": ("藥華藥", "2026-04-09", 8, 22.72, 22.32, 39.36, 39.85, "https://news.cnyes.com/news/id/6414423"),
    "1795": ("美時", "2026-06-29", 8, 16.31, 15.79, 25.72, None, "https://news.cnyes.com/news/id/6516222"),
    "8464": ("億豐", "2026-06-15", 8, 25.48, 25.31, 27.48, 29.85, "https://news.cnyes.com/news/id/6500278"),
    "2884": ("玉山金", "2026-05-11", 11, 2.42, 2.40, 2.54, 2.78, "https://news.cnyes.com/news/id/6452355"),
    "9914": ("美利達", "2026-07-10", 11, 5.11, 5.02, 6.53, 7.47, "https://news.cnyes.com/news/id/6530519"),
    "2603": ("長榮", "2026-06-24", 10, 24.30, 22.87, 21.69, 20.50, "https://news.cnyes.com/news/id/6511002"),
}


def main() -> None:
    payload = json.loads(PATH.read_text(encoding="utf-8"))
    tickers = payload.setdefault("tickers", {})
    for code, row in ROWS.items():
        name, source_date, count, current, previous, next_eps, future, url = row
        age = (AS_OF - date.fromisoformat(source_date)).days
        entry = tickers.setdefault(code, {"stock_id": code, "stock_name": name})
        consensus = entry.setdefault("eps_estimates", {}).setdefault("consensus", {})
        values = {2026: current, 2027: next_eps, 2028: future}
        for year, value in values.items():
            if value is None:
                continue
            consensus[str(year)] = {
                "median_eps": value,
                "analyst_count": count,
                "source": "FactSet consensus via CNYES",
                "source_note": f"FactSet {count} analyst consensus; snapshot {source_date}",
                "source_date": source_date,
                "source_age_days": age,
                "source_url": url,
            }
        prior = [
            item for item in entry.setdefault("evidence_items", [])
            if not str(item.get("id", "")).startswith("diversified-factset-")
        ]
        direction = "up" if current > previous else "down" if current < previous else "flat"
        for year, value in values.items():
            if value is None:
                continue
            prior.append({
                "id": f"diversified-factset-{code}-{year}-{source_date}",
                "evidence_type": "forward_eps_consensus",
                "estimate_type": "consensus_median",
                "estimate_year": year,
                "eps": value,
                "previous_eps": previous if year == 2026 else None,
                "analyst_count": count,
                "source_date": source_date,
                "source_age_days": age,
                "source_title": f"{name} FactSet {year} EPS consensus",
                "raw_text_excerpt": f"{year} EPS median {value}; {count} analysts; current-year revision {direction}",
                "source_nature": "aggregated analyst consensus",
                "source_quality": "A",
                "source_url": url,
            })
        entry["evidence_items"] = prior
        entry["eps_collection"] = {
            "collection_status": "done",
            "searched_at": AS_OF.isoformat(),
            "query_count": 1,
            "best_source_quality": "A",
            "duplicate_count": 0,
            "needs_manual_review": False,
            "error_message": "",
            "rules_path": "docs/tw_eps_used_rules.md",
            "method": "targeted verified CNYES/FactSet snapshot",
        }
    PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"merged {len(ROWS)} verified diversified FactSet snapshots")


if __name__ == "__main__":
    main()
