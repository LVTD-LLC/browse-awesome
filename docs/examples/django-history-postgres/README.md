# Disposable PostgreSQL write-path trial

Companion to [the existing evaluation guide](https://browseawesome.com/blog/verify-django-history-write-paths/).
Keep the adjacent original SQLite trial unchanged; its observations are separate.

Requirements: uv, a non-root Unix user and local PostgreSQL 15 server binaries
(`initdb`, `pg_ctl`, `postgres`). This example does not install PostgreSQL or use
Docker. Set `--postgres-bin` to your installed PostgreSQL 15 binary directory.

Run from the repository root:

```sh
uv run --no-project --python 3.14.7 \
  --with Django==5.2.19 \
  --with django-simple-history==3.13.0 \
  --with django-auditlog==3.4.2 \
  --with django-pghistory==3.9.2 \
  --with django-pgtrigger==4.17.0 \
  --with 'psycopg[binary]==3.3.4' \
  python docs/examples/django-history-postgres/trial.py \
  --postgres-bin /usr/lib/postgresql/15/bin
```

Package pins describe the tested fixture, not recommended changes to an application
lockfile. uv may download Python/packages; the actual database trial makes no
external requests. PostgreSQL must already be installed. See [uv scripts](https://docs.astral.sh/uv/guides/scripts/)
for `--no-project`/`--with` environment isolation.

## Isolation and provenance

The script creates its own mode-0700 temporary directory and brand-new local
cluster. It reads no application settings, database URL or PostgreSQL connection
credentials. The server has **no TCP listener** and accepts connections through
its private Unix socket only. It never connects to an existing cluster. The
script copies `pg_probe` into that directory, generates actual migrations, migrates,
runs Django checks, lists installed triggers, verifies the trigger catalog and
checks fictional records. It stops its own server in `finally` and removes its own
temporary directory after confirmed shutdown. An unconfirmed shutdown preserves
that directory. An interrupted/killed process may need manual cleanup of
that specific temporary cluster; do not stop an unrelated PostgreSQL server.

`initdb --no-sync` and trust authentication apply only to this disposable cluster;
they are not deployment settings. Startup/shutdown syntax follows the official
[PostgreSQL 15 initdb](https://www.postgresql.org/docs/15/app-initdb.html) and
[pg_ctl](https://www.postgresql.org/docs/15/app-pg-ctl.html) references.
SQL writes use bound values per [Django 5.2 custom SQL](https://docs.djangoproject.com/en/5.2/topics/db/sql/#executing-custom-sql-directly).
Model registration follows [pghistory 3.9.2](https://pypi.org/project/django-pghistory/3.9.2/)
and the retained simple-history/Auditlog example. Default `@pghistory.track()`
tracks inserts and changed updates, not deletes. No actor middleware is configured.

JSON output records exact versions, source and generated-migration hashes, trigger
status, business values and new history contents. Initial object creation is
excluded from update-case deltas. Bulk creation is a separate two-object case.
The rollback test checks the changed value and any expected event **inside** the
transaction before confirming neither survives rollback. Never use `python -O`:
the script refuses it because the assertions are the experiment.

A failure is a failed experiment, not permission to delete an assertion. Keep its
output. No throughput, storage, concurrency, M2M, delete, actor, security or
compliance result is established. The existing SQLite M2M/delete/helper checks
are not silently relabeled as PostgreSQL observations.
