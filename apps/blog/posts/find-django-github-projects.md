---
title: "Find GitHub projects using Django—then check the dependency"
seo_title: Find GitHub projects using Django | Browse Awesome
description: >-
  To find GitHub projects using Django, start with a Django topic or framework filter,
  then inspect each candidate's dependency file at a fixed commit. Check which
  section declares Django and whether it belongs to the application, an optional
  integration, development tooling, or an example before deciding what to study.
meta_description: Find GitHub projects using Django, then verify manifest evidence with real linkding and factory_boy examples and a dependency-role worksheet.
published_at: 2026-10-26T01:20:00+03:00
updated_at: 2026-10-26T01:20:00+03:00
author: Browse Awesome Team
author_type: Organization
image: /static/brand/awesome-repos-social.png
image_alt: Browse Awesome repository discovery
categories:
  - Repository evaluation
tags:
  - Django
  - Dependencies
keywords:
  - find GitHub projects using Django
  - Django dependency evidence
---

Suppose you want a complete Django application to read: models, views, settings, and the decisions connecting them. A Django-tagged testing library may be useful, but it does not answer that task. Before adding another repository to your reading list, establish what its Django dependency actually means.

This walkthrough follows a real catalog match, **factory_boy**, into its source configuration and contrasts it with **linkding**. The source files were inspected on October 25, 2026, UTC, at the commits linked below. This is a manifest-reading exercise, not an installation test, a security assessment, or a ranking of the projects.

The short version:

1. Find candidates with a topic or detected-framework filter.
2. Open the file behind the framework evidence.
3. Read the dependency's section and directory context.
4. Keep or exclude the candidate for your specific learning task.

## 1. Start with a discovery filter, not a verdict

