"""Equivalent fictional name fields; no actors, relations or automatic timestamps.

pghistory configuration: https://pypi.org/project/django-pghistory/3.9.2/
Other configurations match the adjacent retained SQLite trial.
"""

import pghistory
from auditlog.registry import auditlog
from django.db import models
from simple_history.models import HistoricalRecords


class SnapshotItem(models.Model):
    name = models.CharField(max_length=40)
    history = HistoricalRecords()

    def __str__(self):
        return self.name


class ChangeItem(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


auditlog.register(ChangeItem)


@pghistory.track()
class TriggerItem(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name
