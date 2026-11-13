# API contract

Base path: `/api/v1`. JSON is used for requests and responses. The generated `contracts/openapi.json` is canonical; this document is its readable guide. Validation errors use FastAPI's standard `422` response and unknown astronaut IDs return `404`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Process/API version health check |
| GET, POST | `/astronauts` | List or create astronaut profiles |
| GET | `/astronauts/{id}` | Read one profile |
| GET, POST | `/astronauts/{id}/measurements` | List or record measurements |
| GET, POST | `/astronauts/{id}/checkins` | List or record self-reports |
| POST, GET | `/astronauts/{id}/assessments` | Generate or list assessments |
| GET | `/astronauts/{id}/alerts` | List alerts (empty until evidence rules exist) |
| GET | `/astronauts/{id}/report` | Aggregate profile, history, and assessments |
| GET | `/mission-context` | Read simulated mission conditions |

POST collection endpoints return `201`. Collection GET endpoints return arrays, including an empty array when no record exists. A missing value is encoded as `null` only where the schema permits it or omitted because no observation exists; it is never replaced by zero or a normal label.

## MVP measurements

| Metric | Required unit | Meaning |
|---|---|---|
| `resting_heart_rate` | `bpm` | Beats per minute |
| `sleep_hours` | `h` | Hours |
| `body_temperature` | `Cel` | Degrees Celsius |
| `blood_pressure_systolic` | `mmHg` | Systolic component |
| `blood_pressure_diastolic` | `mmHg` | Diastolic component |

Example create request:

```json
{
  "measured_at": "2026-10-01T08:00:00Z",
  "metric": "resting_heart_rate",
  "value": 62,
  "unit": "bpm",
  "source": "synthetic manual entry"
}
```

Mood and fatigue use a self-reported integer scale from 1 through 5. The scale is an input vocabulary, not a clinical threshold. At least one check-in field is required. Assessment creation accepts no body: the backend reads current history, calls the two internal package interfaces, and stores the transparent result.

## Compatibility

Additive optional fields may be introduced within v1. Renaming, removing, changing units, or changing meaning requires a new API version and an architecture decision record. Regenerate the OpenAPI snapshot after every route/schema change and update examples in the same PR.

