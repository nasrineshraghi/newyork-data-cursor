#!/usr/bin/env python3
"""Count unique bikes used per day from Citi Bike trip data."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bigquery_client import create_bigquery_client, get_project_id, run_query  # noqa: E402

DEFAULT_TABLE = "{project}.data_engineering_int.newyork_citibike_trips"


def build_query(table: str, limit: int | None, start_date: str | None, end_date: str | None) -> str:
    date_filter = ""
    if start_date:
        date_filter += f" AND DATE(starttime) >= '{start_date}'"
    if end_date:
        date_filter += f" AND DATE(starttime) <= '{end_date}'"

    limit_clause = f"\nLIMIT {limit}" if limit else ""

    return f"""
SELECT
  DATE(starttime) AS trip_date,
  COUNT(DISTINCT bikeid) AS unique_bikes,
  COUNT(*) AS total_trips
FROM `{table}`
WHERE TRUE{date_filter}
GROUP BY trip_date
ORDER BY trip_date
{limit_clause}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Unique Citi Bike bikes per day")
    parser.add_argument("--limit", type=int, default=20, help="Max days to show (default: 20)")
    parser.add_argument("--start-date", help="Filter from date, e.g. 2018-01-01")
    parser.add_argument("--end-date", help="Filter to date, e.g. 2018-05-31")
    parser.add_argument("--all", action="store_true", help="Show all days (no limit)")
    args = parser.parse_args()

    try:
        client = create_bigquery_client()
    except (FileNotFoundError, ValueError) as exc:
        print(f"Connection setup failed: {exc}", file=sys.stderr)
        return 1

    project_id = get_project_id()
    table = DEFAULT_TABLE.format(project=project_id)
    limit = None if args.all else args.limit
    sql = build_query(table, limit, args.start_date, args.end_date)

    print(f"Project: {project_id}")
    print(f"Table:   data_engineering_int.newyork_citibike_trips")
    print()
    print(f"{'Date':<12} {'Unique bikes':>14} {'Total trips':>14}")
    print("-" * 42)

    row_count = 0
    for row in run_query(client, sql):
        print(f"{row.trip_date!s:<12} {row.unique_bikes:>14,} {row.total_trips:>14,}")
        row_count += 1

    if row_count == 0:
        print("No rows returned.")
        return 1

    print()
    print(f"Showing {row_count} day(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
