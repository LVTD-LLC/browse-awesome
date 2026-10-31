from urllib.parse import parse_qs, urlsplit

import pytest
from django.test import RequestFactory
from django.urls import reverse

from apps.repos.models import AwesomeList, AwesomeListItem, Repository, UserStarredRepository
from apps.repos.views import repository_filter_context


def test_license_recovery_preserves_encoded_multivalue_requirements_without_database():
    request = RequestFactory().get(
        "/repos/?q=task%26evidence&license=MIT&has_file=AGENTS.md&has_file=CLAUDE.md"
        "&stack=django&sort=forks&sort_direction=asc&page=2"
    )
    context = repository_filter_context(
        request=request,
        base_queryset=None,
        search_url="/repos/",
        reset_url="/repos/",
        awesome_lists=[],
        languages=[],
        topic_options=[],
        generated_tag_options=[],
        stack_options=[],
        package_manager_options=[],
        license_options=[],
    )
    url = urlsplit(context["search_without_license_url"])
    assert url.path == "/repos/"
    assert parse_qs(url.query) == {
        "q": ["task&evidence"],
        "has_file": ["AGENTS.md", "CLAUDE.md"],
        "stack": ["django"],
        "sort": ["forks"],
        "sort_direction": ["asc"],
    }


@pytest.mark.django_db
@pytest.mark.parametrize("scope", ["catalog", "list", "starred"])
def test_license_recovery_keeps_scope_and_other_requirements(auth_client, profile, scope):
    awesome_list = AwesomeList.objects.create(
        name="Recovery fixture", slug="license-recovery", source_url="https://github.com/test/list"
    )
    repo = Repository.objects.create(
        full_name="example/ripgrep",
        owner="example",
        name="ripgrep",
        url="https://github.com/example/ripgrep",
        language="Rust",
        license_name="Unlicense",
    )
    AwesomeListItem.objects.create(awesome_list=awesome_list, repository=repo)
    UserStarredRepository.objects.create(profile=profile, repository=repo)
    url = {
        "catalog": reverse("repos:search"),
        "list": awesome_list.get_absolute_url(),
        "starred": reverse("repos:starred"),
    }[scope]
    empty = auth_client.get(url, {"q": "ripgrep", "license": "MIT", "language": "Rust"})
    assert empty.status_code == 200
    assert empty.context["page_obj"].paginator.count == 0
    recovery = empty.context["search_without_license_url"]
    assert urlsplit(recovery).path == url
    assert parse_qs(urlsplit(recovery).query) == {"q": ["ripgrep"], "language": ["Rust"]}
    content = empty.content.decode()
    assert "Remove only license label" in content
    assert "An exact license label can exclude" in content
    assert "/blog/filter-github-repositories-by-license/" in content
    if scope == "starred":
        assert 'data-discovery-action="empty_remove_license"' not in content
        assert 'data-discovery-action="empty_license_guide"' not in content
        assert 'data-discovery-action="filter_license_guide"' not in content
    else:
        assert 'data-discovery-action="empty_remove_license"' in content
    recovered = auth_client.get(recovery)
    assert list(recovered.context["repositories"]) == [repo]
    assert "Remove only license label" not in recovered.content.decode()
    assert not recovered.context["search_without_license_url"]
    repo.refresh_from_db()
    assert repo.license_name == "Unlicense"
