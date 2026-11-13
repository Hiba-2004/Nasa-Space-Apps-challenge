# ASTRAVITAL

ASTRAVITAL is an offline-capable, explainable health monitoring and decision-support prototype for long-duration missions. This repository is an early NASA Space Apps Challenge 2026 scaffold, not a medical device. It does **not** diagnose conditions, predict validated clinical risk, or replace qualified medical judgment. All bundled people, readings, and scenarios are synthetic.

## Repository map and ownership

| Area | Owner | Purpose |
|---|---|---|
| `frontend/` | Member 1 | Next.js, TypeScript, Tailwind CSS, Recharts UI |
| `backend/` | Member 2 | The only FastAPI server, SQLite persistence, canonical schemas |
| `analytics/` | Member 3 | Importable analysis package; no server |
| `health_assistant/` | Member 4 | Importable, evidence-linked guidance package; no server |
| `contracts/`, `sample_data/`, `docs/` | Shared | Examples, synthetic fixtures, specifications, decisions |

## Windows PowerShell setup

Prerequisites: Python 3.11+, Node.js 20+, and npm. Once dependencies are installed, the application requires no network or cloud service.

```powershell
git clone <repository-url>
Set-Location Nasa-Space-Apps-challenge
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
Set-Location frontend
npm.cmd install
Copy-Item .env.example .env.local
Set-Location ..
```

Start both development processes from the repository root:

```powershell
.\scripts\dev.ps1
```

Alternatively, use two terminals: `python -m uvicorn backend.app.main:app --reload --port 8000` and `npm.cmd --prefix frontend run dev`. Open http://localhost:3000; API docs are at http://localhost:8000/docs.

## Checks

```powershell
python -m pytest
python -m ruff check backend analytics health_assistant
npm.cmd --prefix frontend run lint
npm.cmd --prefix frontend run typecheck
npm.cmd --prefix frontend run build
```

The generated OpenAPI document is canonical. With the Python environment active, refresh the checked-in snapshot using `python scripts/export_openapi.py`.

## Parallel development workflow

Each member works primarily inside their owned directory and coordinates shared model changes through `backend/app/schemas.py`, `contracts/`, and a focused PR. Analytics and assistant owners program against typed internal interfaces and fixtures, so neither needs the API process running. The frontend owner uses `contracts/examples/` or the live OpenAPI endpoint. The backend owner integrates packages through adapters in the assessment route. Shared contract changes should land first in a small PR; downstream branches then rebase.

Branches use `feature/<area>-<short-description>`, `fix/<area>-<short-description>`, or `docs/<short-description>` (for example, `feature/analytics-trend-summary`). Keep PRs small, link the issue, describe contract/database effects, list checks run, request review from the affected owner, and use squash merge after CI and review. Never commit `.env`, local databases, real crew health data, or generated dependency folders.

See [architecture](docs/ARCHITECTURE.md), [API contract](docs/API_CONTRACT.md), [integration plan](docs/INTEGRATION_PLAN.md), and [decisions](docs/DECISIONS.md).

