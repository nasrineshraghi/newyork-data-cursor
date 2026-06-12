#!/usr/bin/env python3
"""Run a few Citi Bike exploration queries and optionally save CSV reports."""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bigquery_client import create_bigquery_client, get_project_id, run_query  # noqa: E402

DEFAULT_TABLE = "{project}.data_engineering_int.newyork_citibike_trips"
REPORT_YEAR = 2018


def get_queries(table: str) -> dict[str, str]:
    return {
        "busiest_day": f"""
            SELECT
              DATE(starttime) AS trip_date,
              COUNT(*) AS total_trips
            FROM `{table}`
            WHERE EXTRACT(YEAR FROM starttime) = {REPORT_YEAR}
            GROUP BY trip_date
            ORDER BY total_trips DESC
            LIMIT 1
        """,
        "top_stations": f"""
            SELECT
              start_station_name,
              COUNT(*) AS total_trips
            FROM `{table}`
            WHERE EXTRACT(YEAR FROM starttime) = {REPORT_YEAR}
              AND start_station_name IS NOT NULL
            GROUP BY start_station_name
            ORDER BY total_trips DESC
            LIMIT 5
        """,
        "trips_by_weekday": f"""
            SELECT
              FORMAT_DATE('%A', DATE(starttime)) AS weekday,
              EXTRACT(DAYOFWEEK FROM DATE(starttime)) AS day_number,
              COUNT(*) AS total_trips
            FROM `{table}`
            WHERE EXTRACT(YEAR FROM starttime) = {REPORT_YEAR}
            GROUP BY weekday, day_number
            ORDER BY day_number
        """,
    }


def print_section(title: str, rows: list[dict]) -> None:
    print(f"\n=== {title} ===")
    if not rows:
        print("No rows returned.")
        return

    headers = list(rows[0].keys())
    widths = {
        key: max(len(key), *(len(str(row[key])) for row in rows))
        for key in headers
    }

    header_line = "  ".join(key.ljust(widths[key]) for key in headers)
    print(header_line)
    print("  ".join("-" * widths[key] for key in headers))

    for row in rows:
        print("  ".join(str(row[key]).ljust(widths[key]) for key in headers))


def rows_to_dicts(rows) -> list[dict]:
    return [dict(row.items()) for row in rows]


def save_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Explore Citi Bike trip patterns")
    parser.add_argument(
        "--output",
        type=Path,
        help="Folder to save CSV files (optional)",
    )
    args = parser.parse_args()

    try:
        client = create_bigquery_client()
    except (FileNotFoundError, ValueError) as exc:
        print(f"Connection setup failed: {exc}", file=sys.stderr)
        return 1

    project_id = get_project_id()
    table = DEFAULT_TABLE.format(project=project_id)
    queries = get_queries(table)

    print(f"Project: {project_id}")
    print(f"Table:   data_engineering_int.newyork_citibike_trips")
    print(f"Year:    {REPORT_YEAR}")

    for name, sql in queries.items():
        rows = rows_to_dicts(run_query(client, sql))
        title = name.replace("_", " ").title()
        print_section(title, rows)

        if args.output:
            suffix = date.today().isoformat()
            save_csv(args.output / f"{name}_{suffix}.csv", rows)

    if args.output:
        print(f"\nSaved CSV files to: {args.output.resolve()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