Use [Browse Awesome's detected-Django catalog](/repos/?framework=django) to find candidates from indexed awesome lists. For a different starting point, [GitHub's Django topic](https://github.com/topics/django) groups repositories associated with that topic. These are discovery surfaces, not interchangeable proofs of how software runs.

Browse Awesome's framework filter uses stored dependency-detection results. It is separate from the catalog's topic filter, and it searches the catalog rather than every file on GitHub. A repository can contain several projects, languages, and dependency files. Keep the original task visible while browsing: “a complete application to study” is narrower than “something related to Django.”

Open one candidate's detail page and look for its stack evidence. The useful part is not just the Django label; it is the **file path and dependency name** behind it. Record those before moving upstream. If you are using the [read-only MCP discovery workflow](/blog/search-awesome-lists-with-mcp/), inspect the returned stack evidence and pagination rather than assuming the first results exhaust the catalog.

**Done looks like:** a candidate repository, the reason you opened it, and an evidence path—not a conclusion about its architecture.

## 2. Open the original file and fix the revision

Follow the evidence to the upstream repository. Open the referenced file, then use a commit-pinned link so your note continues to identify the version you inspected. A branch link is useful for checking current changes; it is a weaker record of a decision made today because its contents can move.

Read the whole dependency section, not only the line containing Django. Start with these distinctions, grounded in the [PyPA guide to pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) and [Setuptools dependency documentation](https://setuptools.pypa.io/en/latest/userguide/dependency_management.html):

| Location | What to investigate |
| --- | --- |
| `pyproject.toml`, project dependencies | Dependencies declared for the project; still determine whether it is an application or reusable package. |
| `pyproject.toml`, optional dependencies | An extra's purpose and whether your intended use selects it. |
| `setup.cfg`, `install_requires` | The package's required dependencies. |
| `setup.cfg`, `options.extras_require` | Optional extras, whose names describe intended uses but need context. |
| A requirements file under an examples directory | Which example consumes it, rather than assuming it governs the whole repository. |
| `build-system.requires` | Requirements for the build system, not automatically the running application. |

These are reading cues, not a universal parser. Projects can use other layouts, included requirements files, Poetry configuration, or generated dependency declarations. Follow references and installation documentation when the first file does not settle the question. A file named `pyproject.toml` can contain tool configuration as well as package metadata.

**Done looks like:** a pinned file link, the containing section, and a narrow statement about the declaration. “Django is declared here” is stronger than a search match, but weaker than “this application runs successfully on my machine.”

## 3. Work through the factory_boy match

A Browse Awesome [Django-filtered search for factory_boy](/repos/?framework=django&q=factory_boy) returned **FactoryBoy/factory_boy** during this check. Its recorded Django signal pointed to `setup.cfg` and `examples/django_demo/requirements.txt`. That is a useful match for someone seeking Django-related testing tools. It also provides a concrete reason not to treat the framework label as an application classification.

At commit `ae9f2f4`, [factory_boy's package configuration](https://github.com/FactoryBoy/factory_boy/blob/ae9f2f4650afef0bc9b0925de97f618603233ff8/setup.cfg#L38-L57) lists Faker in `install_requires`. Django is instead listed in the optional extra named `dev`. The separate [Django demo's requirements](https://github.com/FactoryBoy/factory_boy/blob/ae9f2f4650afef0bc9b0925de97f618603233ff8/examples/django_demo/requirements.txt#L1) also include Django.

Those locations change the decision:

- If you want testing tooling with Django-related development and example material, keep investigating this candidate.
- If you want a complete Django application to study, the framework match alone does not satisfy that requirement. Look for application structure and its documented execution path before keeping it in that category.
- Do not conclude that factory_boy never needs Django. The optional development extra and the example explain situations where Django is relevant.

This is **not a demonstrated detection bug**. The detected dependency exists. The mistake would be asking the label to answer a question its evidence does not answer.

Browse Awesome's [detector at the version checked](https://github.com/LVTD-LLC/awesome/blob/b335b234358d05d7f6d0541ceb1b85f5f6c65923/apps/repos/stack_detection.py#L783-L811) collects dependencies from several `setup.cfg` sections, including extras. Its evidence records the dependency and file path without preserving that section's role. The [confidence rule](https://github.com/LVTD-LLC/awesome/blob/b335b234358d05d7f6d0541ceb1b85f5f6c65923/apps/repos/stack_detection.py#L1164-L1169) treats manifest-backed evidence as high confidence. That confidence concerns the detection evidence; it does not certify runtime use, compatibility, or project suitability.

## 4. Contrast a project dependency with an application decision

At commit `27b7303`, [linkding's manifest](https://github.com/sissbruecker/linkding/blob/27b7303baf41bb28babc610ac8eaa486e1ddfab5/pyproject.toml#L1-L20) describes a self-hosted bookmark manager and declares Django in the project's dependencies. That is a different declaration from factory_boy's optional development extra.

For the original task, linkding is a candidate to investigate as an application. The declaration supports that investigation; it does not finish it. Open the project documentation and source tree next, identify the settings and application entrypoints, and check that the behavior you want to study is present. Do not infer the deployed Django version from a manifest's allowed version range.

There is an important counterexample to the shortcut “project dependency means application.” At commit `14998d0`, [Django REST framework's manifest](https://github.com/encode/django-rest-framework/blob/14998d0a735f8ed6abd86751fd6984a9277a1d40/pyproject.toml#L32-L86) also declares Django as a project dependency, while configuring the reusable `rest_framework` package. A reusable library can require Django too. Dependency role and project type are separate checks.

Use this compact decision record to keep them separate:

| Candidate | Observed declaration | What it supports | What remains to check |
| --- | --- | --- | --- |
| factory_boy | Django in a development extra and a nested demo's requirements | Django-related development/example use | Whether its tooling fits your task |
| linkding | Django in project dependencies; bookmark-manager description | An application candidate worth opening | Architecture, installation path, and the behavior you need |
| Django REST framework | Django in project dependencies; reusable-package configuration | A Django-dependent package | Whether you wanted a library rather than an application |

The table describes those pinned sources, not every future revision. It contains no live popularity, maintenance, or compatibility score.

## Keep an evidence note you can revisit

For each serious candidate, save the repository, commit, file path, section, dependency name, role you inferred, and next check. Include the inspection date and an explicit unknown. A useful note might say: “Django appears in the development extra at this revision; I have not checked the integration's runtime requirements.”

Copy this into your notes: **Repository:** __. **Inspected commit and date:** __. **Evidence file and section:** __. **Django's declared role:** __. **Application or package evidence:** __. **Unknown:** __. **Next file to open:** __. **Keep or exclude for this task:** __. Leave an unverified field blank instead of borrowing certainty from the framework label.

Do not substitute a lockfile entry for that classification. A lockfile can record resolved dependencies for an environment without explaining each dependency's role or proving that a running environment matches it. Likewise, an absent catalog label does not establish that a framework is absent: the detector works with a [bounded set of recognized files](https://github.com/LVTD-LLC/awesome/blob/b335b234358d05d7f6d0541ceb1b85f5f6c65923/apps/repos/stack_detection.py#L602-L646) and stored observations, not an exhaustive architectural review.

Once the dependency role matches your task, continue with the [repository-shortlisting worksheet](/blog/how-to-shortlist-github-repositories/) for fit, licensing, and a small real trial. Or return to the [Django-filtered catalog](/repos/?framework=django) with a clearer exclusion rule. The useful outcome is a shorter, better-supported reading list—not the largest collection of Django labels.
