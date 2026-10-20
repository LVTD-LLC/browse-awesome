"""Editorial starting points backed by active catalog records, not fixed URLs."""

from datetime import UTC, datetime
from urllib.parse import urlencode

from django.urls import reverse

from apps.repos.models import AwesomeList
from apps.repos.services import REPOSITORY_BASENAME_FILE_FILTERS, REPOSITORY_HAS_FILE_FILTER_OPTIONS

REPOSITORY_FILE_DISCOVERY_UPDATED_AT = datetime(2026, 10, 19, 22, 20, tzinfo=UTC)


def repository_discovery_files(signals):
    """Use the catalog's exact-path and basename matching rules."""
    if not isinstance(signals, list):
        return []
    paths = {
        str(signal.get("path") or "").lower()
        for signal in signals or []
        if isinstance(signal, dict) and signal.get("kind", "file") == "file"
    }
    return [
        file_path
        for file_path in REPOSITORY_HAS_FILE_FILTER_OPTIONS
        if any(
            path == file_path.lower()
            or (
                file_path.lower() in REPOSITORY_BASENAME_FILE_FILTERS
                and path.endswith(f"/{file_path.lower()}")
            )
            for path in paths
        )
    ]


def repository_file_starting_points(signals):
    """Link only supported, observed file filters; never imply instruction quality."""
    return [
        {
            "label": file_path,
            "url": f"{reverse('repos:search')}?{urlencode({'has_file': file_path})}",
        }
        for file_path in repository_discovery_files(signals)
    ]


LIST_STARTING_POINTS = (
    (
        "awesome-selfhosted/awesome-selfhosted",
        "Run your own services",
        "Explore self-hosted applications, then check deployment needs and licenses upstream.",
    ),
    (
        "vinta/awesome-python",
        "Build with Python",
        "Find Python libraries and tools, then narrow the list to your task and stack.",
    ),
    (
        "agarrharr/awesome-cli-apps",
        "Work in the terminal",
        "Browse command-line apps, then check platform support and installation instructions.",
    ),
    (
        "bradAGI/awesome-cli-coding-agents",
        "Find CLI coding agents",
        "Explore coding agents and harnesses, then check permissions "
        "and platform support upstream.",
    ),
    (
        "public-apis/public-apis",
        "Explore API resources",
        "Browse GitHub-linked resources. The upstream list also covers APIs outside this catalog.",
    ),
)


def awesome_list_starting_points():
    lists_by_source = {
        item.repo_full_name: item
        for item in AwesomeList.objects.filter(
            repo_full_name__in=[source for source, _, _ in LIST_STARTING_POINTS],
            is_active=True,
            is_archived=False,
            is_disabled=False,
        ).only("repo_full_name", "name", "slug")
    }
    return [
        {"title": title, "description": description, "awesome_list": lists_by_source[source]}
        for source, title, description in LIST_STARTING_POINTS
        if source in lists_by_source
    ]


def repository_stack_starting_points(stack_options):
    """Offer a few supported filters only when the public catalog has matches."""
    available = {option["name"] for option in stack_options if option["count"] > 0}
    return [
        {
            "label": label,
            "url": f"{reverse('repos:search')}?{urlencode({'stack': slug})}",
            "action": f"stack_search_{slug}",
        }
        for slug, label in (("django", "Django"), ("fastapi", "FastAPI"), ("nextjs", "Next.js"))
        if slug in available
    ]
