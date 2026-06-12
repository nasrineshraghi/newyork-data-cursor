"""BigQuery client helpers."""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account

load_dotenv()


def get_credentials_path() -> Path | None:
    """Return the service account key path from env, if set."""
    raw_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not raw_path:
        return None
    return Path(raw_path).expanduser().resolve()


def get_project_id(explicit_project_id: str | None = None) -> str:
    """Resolve the GCP project ID from args, env, or the service account key."""
    if explicit_project_id:
        return explicit_project_id

    env_project_id = os.getenv("GCP_PROJECT_ID")
    if env_project_id:
        return env_project_id

    credentials_path = get_credentials_path()
    if credentials_path and credentials_path.exists():
        with credentials_path.open(encoding="utf-8") as key_file:
            key_data = json.load(key_file)
        project_from_key = key_data.get("project_id")
        if project_from_key:
            return project_from_key

    raise ValueError(
        "Set GCP_PROJECT_ID or GOOGLE_APPLICATION_CREDENTIALS with a valid "
        "service account JSON file."
    )


def create_bigquery_client(
    credentials_path: str | Path | None = None,
    project_id: str | None = None,
) -> bigquery.Client:
    """Create an authenticated BigQuery client using a service account key."""
    resolved_path = (
        Path(credentials_path).expanduser().resolve()
        if credentials_path
        else get_credentials_path()
    )
    resolved_project_id = get_project_id(project_id)

    if resolved_path and resolved_path.exists():
        credentials = service_account.Credentials.from_service_account_file(
            str(resolved_path)
        )
        return bigquery.Client(
            credentials=credentials,
            project=resolved_project_id,
        )

    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        raise FileNotFoundError(
            f"Service account key not found: {resolved_path}"
        )

    # Fallback for environments that inject credentials another way (e.g. GCE, CI).
    return bigquery.Client(project=resolved_project_id)


def list_datasets(client: bigquery.Client, max_results: int = 25) -> list[str]:
    """Return dataset IDs visible to the authenticated client."""
    return [
        dataset.dataset_id
        for dataset in client.list_datasets(max_results=max_results)
    ]


def run_query(client: bigquery.Client, sql: str) -> bigquery.table.RowIterator:
    """Run a SQL query and return the result iterator."""
    job = client.query(sql)
    return job.result()
