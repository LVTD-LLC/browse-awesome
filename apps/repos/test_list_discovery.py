from html import escape
from urllib.parse import parse_qs, urlsplit

import pytest
from django.urls import reverse

from apps.repos.discovery import awesome_list_starting_points
from apps.repos.models import AwesomeList, AwesomeListItem, Repository


@pytest.mark.django_db
def test_starting_points_use_current_slug_and_skip_unavailable_sources(django_assert_num_queries):
    python_list = AwesomeList.objects.create(
        name="Python tools",
        slug="python-tools",
        repo_full_name="vinta/awesome-python",
        source_url="https://github.com/vinta/awesome-python",
    )
    AwesomeList.objects.create(
        name="Inactive",
        slug="inactive",
        repo_full_name="agarrharr/awesome-cli-apps",
        source_url="https://github.com/agarrharr/awesome-cli-apps",
        is_active=False,
    )
    AwesomeList.objects.create(
        name="Archived",
        slug="archived",
        repo_full_name="public-apis/public-apis",
        source_url="https://github.com/public-apis/public-apis",
        is_archived=True,
    )
    with django_assert_num_queries(1):
        entries = awesome_list_starting_points()
        assert len(entries) == 1
        assert entries[0]["awesome_list"].get_absolute_url() == python_list.get_absolute_url()
        assert entries[0]["awesome_list"].name == "Python tools"

    python_list.is_disabled = True
    python_list.save()
    assert awesome_list_starting_points() == []


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("source", "slug"),
    [
        ("vinta/awesome-python", "python-tools"),
        ("bradAGI/awesome-cli-coding-agents", "renamed-coding-list"),
    ],
)
def test_directory_starting_points_do_not_displace_search_results(client, source, slug):
    selected_list = AwesomeList.objects.create(
        name="Tools for this task",
        slug=slug,
        repo_full_name=source,
        source_url=f"https://github.com/{source}",
        stars=100,
    )
    for index in range(30):
        AwesomeList.objects.create(
            name=f"Other list {index}",
            slug=f"other-{index}",
            source_url=f"https://github.com/example/list-{index}",
        )
    response = client.get(reverse("repos:list"))
    assert response.status_code == 200
    assert b"Start with what you want to do" in response.content
    assert f'href="/lists/{slug}/"'.encode() in response.content
    assert f'data-discovery-action="{source}"'.encode() in response.content
    assert client.get(selected_list.get_absolute_url()).status_code == 200
    assert b'data-discovery-action="directory_checklist"' in response.content
    assert b'href="/blog/how-to-shortlist-github-repositories/"' in response.content
    assert response.content.index(b"Search lists") < response.content.index(b"Start with what")

    for params in ({"q": "Tools"}, {"sort": "recent"}, {"page": "2"}):
        filtered = client.get(reverse("repos:list"), params)
        assert filtered.status_code == 200
        assert b"Start with what you want to do" not in filtered.content
        assert filtered.context["list_starting_points"] == []
        assert b'data-discovery-action="directory_empty_repositories"' not in filtered.content

    selected_list.is_disabled = True
    selected_list.save()
    assert (
        f'data-discovery-action="{source}"'.encode()
        not in client.get(reverse("repos:list")).content
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "params",
    [
        {},
        {"q": "   "},
        {"q": '  httpx & <script>" / café  '},
        {"q": "httpx", "sort": "scanned", "min_age_years": "10"},
    ],
)
def test_empty_directory_offers_repository_search_only_for_a_term(client, params):
    response = client.get(reverse("repos:list"), params)
    assert response.status_code == 200
    assert b"Start with what you want to do" not in response.content
    query = params.get("q", "").strip()
    if query:
        target = response.context["empty_list_repository_search_url"]
        assert urlsplit(target).path == reverse("repos:search")
        assert parse_qs(urlsplit(target).query) == {"q": [query]}
        assert f'href="{escape(target)}"'.encode() in response.content
        assert b'data-discovery-action="directory_empty_repositories"' in response.content
        assert b"List history and sorting won't carry over." in response.content
        assert client.get(target).status_code == 200
    else:
        assert b'data-discovery-action="directory_empty_repositories"' not in response.content


@pytest.mark.django_db
def test_empty_list_repository_search_can_expand_scope(client, user):
    curated_list = AwesomeList.objects.create(
        name="Django", slug="django", source_url="https://github.com/example/awesome-django"
    )
    other_list = AwesomeList.objects.create(
        name="Python", slug="python", source_url="https://github.com/example/awesome-python"
    )
    repo = Repository.objects.create(
        full_name="encode/httpx",
        owner="encode",
        name="httpx",
        url="https://github.com/encode/httpx",
        description="HTTP client for café & tea",
        language="Python",
        license_name="BSD-3-Clause",
    )
    AwesomeListItem.objects.create(awesome_list=other_list, repository=repo)
    action = b'data-discovery-action="empty_search_across_catalog"'
    query = {
        "q": "café & tea",
        "language": "Python",
        "license": "bsd-3-clause",
        "sort": "stars",
        "sort_direction": "asc",
    }

    empty = client.get(
        curated_list.get_absolute_url(),
        {**query, "list": "django", "also_in": "django", "page": "2", "extra": "discard"},
    )
    assert empty.status_code == 200
    assert empty.context["page_obj"].paginator.count == 0
    target = empty.context["search_across_catalog_url"]
    assert urlsplit(target).path == reverse("repos:search")
    assert parse_qs(urlsplit(target).query) == {name: [value] for name, value in query.items()}
    assert f'href="{escape(target)}"'.encode() in empty.content
    assert empty.content.count(action) == 1
    assert b'data-discovery-action="empty_remove_license"' in empty.content
    assert b'data-discovery-action="empty_keep_search"' in empty.content

    recovered = client.get(target)
    assert recovered.status_code == 200
    assert list(recovered.context["repositories"]) == [repo]
    assert action not in recovered.content
    assert action not in client.get(curated_list.get_absolute_url()).content
    assert action not in client.get(other_list.get_absolute_url(), query).content
    assert action not in client.get(reverse("repos:search"), {"q": "no-match"}).content

    repeated = client.get(
        curated_list.get_absolute_url(),
        {
            "has_file": ["AGENTS.md", ".github/copilot-instructions.md"],
            "q": "httpx",
            "mode": "keyword",
        },
    )
    assert parse_qs(urlsplit(repeated.context["search_across_catalog_url"]).query) == {
        "has_file": ["AGENTS.md", ".github/copilot-instructions.md"],
        "q": ["httpx"],
        "mode": ["keyword"],
    }

    client.force_login(user)
    assert action not in client.get(reverse("repos:starred"), query).content
