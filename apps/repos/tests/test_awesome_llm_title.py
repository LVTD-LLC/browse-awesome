from importlib import import_module
from types import SimpleNamespace

import pytest
from django.apps import apps
from django.db import connection

from apps.repos.models import AwesomeList
from apps.repos.search_services import awesome_list_search_queryset


@pytest.mark.django_db
def test_title_correction_preserves_discovery_and_editor_changes():
    entry = AwesomeList.objects.create(
        slug="awesome-chatgpt",
        source_url="https://github.com/uhub/awesome-chatgpt",
        repo_full_name="uhub/awesome-llm",
        name="Awesome Chatgpt",
    )
    migration = import_module("apps.repos.migrations.0024_correct_awesome_llm_title")
    editor = SimpleNamespace(connection=connection)
    migration.correct_title(apps, editor)
    entry.refresh_from_db()
    assert entry.name == "Awesome LLM (formerly Awesome ChatGPT)"
    assert entry.get_absolute_url() == "/lists/awesome-chatgpt/"
    for query in ("awesome llm", "awesome chatgpt"):
        assert awesome_list_search_queryset({"q": query}).get().pk == entry.pk

    entry.name = "An editor's title"
    entry.save(update_fields=["name"])
    migration.correct_title(apps, editor)
    entry.refresh_from_db()
    assert entry.name == "An editor's title"
