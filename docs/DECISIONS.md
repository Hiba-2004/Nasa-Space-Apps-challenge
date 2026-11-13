# Architecture decisions

## ADR-001: Modular monolith

**Status:** accepted. One FastAPI application imports analytics and guidance packages. This minimizes offline operations, deployment complexity, and contract drift. Separate services are explicitly out of scope.

## ADR-002: SQLite local persistence

**Status:** accepted. SQLite supports the local/offline MVP with no service dependency. SQLAlchemy keeps persistence testable. The database file is not source-controlled. Migration tooling is deferred until schemas begin evolving.

## ADR-003: Generated OpenAPI is canonical

**Status:** accepted. Pydantic/FastAPI source generates the machine contract, which is checked in for review and offline client work. Markdown and examples are supporting explanations and must remain consistent.

## ADR-004: Transparent placeholders, no medical thresholds

**Status:** accepted. Starter analytics reports data availability and descriptive counts only. Guidance links actions to findings. No diagnosis, risk score, clinical alert, or threshold is introduced without documented evidence review and domain governance.

## ADR-005: Explicit units, UTC, and missingness

**Status:** accepted. Each observation carries a metric-specific unit and UTC timestamp. Nullable check-in fields represent “not reported.” Absence must never be imputed as normal at an API boundary.

## ADR-006: No Docker in the starter

**Status:** accepted. Native Python and Node setup is simpler for the initial offline hackathon workflow. Reconsider only when reproducible packaging becomes a demonstrated need.

