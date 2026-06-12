# BigQuery Project

Python project with BigQuery service-account authentication and GitHub Actions CI/CD.

## Project structure

```
.
├── .github/workflows/ci.yml   # CI/CD pipeline
├── credentials/               # Local service account key (gitignored)
├── scripts/
│   └── test_connection.py     # Connection smoke test
├── src/bigquery_client/       # Reusable BigQuery client
├── tests/                     # Unit tests
├── .env.example
├── requirements.txt
└── requirements-dev.txt
```

## Local setup

### 1. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

### 2. Add your service account key

1. In [Google Cloud Console](https://console.cloud.google.com/), create or download a service account JSON key.
2. Save it locally (never commit it):

```bash
mkdir -p credentials
cp /path/to/your-key.json credentials/service-account.json
```

3. Copy the example env file and update values:

```bash
cp .env.example .env
```

Your `.env` should look like:

```env
GCP_PROJECT_ID=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=credentials/service-account.json
```

### 3. Test the connection

```bash
python scripts/test_connection.py
```

### 4. Use the client in your code

```python
from bigquery_client import create_bigquery_client, run_query

client = create_bigquery_client()
rows = run_query(client, "SELECT 1 AS ok")
print(list(rows))
```

## Required IAM roles

Your service account needs at least:

- `roles/bigquery.user` — run queries
- `roles/bigquery.dataViewer` — read datasets/tables (adjust as needed)

## CI/CD with GitHub Actions

The workflow in `.github/workflows/ci.yml` does two things:

1. **On every push/PR** — runs unit tests (no GCP credentials needed).
2. **On push to main** — runs a live BigQuery smoke test using GitHub secrets.

### GitHub secrets to add

In your repo: **Settings → Secrets and variables → Actions → New repository secret**

| Secret | Value |
|--------|-------|
| `GCP_SA_KEY` | Full contents of your service account JSON file |
| `GCP_PROJECT_ID` | Your GCP project ID |

### Push to GitHub

```bash
git init
git add .
git commit -m "Initial BigQuery project with CI/CD"
git branch -M main
git remote add origin https://github.com/YOUR_USER/YOUR_REPO.git
git push -u origin main
```

After the first push to `main`, check the **Actions** tab to confirm tests and the BigQuery smoke test pass.

## Security notes

- Never commit `credentials/` or `.env` — both are in `.gitignore`.
- Prefer GitHub Secrets for CI instead of storing keys in the repo.
- Rotate service account keys if one is ever exposed.
