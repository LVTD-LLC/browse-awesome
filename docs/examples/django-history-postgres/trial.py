"""Run only against a new, disposable PostgreSQL cluster created by this script.

No application settings, database URLs, credentials, production data or TCP listener.
Provenance:
https://www.postgresql.org/docs/15/app-initdb.html
https://www.postgresql.org/docs/15/app-pg-ctl.html
https://pypi.org/project/django-pghistory/3.9.2/
https://django-pghistory.readthedocs.io/en/stable/faq/
https://docs.djangoproject.com/en/5.2/topics/db/transactions/
https://docs.djangoproject.com/en/5.2/topics/db/sql/#executing-custom-sql-directly
"""

import argparse
import hashlib
import importlib.metadata
import io
import json
import platform
import shlex
import shutil
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path


def command(args):
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout


def run_probe(root):
    from django.conf import settings

    # Generated migrations belong to a disposable copy, never the source checkout.
    shutil.copytree(Path(__file__).with_name("pg_probe"), root / "pg_probe")
    sys.path.insert(0, str(root))
    settings.configure(
        SECRET_KEY="synthetic-disposable-only",
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "simple_history",
            "auditlog",
            "pgtrigger",
            "pghistory",
            "pg_probe",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": "postgres",
                "USER": "trial",
                "HOST": str(root),
                "PORT": "5432",
            }
        },
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        USE_TZ=True,
    )
    import django

    django.setup()
    from django.core.management import call_command
    from django.db import connection
    from pg_probe.models import TriggerItem

    captured = io.StringIO()
    call_command("makemigrations", "pg_probe", verbosity=0, stdout=captured)
    call_command("migrate", verbosity=0, stdout=captured)
    call_command("check", stdout=captured)
    with redirect_stdout(captured):
        call_command("pgtrigger", "ls", stdout=captured)
    with connection.cursor() as cursor:
        cursor.execute("SHOW server_version")
        server_version = cursor.fetchone()[0]
        cursor.execute(
            "SELECT tgname, tgenabled FROM pg_trigger "
            "WHERE tgrelid = %s::regclass AND NOT tgisinternal ORDER BY tgname",
            [TriggerItem._meta.db_table],
        )
        triggers = cursor.fetchall()
    assert len(triggers) == 2 and all(state == "O" for _, state in triggers), triggers
    result = exercise()
    result.update(
        {
            "python": platform.python_version(),
            "server_version": server_version,
            "database": "new local cluster, Unix socket only, fictional records",
            "packages": {
                p: importlib.metadata.version(p)
                for p in [
                    "Django",
                    "django-simple-history",
                    "django-auditlog",
                    "django-pghistory",
                    "django-pgtrigger",
                    "psycopg",
                ]
            },
            "installed_enabled_triggers": triggers,
            "django_checks_and_trigger_listing": captured.getvalue(),
            "generated_migrations": {
                p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted((root / "pg_probe" / "migrations").glob("*.py"))
            },
            "source_sha256": {
                str(p.relative_to(Path(__file__).parent)): hashlib.sha256(
                    p.read_bytes()
                ).hexdigest()
                for p in [
                    Path(__file__),
                    Path(__file__).with_name("pg_probe") / "models.py",
                ]
            },
            "exclusions": [
                "M2M and deletion",
                "manual/history-aware adapters",
                "actor attribution",
                "concurrency or performance",
                "security or compliance",
                "production integration",
            ],
        }
    )
    connection.close()
    return result


def history(model, obj):
    from auditlog.models import LogEntry
    from pg_probe.models import ChangeItem, SnapshotItem, TriggerItemEvent

    if model is SnapshotItem:
        return obj.history.order_by("-history_id")
    if model is ChangeItem:
        return LogEntry.objects.get_for_object(obj).order_by("-id")
    return TriggerItemEvent.objects.filter(pgh_obj_id=obj.pk).order_by("-pgh_id")


def check_content(model, obj, expected_name, expected_label):
    from auditlog.models import LogEntry
    from pg_probe.models import ChangeItem, SnapshotItem

    record = history(model, obj).first()
    if model is SnapshotItem:
        assert record.id == obj.pk and record.name == expected_name
        assert record.history_type == "~"
        return {"name": record.name, "kind": record.history_type}
    if model is ChangeItem:
        assert str(record.object_pk) == str(obj.pk)
        assert record.action == LogEntry.Action.UPDATE
        assert record.changes["name"] == ["before", expected_name]
        return {"name_change": record.changes["name"], "action": record.action}
    assert record.pgh_obj_id == obj.pk and record.name == expected_name
    assert record.pgh_label == expected_label
    return {"name": record.name, "label": record.pgh_label}


