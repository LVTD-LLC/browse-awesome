from urllib.parse import parse_qs, urlsplit

import pytest

from apps.repos.discovery import repository_file_starting_points
from apps.repos.models import Repository
from awesome_repos.sitemaps import RepositorySitemap


@pytest.mark.parametrize(
    ("signals", "expected"),
    [
        (None, []),
        (
            [
                None,
                {"path": "nested/agents.MD", "kind": "file"},
                {"path": "AGENTS.md", "kind": "file"},
                {"path": "nested/CLAUDE.md"},
                {"path": ".github/copilot-instructions.md"},
            ],
            ["AGENTS.md", "CLAUDE.md", ".github/copilot-instructions.md"],
        ),
        (
            [
                {"path": "AGENTS.md", "kind": "directory"},
                {"path": "AGENTS.md.bak"},
                {"path": "nested/PRODUCT.md"},
                {"path": "nested/.github/copilot-instructions.md"},
                {"path": "private@example.com"},
                {"path": " AGENTS.md "},
            ],
            [],
        ),
        ([{"path": "PRODUCT.md"}, {"path": "nested/gemini.md"}], ["PRODUCT.md", "GEMINI.md"]),
    ],
)
def test_file_discovery_uses_supported_filter_semantics(signals, expected):
    entries = repository_file_starting_points(signals)
    assert [entry["label"] for entry in entries] == expected
    for entry in entries:
        url = urlsplit(entry["url"])
        assert url.path == "/repos/"
        assert parse_qs(url.query) == {"has_file": [entry["label"]]}


def test_file_navigation_lastmod_does_not_rewrite_catalog_dates():
    from datetime import UTC, datetime

    from apps.repos.discovery import REPOSITORY_FILE_DISCOVERY_UPDATED_AT

    older = datetime(2026, 1, 1, tzinfo=UTC)
    newer = datetime(2027, 1, 1, tzinfo=UTC)
    repo = Repository(github_pushed_at=older, last_synced_at=older, updated_at=older)
    sitemap = RepositorySitemap()
    assert sitemap.lastmod(repo) == older
    repo.ai_development_signals = [{"path": "AGENTS.md"}]
    assert sitemap.lastmod(repo) == REPOSITORY_FILE_DISCOVERY_UPDATED_AT
    assert repo.updated_at == repo.last_synced_at == repo.github_pushed_at == older
    repo.github_pushed_at = newer
    assert sitemap.lastmod(repo) == newer
