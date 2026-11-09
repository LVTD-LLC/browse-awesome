---
title: "Test Django history packages against your actual write paths"
seo_title: "Test Django history packages: a write-path trial"
description: >-
  Before choosing a Django history package, test the operations your application
  actually uses. This reproducible synthetic trial checks saves, bulk writes,
  configured many-to-many changes, deletion and rollback in django-simple-history
  and django-auditlog. Its purpose is a better-supported shortlist, not a package
  ranking or a production audit guarantee.
meta_description: "Run a pinned Django history-package trial covering saves, bulk writes, many-to-many changes and rollback before keeping a repository on your shortlist."
published_at: 2026-11-10T01:24:40+03:00
updated_at: 2026-11-10T01:24:40+03:00
author: Browse Awesome Team
author_type: Organization
image: /static/brand/awesome-repos-social.png
image_alt: Browse Awesome repository discovery
categories:
  - Repository evaluation
tags:
  - Django
  - Reproducible trials
keywords:
  - django history bulk update
  - django simple history vs auditlog
---

To evaluate a Django history package, test your application's write paths before comparing repository popularity. An instance save, a queryset update and a relation change do not exercise the same hooks. Use a disposable model, verify both its stored state and its history, then keep candidates that meet your specific evidence requirement.

This walkthrough supplies a [runnable synthetic fixture](https://github.com/LVTD-LLC/browse-awesome/tree/main/docs/examples/django-history) for two candidates: **django-simple-history** and **django-auditlog**. Browse Awesome executed it on November 9, 2026, UTC, using Python 3.14.7, Django 5.2.19, django-simple-history 3.13.0 and django-auditlog 3.4.2. Three fresh-process runs produced the same assertions and results. These are local behavior checks with fictional records, not customer analytics, a performance benchmark or a security assessment.

## 1. Define the evidence before finding a package

Start with one sentence: “When this operation succeeds, I need to recover this evidence.” For example, an import job may update product names in bulk, while an administrator edits one product through a form. If both paths matter, testing only the form's instance save leaves the import unanswered.

Use [Django repository discovery](/repos/?framework=django) or [Awesome Django](/lists/awesome-django/) to find candidates, then read their current source and documentation. A catalog match is a lead, not proof of installed behavior. The [dependency-evidence walkthrough](/blog/find-django-github-projects/) explains how to distinguish an application dependency from development or example configuration before testing it.

The two candidates here also store different kinds of evidence. django-simple-history provides historical model-state records. django-auditlog records model changes as log entries. Equal row counts would not establish equal contents, retention behavior or ability to answer your question. Decide whether you need a state snapshot, a field change, an attempted business action, or something else before using the table below.

This guide tests automatic model-change coverage. It does not test denied requests, sensitive reads, actor attribution or evidence outside a rolled-back transaction. [Djass's audit-log guide](https://djass.dev/blog/django-audit-log) covers the broader distinction between model history and security or business events; it is not independent validation of this trial.

## 2. Run the fixture in a disposable environment

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) first. Use a local checkout of the Browse Awesome repository, or download the fixture into an empty working directory with these exact relative paths: `docs/examples/django-history/trial.py`, `docs/examples/django-history/probe/__init__.py` and `docs/examples/django-history/probe/models.py`. Keep the empty initialization file too, so the local probe remains an importable package. The fixture uses an in-memory SQLite database and fictional names. It configures its own Django settings, performs local migrations and makes no network requests. Do not point it at your application settings or a production database.

From the repository root, run the following command. The syntax follows [uv's script/environment documentation](https://docs.astral.sh/uv/guides/scripts/); `--no-project` keeps the example's package environment separate from this website's dependencies. The exact package versions below are the versions exercised in this walkthrough, not an instruction to change an existing application's lockfile.

```sh
uv run --no-project --python 3.14.7 \
  --with Django==5.2.19 \
  --with django-simple-history==3.13.0 \
  --with django-auditlog==3.4.2 \
  python docs/examples/django-history/trial.py
```

The command can download Python or packages if they are not already available. A successful run prints JSON containing the actual interpreter and package versions, operation results, exclusions and source-file hashes. An assertion failure is a failed check: preserve its output and investigate rather than deleting the assertion to obtain a pass. Package-install or migration errors are also not a clean result.

The fixture uses equivalent models with a name and a many-to-many tag relation. One has `HistoricalRecords(m2m_fields=["tags"])`; the other is registered with `auditlog.register(..., m2m_fields={"tags"})`. Both relations are explicitly configured for tracking. See the [simple-history historical-model documentation](https://django-simple-history.readthedocs.io/en/stable/historical_model.html) and [Auditlog usage documentation](https://django-auditlog.readthedocs.io/en/latest/usage.html). The fixture links the tested release sources too: moving documentation is a useful current reference, not a version pin.

## 3. Read stored state and history separately

Each case creates a fresh starting object before measuring new history records. The baseline creation is excluded from the deltas below. The script separately checks the resulting model value or deletion, so “no new history” cannot be mistaken for “the write did not happen.”

**Observed fixture results, November 9, 2026, UTC:**

| Operation | simple-history: new records | Auditlog: new entries |
| --- | --- | --- |
| Save without changing the name | 1 | 0 |
| Change the name and save | 1 | 1 |
| Change the name with `QuerySet.update()` | 0 | 0 |
| Change the name with ordinary `bulk_update()` | 0 | 0 |
| Create two objects with ordinary `bulk_create()` | 0 | 0 |
| Add a tag to the explicitly tracked relation | 1 | 1 |
| Save inside an atomic block, then roll it back | 0 | 0 |
| Delete the object through a queryset | 1 | 1 |

These are operation-level observations from the named fixture and versions, not coverage percentages or package scores. In the bulk-update cases, the model's name changed in the database despite the zero history delta. In the rollback case, neither the changed name nor the transaction's new history record remained. Queryset deletion did create history in this fixture: do not generalize “bulk operations” into a single behavior.

The unchanged-save difference is another reason not to rank packages by record volume. A historical snapshot and a change entry answer different questions. An extra snapshot is not automatically better evidence; an absent change entry after an unchanged save is not automatically lost data. Inspect the record's meaning, not only its count.

## 4. Test supported alternatives without hiding the default

[Django's queryset reference](https://docs.djangoproject.com/en/5.2/ref/models/querysets/) documents that ordinary bulk creation and updating bypass the per-instance save signals used by these paths. The [simple-history bulk-operation documentation](https://django-simple-history.readthedocs.io/en/stable/common_issues.html) describes its `bulk_create_with_history()` and `bulk_update_with_history()` helpers.

The fixture exercises those helpers separately: creating two objects adds two historical records, and updating those objects through the history-aware helper adds two more. Keeping that check separate preserves the important distinction between the ordinary manager method and a deliberately chosen history-aware write path. It does not mean existing import jobs will start using the helpers when a package is installed.

When adapting the fixture, keep a failing ordinary-operation case beside the proposed alternative. First establish that the business row actually changed. Then inspect the history record for the specific value or relation you expected to recover. Finally, repeat the rollback check with the alternative inside the same transaction boundary. A total record count alone can pass even when the record describes the wrong object or lacks the evidence you need. If your requirement includes an actor or a reason, add an explicit content assertion for it; this fixture leaves those requirements unanswered rather than filling them with a placeholder identity.

Auditlog's [tested receiver source](https://github.com/django-commons/django-auditlog/blob/6a2a88f90f908b7d2aa9aa9e62a077a4c330cb18/auditlog/receivers.py) and [manual logging interfaces](https://django-auditlog.readthedocs.io/en/latest/internals.html) are relevant when designing another path. This fixture does **not** implement or test a manual Auditlog bulk adapter. “Not tested here” is not “impossible.” Do not treat an unimplemented alternative as a reason to declare one package the winner.

## 5. Turn the result into a shortlist decision

Write down the required operation, expected evidence, tested version, observed state, observed history and unresolved question. A useful decision could be: “Our import uses ordinary bulk updates. Neither default setup in this fixture records that path. Evaluate a deliberate history-aware path before keeping either candidate for the import requirement.” That is narrower and more actionable than “this library supports auditing.”

For an application that needs point-in-time model snapshots, investigate simple-history's documented query and administration workflows next. For one that needs change entries with selected fields and actor context, investigate Auditlog's documented configuration next. Those are reasons to continue evaluating, not findings that this fixture tested either workflow end to end.

Then extend the test only where your actual requirement differs. Relevant next cases might include a custom manager, explicit through models, worker actor context, a database router or direct SQL. Run against your database engine and transaction design before making an integration decision. This SQLite fixture says nothing about PostgreSQL-specific behavior, concurrency, throughput, storage growth, raw SQL, tamper resistance, access policy or regulatory suitability.

Keep the versions, command, source hashes and failed checks with the decision. Re-run when the package version or your application's write path changes, not merely because a repository's star count moved. Return to the [repository-shortlisting worksheet](/blog/how-to-shortlist-github-repositories/) to combine this small behavior trial with license, maintenance and task-fit evidence. The goal is a shorter shortlist with a testable reason for each candidate—not a universal ranking of Django history packages.