def write(model, obj, operation):
    from django.db import connection

    if operation == "save_unchanged":
        obj.save()
    elif operation == "save_changed":
        obj.name = "after"
        obj.save()
    elif operation == "queryset_update":
        model.objects.filter(pk=obj.pk).update(name="after")
    elif operation == "bulk_update":
        obj.name = "after"
        model.objects.bulk_update([obj], ["name"])
    else:
        assert operation == "raw_sql_update"
        with connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE {connection.ops.quote_name(model._meta.db_table)} "
                "SET name = %s WHERE id = %s",
                ["after", obj.pk],
            )
            assert cursor.rowcount == 1


class IntentionalRollback(Exception):
    """Only this exception is the deliberately rolled-back operation."""


def rollback(model, obj, before, expected):
    from django.db import transaction

    try:
        with transaction.atomic():
            write(model, obj, "raw_sql_update")
            assert model.objects.get(pk=obj.pk).name == "after"
            assert history(model, obj).count() == before + expected
            if expected:
                check_content(model, obj, "after", "update")
            raise IntentionalRollback
    except IntentionalRollback:
        pass


def exercise():
    from pg_probe.models import ChangeItem, SnapshotItem, TriggerItem

    models = [SnapshotItem, ChangeItem, TriggerItem]
    expected = {
        "save_unchanged": (1, 0, 0),
        "save_changed": (1, 1, 1),
        "queryset_update": (0, 0, 1),
        "bulk_update": (0, 0, 1),
        "raw_sql_update": (0, 0, 1),
        "rollback_raw_sql": (0, 0, 0),
    }
    out = []
    for operation, deltas in expected.items():
        result = {"operation": operation}
        for i, model in enumerate(models):
            obj = model.objects.create(name="before")
            before = history(model, obj).count()
            if operation == "rollback_raw_sql":
                rollback(model, obj, before, int(model is TriggerItem))
            else:
                write(model, obj, operation)
            current = model.objects.get(pk=obj.pk).name
            wanted = "before" if operation in {"save_unchanged", "rollback_raw_sql"} else "after"
            assert current == wanted
            delta = history(model, obj).count() - before
            assert delta == deltas[i], (operation, model.__name__, delta)
            result[model.__name__] = {
                "new_records": delta,
                "stored_name": current,
                "new_record_contents": (
                    check_content(model, obj, current, "update") if delta else None
                ),
            }
        out.append(result)
    creates = {}
    for model in models:
        objects = model.objects.bulk_create([model(name="new-a"), model(name="new-b")])
        for obj in objects:
            assert model.objects.get(pk=obj.pk).name == obj.name
            count = history(model, obj).count()
            assert count == int(model is TriggerItem)
            if count:
                check_content(model, obj, obj.name, "insert")
        creates[model.__name__] = sum(history(model, obj).count() for obj in objects)
    return {"cases": out, "bulk_create_two_new_records": creates}


def main():
    if not __debug__:
        raise RuntimeError("Run without -O: this trial requires enabled assertions.")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--postgres-bin", required=True, type=Path)
    args = parser.parse_args()
    binaries = args.postgres_bin.resolve()
    for name in ["initdb", "pg_ctl"]:
        if not (binaries / name).is_file():
            parser.error(f"Missing PostgreSQL executable: {name}")
    root = Path(tempfile.mkdtemp(prefix="ba-history-pg-"))
    try:
        data = root / "data"
        command(
            [
                str(binaries / "initdb"),
                "-D",
                str(data),
                "-A",
                "trust",
                "-U",
                "trial",
                "--no-locale",
                "--no-sync",  # Only this newly created, disposable cluster.
            ]
        )
        control = [str(binaries / "pg_ctl"), "-D", str(data)]
        try:
            command(
                control
                + [
                    "-l",
                    str(root / "server.log"),
                    "-o",
                    f"-h '' -k {shlex.quote(str(root))} -p 5432",
                    "-w",
                    "start",
                ]
            )
            result = run_probe(root)
        finally:
            if (data / "postmaster.pid").exists():
                command(control + ["-m", "immediate", "-w", "stop"])
        print(json.dumps(result, indent=2))
    finally:
        # Preserve evidence/files if our own server could not be confirmed stopped.
        if not (root / "data" / "postmaster.pid").exists():
            shutil.rmtree(root)
        else:
            print(f"Unconfirmed shutdown; own cluster retained at {root}", file=sys.stderr)


if __name__ == "__main__":
    main()
