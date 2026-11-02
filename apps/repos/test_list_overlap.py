"""The second list must intersect, not union with or replace the first scope."""

from urllib.parse import parse_qs

import pytest
from django.http import QueryDict
from django.urls import reverse

from apps.repos.models import AwesomeList, AwesomeListItem, Repository
from apps.repos.services import awesome_list_repository_queryset, repository_search_queryset


@pytest.mark.django_db
def test_second_list_intersects_public_search_and_retains_other_requirements(client):
    first, second = [
        AwesomeList.objects.create(
            name=name, slug=slug, source_url=f"https://github.com/example/{slug}"
        )
        for name, slug in [("First", "first"), ("Second", "second")]
    ]
    repos = [
        Repository.objects.create(
            full_name=f"example/{name}",
            owner="example",
            name=name,
            language=language,
            is_awesome_list_candidate=hidden,
        )
        for name, language, hidden in [
            ("both", "Python", False),
            ("first-only", "Python", False),
            ("second-only", "Python", False),
            ("both-wrong-language", "Go", False),
            ("both-hidden", "Python", True),
        ]
    ]
    for repo in repos:
        for awesome_list in (first, second):
            if repo.name == "first-only" and awesome_list == second:
                continue
            if repo.name == "second-only" and awesome_list == first:
                continue
            AwesomeListItem.objects.create(awesome_list=awesome_list, repository=repo)
    params = {"list": "first", "also_in": "second", "language": "Python", "sort": "name"}
    response = client.get(reverse("repos:search"), params)
    assert list(response.context["page_obj"].object_list) == [repos[0]]
    html = response.content.decode()
    assert 'name="also_in"' in html and 'value="second"' in html
    assert "results must belong to both lists" in html
    assert response.context["advanced_repository_filters_applied"]
    chip = next(
        c for c in response.context["active_repository_filters"] if c["label"] == "Also in list"
    )
    assert parse_qs(chip["remove_querystring"]) == {
        "list": ["first"],
        "language": ["Python"],
        "sort": ["name"],
    }
    assert '<link rel="canonical" href="https://testserver/repos/"' in html
    # With just the second requirement, search is still scoped to that list.
    assert set(
        repository_search_queryset(
            {"also_in": "second", "language": "Python"}, include_snapshot_metrics=False
        )
    ) == {repos[0], repos[2]}
    # List detail deliberately owns its own scope and does not expose these controls.
    assert set(
        awesome_list_repository_queryset(first, {"also_in": "missing", "language": "Python"})
    ) == {repos[0], repos[1]}
    second.is_disabled = True
    second.save(update_fields=["is_disabled"])
    assert not repository_search_queryset(params, include_snapshot_metrics=False).exists()
    second.is_disabled = False
    second.is_archived = True
    second.save(update_fields=["is_disabled", "is_archived"])
    assert not repository_search_queryset(params, include_snapshot_metrics=False).exists()
    second.is_archived = False
    second.is_active = False
    second.save(update_fields=["is_archived", "is_active"])
    assert not repository_search_queryset(params, include_snapshot_metrics=False).exists()


@pytest.mark.django_db
def test_unknown_ambiguous_and_oversize_overlap_never_broaden_search():
    Repository.objects.create(full_name="example/one", owner="example", name="one")
    for params in [
        {"also_in": "does-not-exist"},
        {"also_in": "x" * 256},
        QueryDict("also_in=first&also_in=second"),
        QueryDict("also_in=first&also_in="),
        QueryDict("also_in=first&also_in=+"),
        {"also_in": "abc\x00def"},
        {"also_in": "not/a/slug"},
    ]:
        assert not repository_search_queryset(params, include_snapshot_metrics=False).exists()
