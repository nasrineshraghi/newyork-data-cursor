"""Tests for BigQuery client helpers."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from bigquery_client.client import create_bigquery_client, get_project_id, list_datasets


def test_get_project_id_from_env(monkeypatch):
    monkeypatch.setenv("GCP_PROJECT_ID", "my-test-project")
    assert get_project_id() == "my-test-project"


def test_get_project_id_explicit():
    assert get_project_id("override-project") == "override-project"


def test_get_project_id_missing(monkeypatch):
    monkeypatch.delenv("GCP_PROJECT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)

    with pytest.raises(ValueError, match="Set GCP_PROJECT_ID"):
        get_project_id()


@patch("bigquery_client.client.bigquery.Client")
@patch("bigquery_client.client.service_account.Credentials.from_service_account_file")
def test_create_bigquery_client_with_key(mock_from_file, mock_client, tmp_path, monkeypatch):
    key_path = tmp_path / "service-account.json"
    key_path.write_text(
        '{"type":"service_account","project_id":"from-key-project"}',
        encoding="utf-8",
    )
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", str(key_path))
    monkeypatch.delenv("GCP_PROJECT_ID", raising=False)

    mock_credentials = MagicMock(project_id="from-key-project")
    mock_from_file.return_value = mock_credentials

    create_bigquery_client()

    mock_from_file.assert_called_once_with(str(key_path))
    mock_client.assert_called_once_with(
        credentials=mock_credentials,
        project="from-key-project",
    )


def test_list_datasets():
    mock_client = MagicMock()
    mock_client.list_datasets.return_value = [
        MagicMock(dataset_id="analytics"),
        MagicMock(dataset_id="staging"),
    ]

    assert list_datasets(mock_client) == ["analytics", "staging"]
