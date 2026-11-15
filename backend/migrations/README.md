# Database migrations

Run `python -m alembic upgrade head` from the repository root before starting a persistent development database. New installations may also rely on startup table creation, but migration history is the durable schema-change mechanism.

The initial migration only creates schema objects; it contains no destructive data operation. For an unversioned database created by the earlier starter, back it up, verify its tables match the initial revision, then use `python -m alembic stamp 0001` before upgrading. Never stamp an unknown database merely to suppress an error.

