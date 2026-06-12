#!/usr/bin/env python3
"""Verify local BigQuery connectivity."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bigquery_client import create_bigquery_client, list_datasets  # noqa: E402


def main() -> int:
    try:
        client = create_bigquery_client()
    except (FileNotFoundError, ValueError) as exc:
        print(f"Connection setup failed: {exc}", file=sys.stderr)
        print(
            "\nPlace your service account JSON at credentials/service-account.json "
            "or set GOOGLE_APPLICATION_CREDENTIALS in .env",
            file=sys.stderr,
        )
        return 1

    print(f"Connected to BigQuery project: {client.project}")

    datasets = list_datasets(client)
    print(f"Found {len(datasets)} dataset(s):")
    for dataset_id in datasets:
        print(f"  - {dataset_id}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
