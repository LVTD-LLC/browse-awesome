from auditlog.registry import auditlog
from django.db import models
from simple_history.models import HistoricalRecords


class Tag(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


class SnapshotItem(models.Model):
    name = models.CharField(max_length=40)
    tags = models.ManyToManyField(Tag)
    history = HistoricalRecords(m2m_fields=["tags"])

    def __str__(self):
        return self.name


class ChangeItem(models.Model):
    name = models.CharField(max_length=40)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.name


auditlog.register(ChangeItem, m2m_fields={"tags"})
