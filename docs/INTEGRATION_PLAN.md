# Integration plan

## Package contracts

Analytics implements:

```python
analyze_health(history, baseline, context) -> list[structured finding]
```

The health assistant implements:

```python
generate_guidance(findings, checkin, context) -> list[evidence-linked action]
```

The backend is the adapter: it loads records, serializes neutral dictionaries, invokes analytics, passes its findings to guidance, validates the combined response, and persists an assessment. Packages remain deterministic and separately testable.

## Delivery order

1. Agree on schema/OpenAPI changes in a small shared-contract PR.
2. Analytics and guidance update their unit tests against synthetic dictionaries.
3. Backend adds integration and persistence behavior, then refreshes OpenAPI.
4. Frontend updates typed client models and accessible states for loading, empty data, and errors.
5. Run Python tests/lint and frontend lint/type/build checks before merge.

## Working without blocking

Member 1 can use checked-in JSON examples while Member 2 develops routes. Members 3 and 4 depend only on their function signatures and local fixtures; Member 4 can consume saved finding fixtures without waiting for analytic logic. Member 2 can use package placeholders while integrating storage. Avoid editing another owner's implementation unless paired; put cross-cutting model proposals in `contracts/` and request both affected owners.

Resolve conflicts by treating generated OpenAPI as output: merge schema/route source, regenerate once, then validate examples. Do not hand-merge generated JSON. CI should eventually run the commands documented in the README on every PR.

