"""Contracts for the public comparison's boundaries, evidence and index posture."""

import json
import re
from unittest.mock import Mock

import pytest
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags

from apps.repos.comparison import (
    EXAMPLE_IDENTITIES,
    MAX_SOURCE_PREVIEW,
    comparison_columns,
    parse_repository_identity,
)
from apps.repos.models import AwesomeList, AwesomeListItem, Repository
from awesome_repos.sitemaps import StaticViewSitemap


@pytest.mark.parametrize(
    ("value", "identity"),
    [
        ("  PSF/Requests  ", "psf/requests"),
        ("https://github.com/Encode/HTTPX/", "encode/httpx"),
        ("a/b.c_d-e", "a/b.c_d-e"),
        (f"{'a' * 39}/{'b' * 100}", f"{'a' * 39}/{'b' * 100}"),
    ],
)
def test_exact_identity_normalization(value, identity):
    assert parse_repository_identity(value) == identity


@pytest.mark.parametrize(
    "value",
    [
        "",
        " ",
        "owner",
        "owner/repo/issues",
        "owner/repo?x=y",
        "owner/repo#readme",
        "http://github.com/owner/repo",
        "https://github.com.evil/owner/repo",
        "https://user@github.com/owner/repo",
        "https://github.com:443/owner/repo",
        "https://127.0.0.1/owner/repo",
        "https://github.com/owner/repo?tab=readme",
        "https://github.com/owner/repo//",
        "https://github.com/owner/%72epo",
        "owner/..",
        "owner/.",
        "owner/répo",
        "owner/repo\nother/repo",
        "a--b/repo",
        f"{'a' * 40}/repo",
        f"a/{'b' * 101}",
        "a" * 10_000,
    ],
)
def test_invalid_identity_is_rejected(value):
    with pytest.raises(ValueError):
        parse_repository_identity(value)


@pytest.fixture
def catalog(db):
    repositories = []
    for identity in EXAMPLE_IDENTITIES:
        owner, name = identity.split("/")
        repositories.append(
            Repository.objects.create(
                full_name=identity,
                owner=owner,
                name=name,
                url=f"https://github.com/{identity}",
                language="Python",
                stars=123,
                last_synced_at=timezone.now(),
            )
        )
    return repositories


@pytest.mark.django_db
def test_base_has_real_guarded_demo_and_indexable_schema(client, catalog, settings):
    settings.SITE_URL = "https://browseawesome.com"
    response = client.get(reverse("compare_repositories"))
    html = response.content.decode()
    assert response.status_code == 200
    assert '<meta name="robots" content="index, follow"' in html
    assert (
        '<link rel="canonical" href="https://browseawesome.com/tools/compare-github-repositories/"'
        in html
    )
    assert 'value="psf/requests"' in html and 'value="encode/httpx"' in html
    assert "Example comparison" in html
    assert "not interchangeable recommendations" in html
    assert "X-Robots-Tag" not in response.headers
    schema = json.loads(
        re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)[1]
    )
    application, breadcrumbs = schema["@graph"]
    assert application["@type"] == "WebApplication"
    assert application["offers"]["price"] == "0"
    assert [item["item"] for item in breadcrumbs["itemListElement"]] == [
        "https://browseawesome.com/",
        "https://browseawesome.com/tools/",
        "https://browseawesome.com/tools/compare-github-repositories/",
    ]
    assert html.count("<h1") == 1
    tracked = client.get(reverse("compare_repositories"), {"utm_source": "reference"})
    assert "Example comparison" in tracked.content.decode()
    assert 'role="alert"' not in tracked.content.decode()
    assert tracked.headers["X-Robots-Tag"] == "noindex, follow"


@pytest.mark.django_db
def test_missing_example_is_not_fabricated_and_valid_missing_stays_unobserved(client):
    base = client.get(reverse("compare_repositories"))
    assert "demonstration pair is not fully available" in base.content.decode()
    result = client.get(
        reverse("compare_repositories"), {"first": "missing/one", "second": "missing/two"}
    )
    html = result.content.decode()
    assert html.count("Not observed in the public repository catalog.") == 2
    assert 'href="https://github.com/missing/' not in html
    assert result.headers["X-Robots-Tag"] == "noindex, follow"


