"""Public server-rendered tools. No upstream fetching or catalog mutations."""

from django import forms
from django.conf import settings
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_safe

from apps.blog.services import json_ld
from apps.repos.comparison import (
    EXAMPLE_IDENTITIES,
    MAX_IDENTITY_LENGTH,
    comparison_columns,
    parse_repository_identity,
)


class RepositoryComparisonForm(forms.Form):
    first = forms.CharField(max_length=MAX_IDENTITY_LENGTH, strip=False)
    second = forms.CharField(max_length=MAX_IDENTITY_LENGTH, strip=False)

    def clean(self):
        cleaned = super().clean()
        for field in ("first", "second"):
            if field not in cleaned:
                continue
            try:
                cleaned[field] = parse_repository_identity(cleaned[field])
            except ValueError as exc:
                self.add_error(field, str(exc))
        if cleaned.get("first") and cleaned.get("first") == cleaned.get("second"):
            self.add_error("second", "Choose a different repository for the second column.")
        return cleaned


def _tool_schema():
    origin = settings.SITE_URL.rstrip("/")
    path = reverse("compare_repositories")
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebApplication",
                "name": "Browse Awesome GitHub repository comparison",
                "url": f"{origin}{path}",
                "applicationCategory": "DeveloperApplication",
                "operatingSystem": "Any",
                "description": "Compare two indexed GitHub repositories using stored catalog "
                "metadata, observation dates and awesome-list source membership.",
                "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": origin + "/"},
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": "Tools",
                        "item": origin + reverse("tools"),
                    },
                    {
                        "@type": "ListItem",
                        "position": 3,
                        "name": "Compare GitHub repositories",
                        "item": origin + path,
                    },
                ],
            },
        ],
    }


@require_safe
def tools_index(request):
    return render(request, "pages/tools.html", {"hide_side_ad_rails": True})


def _prepared_identity(params):
    # A contextual link supplies just the first choice; an actual form submit
    # always includes both fields, including an empty second field.
    if "second" in params or len(params.getlist("first")) != 1:
        return None
    try:
        return parse_repository_identity(params["first"])
    except ValueError:
        return None


@require_safe
def compare_repositories(request):
    # Any query string is a result/variant, not a new indexable landing page.
    has_query = bool(request.GET)
    submitted = "first" in request.GET or "second" in request.GET
    form = RepositoryComparisonForm(request.GET if submitted else None)
    columns = []
    is_example = False
    prepared_identity = _prepared_identity(request.GET)
    comparison_state = "empty"
    if prepared_identity:
        form = RepositoryComparisonForm(initial={"first": prepared_identity})
        comparison_state = "prepared"
    elif submitted:
        comparison_state = "invalid"
        # Do not silently resolve ambiguous duplicate query keys.
        if any(len(request.GET.getlist(field)) > 1 for field in ("first", "second")):
            form.is_valid()
            form.add_error(None, "Enter exactly one identity in each repository field.")
        elif form.is_valid():
            columns = comparison_columns((form.cleaned_data["first"], form.cleaned_data["second"]))
            comparison_state = (
                "compared"
                if all(column["repository"] is not None for column in columns)
                else "unobserved"
            )
    else:
        example_columns = comparison_columns(EXAMPLE_IDENTITIES)
        if all(column["repository"] is not None for column in example_columns):
            columns = example_columns
            is_example = True
            comparison_state = "example"
            form = RepositoryComparisonForm(
                initial={"first": EXAMPLE_IDENTITIES[0], "second": EXAMPLE_IDENTITIES[1]}
            )
    response = render(
        request,
        "pages/compare_repositories.html",
        {
            "hide_side_ad_rails": True,
            "form": form,
            "first_value": str(form["first"].value() or "")[:MAX_IDENTITY_LENGTH],
            "second_value": str(form["second"].value() or "")[:MAX_IDENTITY_LENGTH],
            "columns": columns,
            "is_example": is_example,
            "comparison_state": comparison_state,
            "robots": "noindex, follow" if has_query else "index, follow",
            "schema_json": json_ld(_tool_schema()),
            "canonical_path": reverse("compare_repositories"),
        },
    )
    if has_query:
        response.headers["X-Robots-Tag"] = "noindex, follow"
    return response
