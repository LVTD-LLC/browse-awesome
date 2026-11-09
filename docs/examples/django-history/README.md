# Synthetic Django history write-path fixture

Used by the [write-path walkthrough](https://browseawesome.com/blog/verify-django-history-write-paths/).
No production settings, user records, credentials or network calls are used by
the Python fixture. Package installation can use the network. SQLite is in-memory.

From the repository root, with uv installed:

```sh
uv run --no-project --python 3.14.7 \
  --with Django==5.2.19 \
  --with django-simple-history==3.13.0 \
  --with django-auditlog==3.4.2 \
  python docs/examples/django-history/trial.py
```

The command is intentionally independent of the website's dependency lock.
Retain `trial.py`, `probe/__init__.py` and `probe/models.py` together when downloading.
An assertion or environment error is not a passed check. Output includes versions,
source hashes, the checked operations and explicit exclusions. Run normally,
without Python's `-O` option, which disables assertions.

Configuration and behavior references for the tested releases:

- [simple-history 3.13.0 quick start](https://github.com/django-commons/django-simple-history/blob/723260fc51807a6642448983198ff291928031bb/docs/quick_start.rst)
- [simple-history 3.13.0 historical models](https://github.com/django-commons/django-simple-history/blob/723260fc51807a6642448983198ff291928031bb/docs/historical_model.rst)
- [simple-history 3.13.0 bulk helpers](https://github.com/django-commons/django-simple-history/blob/723260fc51807a6642448983198ff291928031bb/docs/common_issues.rst)
- [Auditlog 3.4.2 usage](https://github.com/django-commons/django-auditlog/blob/6a2a88f90f908b7d2aa9aa9e62a077a4c330cb18/docs/source/usage.rst)
- [Django 5.2 queryset methods](https://docs.djangoproject.com/en/5.2/ref/models/querysets/)
- [Django 5.2 atomic transactions](https://docs.djangoproject.com/en/5.2/topics/db/transactions/)
- [uv script environments](https://docs.astral.sh/uv/guides/scripts/)

The fixture tests snapshot and change-entry behavior, not security-event coverage,
actor attribution, production integration, performance or a universal package winner.