@pytest.mark.django_db
def test_results_are_noindex_and_unknown_is_not_zero_or_maintenance(client, catalog):
    first, second = catalog
    first.last_synced_at = None
    first.stars = 0
    first.save()
    second.is_archived = True
    second.save()
    response = client.get(
        reverse("compare_repositories"),
        {"first": "PSF/Requests", "second": "https://github.com/encode/httpx/"},
    )
    html = response.content.decode()
    assert response.status_code == 200
    assert response.headers["X-Robots-Tag"] == "noindex, follow"
    assert '<meta name="robots" content="noindex, follow"' in html
    assert "?first=" not in re.search(r'<link rel="canonical"[^>]+>', html)[0]
    assert "Not recorded — metadata not checked" in html
    assert re.search(r"Stored stars</dt>\s*<dd[^>]*>\s*Not checked\s*</dd>", html)
    assert "Yes, at last metadata sync" in html
    assert "No stack observation shown; not proof of absence." in html
    assert "Actively maintained" not in html


@pytest.mark.django_db
def test_visibility_and_source_preview_follow_public_catalog(catalog, django_assert_num_queries):
    first, second = catalog
    first.is_awesome_list_candidate = True
    first.save()
    for number in range(MAX_SOURCE_PREVIEW + 2):
        source = AwesomeList.objects.create(
            name=f"Source {number:02}",
            slug=f"source-{number}",
            source_url=f"https://github.com/lists/list-{number}",
        )
        AwesomeListItem.objects.create(repository=second, awesome_list=source)
    disabled = AwesomeList.objects.create(
        name="Disabled",
        slug="disabled",
        source_url="https://github.com/lists/disabled",
        is_disabled=True,
    )
    AwesomeListItem.objects.create(repository=second, awesome_list=disabled)
    # One bounded repository lookup plus one bounded source lookup for the match.
    with django_assert_num_queries(2):
        columns = comparison_columns(EXAMPLE_IDENTITIES)
    assert columns[0]["repository"] is None
    assert len(columns[1]["sources"]) == MAX_SOURCE_PREVIEW
    assert columns[1]["has_more_sources"]
    assert all(item.awesome_list.name != "Disabled" for item in columns[1]["sources"])


@pytest.mark.django_db
def test_active_list_source_repository_is_not_a_comparison_candidate(catalog):
    AwesomeList.objects.create(
        name="Source",
        slug="source",
        source_url="https://github.com/psf/requests",
        repo_full_name="psf/requests",
    )
    assert comparison_columns(EXAMPLE_IDENTITIES)[0]["repository"] is None


@pytest.mark.django_db
@pytest.mark.parametrize(
    "params",
    [
        {"first": "", "second": ""},
        {"first": "PSF/Requests", "second": "psf/requests"},
        {"first": "<script>alert(1)</script>", "second": "encode/httpx"},
        {"first": "x" * 10_000, "second": "encode/httpx"},
        {"first": ["psf/requests", "other/repo"], "second": "encode/httpx"},
    ],
)
def test_bad_input_has_neutral_errors_without_catalog_lookup(client, params, monkeypatch):
    lookup = Mock()
    monkeypatch.setattr("apps.pages.tools.comparison_columns", lookup)
    response = client.get(reverse("compare_repositories"), params)
    html = response.content.decode()
    assert response.status_code == 200
    assert response.headers["X-Robots-Tag"] == "noindex, follow"
    assert 'role="alert"' in html
    assert "<script>alert(1)</script>" not in html
    assert "x" * 256 not in html
    lookup.assert_not_called()


@pytest.mark.django_db
def test_comparison_does_not_mutate_catalog_and_refuses_post(client, catalog):
    before = list(Repository.objects.values())
    assert (
        client.post(
            reverse("compare_repositories"), {"first": "psf/requests", "second": "encode/httpx"}
        ).status_code
        == 405
    )
    client.get(reverse("compare_repositories"), {"first": "psf/requests", "second": "encode/httpx"})
    assert list(Repository.objects.values()) == before


def test_tools_are_discoverable_with_actual_edit_date():
    sitemap = StaticViewSitemap()
    for name in ("tools", "compare_repositories"):
        assert name in sitemap.items()
        assert sitemap.location(name) == reverse(name)
        assert sitemap.lastmod(name).date().isoformat() == "2026-10-27"


def test_methodology_meets_content_and_accessible_diagram_contract():
    html = render_to_string("pages/partials/comparison_methodology.html")
    words = strip_tags(html).split()
    assert 600 <= len(words) <= 1200
    assert 'role="img"' in html
    assert '<title id="compare-repositories-flow-title">' in html
    assert '<desc id="compare-repositories-flow-desc">' in html
    assert "currentColor" in html
    for path in (
        "/blog/github-star-growth/",
        "/blog/how-to-shortlist-github-repositories/",
        "/repos/",
        "/lists/",
    ):
        assert f'href="{path}"' in html
