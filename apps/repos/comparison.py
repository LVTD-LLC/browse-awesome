"""Read-only, bounded comparison of identities already in the public catalog."""

import re

from django.db.models import Q

from apps.repos.models import AwesomeListItem
from apps.repos.services import visible_repository_queryset
from apps.repos.stack_detection import stack_label

MAX_IDENTITY_LENGTH = 255
MAX_SOURCE_PREVIEW = 10
MAX_STACK_PREVIEW = 8
# Exact identities only: not arbitrary GitHub paths, URLs or search expressions.
IDENTITY_RE = re.compile(
    r"(?:https://github\.com/)?([a-z0-9](?:[a-z0-9-]{0,37}[a-z0-9])?)/"
    r"([a-z0-9_.-]{1,100})/?",
    re.IGNORECASE | re.ASCII,
)
EXAMPLE_IDENTITIES = ("psf/requests", "encode/httpx")


def parse_repository_identity(value: str) -> str:
    if len(value) > MAX_IDENTITY_LENGTH:
        raise ValueError("Use an owner/repository or its exact https://github.com URL.")
    match = IDENTITY_RE.fullmatch(value.strip())
    if not match or match[2] in {".", ".."} or "--" in match[1]:
        raise ValueError("Use an owner/repository or its exact https://github.com URL.")
    return f"{match[1]}/{match[2]}".casefold()


def _stack_preview(repository):
    stacks = [slug for slug in (repository.detected_stacks or []) if isinstance(slug, str)]
    return [stack_label(slug) for slug in stacks[:MAX_STACK_PREVIEW]]


def comparison_columns(identities: tuple[str, str]) -> list[dict]:
    repositories = (
        visible_repository_queryset()
        .filter(Q(full_name__iexact=identities[0]) | Q(full_name__iexact=identities[1]))
        .only(
            "full_name",
            "owner",
            "name",
            "description",
            "stars",
            "last_synced_at",
            "language",
            "license_name",
            "is_archived",
            "github_pushed_at",
            "detected_stacks",
            "stack_detected_at",
        )
    )
    by_identity = {repository.full_name.casefold(): repository for repository in repositories}
    columns = []
    for identity in identities:
        repository = by_identity.get(identity)
        column = {"identity": identity, "repository": repository}
        if repository is not None:
            sources = list(
                AwesomeListItem.objects.filter(
                    repository=repository,
                    awesome_list__is_active=True,
                    awesome_list__is_disabled=False,
                )
                .select_related("awesome_list")
                .only(
                    "repository_id",
                    "awesome_list_id",
                    "awesome_list__name",
                    "awesome_list__slug",
                    "awesome_list__last_scanned_at",
                )
                .order_by("awesome_list__name", "awesome_list__slug")[: MAX_SOURCE_PREVIEW + 1]
            )
            column.update(
                sources=sources[:MAX_SOURCE_PREVIEW],
                has_more_sources=len(sources) > MAX_SOURCE_PREVIEW,
                stacks=_stack_preview(repository),
            )
        columns.append(column)
    return columns
