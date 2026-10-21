# GitHub star growth — public implementation brief

## Intent and information gain

Definition/explanation owner: `/blog/github-star-growth/`. The existing
shortlisting guide retains the broader project-evaluation intent; its new link
hands off only metric interpretation. The MCP guide retains agent retrieval.

Explain denominator-driven ranking reversal, missing versus observed zero, and
a worked timeline showing why two actual catalog baseline anchors can produce
different percentages. Counts and dates in the examples are explicitly
synthetic arithmetic, not public/private product statistics or benchmarks.

## Verified public sources and limits

- Source revision `5a1670a2f0c7b6f3862493d881b946131084b4cd`:
  `apps/repos/services.py` functions `_annotate_repository_snapshot_metrics`,
  `annotate_repository_recent_growth_metrics`, and
  `repository_performance_summary`; actual search/card/detail templates.
- Both growth helpers subtract a selected stored baseline from current stored
  repository counts. Do not silently substitute the latest snapshot count.
- Current-time and latest-capture-relative windows select available observations,
  not necessarily observations exactly seven days apart. No visible-baseline
  timestamp promise: the UI exposes capture/history context, not that field
  beside every percentage.
- GitHub documentation: saving repositories with stars and Pulse activity.
- GitHub engineering's October 14, 2026 star-history explanation distinguishes
  surviving-star timestamp buckets from a net difference between count snapshots.
  Do not claim that GitHub lacks a history endpoint.

No adoption, maintenance, security, popularity superiority, benchmark, or
full-seven-day coverage claim. No raw analytics, usernames, database rows,
market volumes, or private source details belong in this brief or article.

## Delivery and verification

Reuse Markdown blog rendering, canonical, social metadata, BlogPosting and
BreadcrumbList schema. Confirm sitemap content dates, server-rendered body,
two inbound links including a crawl hub, and at least three in-body links.
No extra client-side JavaScript or model/database changes needed.

Independent source and editorial critics, real mobile/desktop light/dark
rendering, navigation, repository CI, deployment and live checks are required.
This is an implementation brief, not a receipt that any gate passed.

Private research, selection, lifecycle and outcome history: existing dataset
`c3ed745c-5336-4f89-8022-4990c3ecc5d5`, run
`browseawesome:daily-seo:2026-10-22`. Retain all prior experiment windows;
publication and new distribution overlap, so clean attribution is not claimed.
