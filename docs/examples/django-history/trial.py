"""Synthetic write-path trial; no network, production DB, middleware or user data.

Configuration provenance:
https://github.com/django-commons/django-simple-history/tree/723260fc51807a6642448983198ff291928031bb/docs
https://github.com/django-commons/django-auditlog/blob/6a2a88f90f908b7d2aa9aa9e62a077a4c330cb18/docs/source/usage.rst
https://docs.djangoproject.com/en/5.2/topics/db/transactions/
"""

# Django must be configured and initialized before importing its runtime models.
# ruff: noqa: E402
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path

from django.conf import settings

if not __debug__:
    raise RuntimeError("Run without -O: this fixture requires enabled assertions.")

settings.configure(
    SECRET_KEY="synthetic-local-only",
    INSTALLED_APPS=[
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "simple_history",
        "auditlog",
        "probe",
    ],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    MIGRATION_MODULES={"probe": None},
    DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
    USE_TZ=True,
)
import django

django.setup()
from auditlog.models import LogEntry
from django.core.management import call_command
from django.db import transaction
from probe.models import ChangeItem, SnapshotItem, Tag
from simple_history.utils import bulk_create_with_history, bulk_update_with_history

call_command("migrate", run_syncdb=True, verbosity=0)


def count(model):
    return (
        model.history.count()
        if model is SnapshotItem
        else LogEntry.objects.get_for_model(model).count()
    )


def setup(model):
    return model.objects.create(name="before")


def save_changed(model, obj):
    obj.name = "after"
    obj.save()


def qs_update(model, obj):
    model.objects.filter(pk=obj.pk).update(name="after")


def bulk_update(model, obj):
    obj.name = "after"
    model.objects.bulk_update([obj], ["name"])


def bulk_create(model, obj):
    model.objects.bulk_create([model(name="new-a"), model(name="new-b")])


def add_tag(model, obj):
    obj.tags.add(Tag.objects.create(name="tag"))


class IntentionalRollback(Exception):
    """Only this deliberate exception marks the rollback case as exercised."""


def rolled_back_save(model, obj):
    records_before = count(model)
    try:
        with transaction.atomic():
            save_changed(model, obj)
            assert model.objects.get(pk=obj.pk).name == "after"
            assert count(model) == records_before + 1
            raise IntentionalRollback
    except IntentionalRollback:
        pass


def delete_queryset(model, obj):
    model.objects.filter(pk=obj.pk).delete()


cases = {
    "save_unchanged": lambda model, obj: obj.save(),
    "save_changed": save_changed,
    "queryset_update": qs_update,
    "bulk_update": bulk_update,
    "bulk_create_two": bulk_create,
    "m2m_add_configured": add_tag,
    "atomic_rollback_save": rolled_back_save,
    "queryset_delete": delete_queryset,
}
out = []
expected = {
    "save_unchanged": (1, 0),
    "save_changed": (1, 1),
    "queryset_update": (0, 0),
    "bulk_update": (0, 0),
    "bulk_create_two": (0, 0),
    "m2m_add_configured": (1, 1),
    "atomic_rollback_save": (0, 0),
    "queryset_delete": (1, 1),
}
for case, operation in cases.items():
    result = {"case": case}
    for n, model in enumerate([SnapshotItem, ChangeItem]):
        obj = setup(model)
        before = count(model)
        rows_before = model.objects.count()
        operation(model, obj)
        records = count(model) - before
        current = model.objects.filter(pk=obj.pk).values_list("name", flat=True).first()
        assert records == expected[case][n], (case, model.__name__, records)
        if case in {"save_changed", "queryset_update", "bulk_update"}:
            assert current == "after"
        if case in {"save_unchanged", "atomic_rollback_save"}:
            assert current == "before"
        if case == "queryset_delete":
            assert current is None
        if case == "bulk_create_two":
            assert model.objects.count() == rows_before + 2
        if case == "m2m_add_configured":
            assert obj.tags.count() == 1
            if model is SnapshotItem:
                assert obj.history.first().tags.count() == 1
            else:
                assert (
                    LogEntry.objects.get_for_object(obj).first().changes["tags"]["operation"]
                    == "add"
                )
        result[model.__name__] = {
            "new_records": records,
            "stored_name": current,
            "model_row_delta": model.objects.count() - rows_before,
        }
    out.append(result)

before = count(SnapshotItem)
created = bulk_create_with_history(
    [SnapshotItem(name="helper-a"), SnapshotItem(name="helper-b")], SnapshotItem
)
assert count(SnapshotItem) - before == 2
before = count(SnapshotItem)
for obj in created:
    obj.name = "helper-after"
bulk_update_with_history(created, SnapshotItem, ["name"])
assert count(SnapshotItem) - before == 2
assert all(SnapshotItem.objects.get(pk=obj.pk).name == "helper-after" for obj in created)

result = {
    "python": platform.python_version(),
    "packages": {
        p: importlib.metadata.version(p)
        for p in ["Django", "django-simple-history", "django-auditlog"]
    },
    "database": "SQLite in-memory, one process, no production data",
    "configured_m2m": True,
    "middleware_actor_tracking": False,
    "cases": out,
    "simple_history_helpers": {"create_two_records": True, "update_two_records": True},
    "exclusions": [
        "PostgreSQL",
        "concurrency",
        "performance",
        "raw SQL",
        "request actors",
        "admin revert",
        "security or compliance guarantee",
        "production integration",
    ],
    "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "models_sha256": hashlib.sha256(
        Path(__file__).with_name("probe").joinpath("models.py").read_bytes()
    ).hexdigest(),
}
print(json.dumps(result, indent=2))
