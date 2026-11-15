# Backend engineering

FastAPI is the only HTTP process. SQLite is local persistence; analytics and health-assistant code is imported through `backend.app.services.assessments` and never deployed separately.

## Database workflow

```powershell
python -m alembic upgrade head
python -m backend.scripts.seed_synthetic
python -m uvicorn backend.app.main:app --reload --port 8000
```

The seed command uses deterministic UUIDs and is idempotent. Its records are fictional and explicitly labeled synthetic. Runtime `.db`/`.sqlite3` files remain ignored. Create future migrations with `python -m alembic revision --autogenerate -m "description"`, inspect the generated operations, and test upgrades against a backup before applying them to an existing database.

Startup still calls `create_all` for a zero-setup hackathon experience. It creates missing tables only and does not migrate existing tables; Alembic remains required for schema evolution.

## Security limitations

The MVP has no authentication, authorization, encryption-at-rest, audit trail, or clinical governance. Bind the service only to a trusted local interface and use synthetic data. These controls must be designed before any real or identifiable health information is used.

