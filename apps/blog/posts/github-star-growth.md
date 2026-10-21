---
title: "GitHub star growth: read the baseline first"
seo_title: GitHub star growth explained | Browse Awesome
description: >-
  In a snapshot comparison, GitHub star growth is the change between two observed star counts. A percentage
  divides that change by the earlier count, so its meaning depends on the
  baseline size and the actual observation interval. Compare absolute gains,
  capture dates, and missing history before using growth to prioritize
  repositories for evaluation.
meta_description: Understand GitHub star growth with worked examples, missing-history checks, and Browse Awesome's snapshot windows before comparing repositories.
published_at: 2026-10-22T01:25:00+03:00
updated_at: 2026-10-22T01:25:00+03:00
author: Browse Awesome Team
author_type: Organization
image: /static/brand/awesome-repos-social.png
image_alt: Browse Awesome repository discovery
categories:
  - Repository evaluation
tags:
  - GitHub stars
  - Repository activity
keywords:
  - GitHub star growth
  - GitHub repository growth percentage
  - repository snapshot history
---

A repository gaining 50% can have a smaller net star gain than one gaining 5%. That is not a contradiction: the percentages start from different counts. The harder comparison is between two numbers both labeled “7-day growth” when their observations cover different dates.

This explainer works through those cases using **invented counts and dates**, not a benchmark or a measurement of real projects. The Browse Awesome calculation descriptions were checked against the catalog's source on October 21, 2026, UTC. Use the examples to interpret a result from [repository search](/repos/), then investigate the project itself.

## Absolute growth and percentage growth answer different questions

Absolute star growth subtracts the earlier count from the later count. Percentage growth divides that difference by the earlier count and multiplies by 100. A positive percentage therefore needs an earlier count greater than zero; starting from zero does not produce a meaningful percentage by this formula.

For these synthetic examples, assume the two counts cover the **same observation interval**:

| Example | Earlier stars | Later stars | Change | Percentage |
| --- | --- | --- | --- | --- |
| Small baseline | 20 | 30 | +10 | +50% |
| Larger baseline | 1,000 | 1,050 | +50 | +5% |
| Unchanged counts | 100 | 100 | 0 | 0% |
| Zero baseline | 0 | 5 | +5 | Unavailable |

The small-baseline example ranks higher by percentage. The larger-baseline example ranks higher by absolute gain. Neither ranking establishes which repository solves your problem. Choose the comparison that answers your discovery question, and keep the underlying counts beside the percentage.

The last two rows are different states. An observed change from 100 to 100 supports a zero difference. A change from zero to five supports an absolute gain of five, but division by zero leaves the percentage unavailable. If the earlier count is missing altogether, you cannot derive either change. Do not fill that gap with zero.

## A count difference is not a history of every star event

Two totals show a **net change between observations**. They do not reveal all the additions and removals in between. A total that stays at 100 could reflect no changes, or additions offset by removals.

GitHub also provides historical star buckets. Its [explanation of the star-history endpoint](https://github.blog/engineering/architecture-optimization/from-2500-requests-to-24-rebuilding-star-history-without-the-stargazers/) describes grouping currently active star records by their creation time. Historical unstar records are not retained in that model. A curve reconstructed from surviving stars and a series of totals recorded over time therefore answer different questions; do not assume their historical values must match.

GitHub describes [starring as a way to save interesting projects and show appreciation](https://docs.github.com/en/get-started/exploring-projects-on-github/saving-repositories-with-stars). Neither a star count nor its growth establishes installation, continued use, security, or maintenance quality. Growth can help you decide what to inspect next, not what to deploy.

## Why Browse Awesome can show different growth percentages

Browse Awesome has two baseline-selection rules. They operate on stored catalog data, not a live GitHub count fetched for each page view. The source references below pin the behavior to the version checked for this article.

- **Cards and repository detail:** choose the earliest available snapshot within the seven days preceding the current time. Subtract its count from the repository's current stored count. See the [display-growth calculation](https://github.com/LVTD-LLC/awesome/blob/5a1670a2f0c7b6f3862493d881b946131084b4cd/apps/repos/services.py#L2700).
- **Percentage-growth filters and the “Star growth” sort:** choose the earliest snapshot in the seven days preceding the latest capture, excluding that latest capture itself. Subtract the baseline from the current stored repository count. See the [filter-growth calculation](https://github.com/LVTD-LLC/awesome/blob/5a1670a2f0c7b6f3862493d881b946131084b4cd/apps/repos/services.py#L2591).

The separate **“7-day star gain”** sort uses the card/display calculation. A shared word such as “growth” does not make every control use the same baseline.

### A worked timeline: 50% and 20% can both follow the rules

Assume it is October 22 at noon UTC, the current stored star count is 30, and these are the only stored snapshots. All times below are noon UTC; this is another synthetic example.

| Capture date | Stored stars |
| --- | --- |
| October 14 | 20 |
| October 16 | 25 |
| October 20 | 30 |

The display window starts October 15, seven days before “now.” Its earliest eligible snapshot is October 16: the gain is 30 minus 25, or five stars, and the percentage is **20%**.

The percentage-filter window starts October 13, seven days before the latest capture on October 20. October 14 is eligible: the gain is 30 minus 20, or ten stars, and the percentage is **50%**.

Neither comparison contains observations exactly seven days apart. The window limits where a baseline may be selected; it does not guarantee seven complete days of measurements. Comparing those percentages as if they covered identical dates would be misleading.

## Read missing history before ranking candidates

The repository detail page shows a latest-capture time and a stored-history section. It does **not** print the selected baseline timestamp beside each growth percentage. Inspect the available capture dates where you need a closer comparison; if you cannot establish the interval, record it as unknown rather than inferring it from the label.

One recent snapshot can also produce a displayed zero when its count equals the current stored count. That is not evidence of a full quiet week. The percentage filter requires an earlier snapshot than the latest capture, so the same repository can lack an eligible filter baseline.

“Stars since tracking” has another starting point: the earliest stored capture. It is not necessarily the repository's creation date or its lifetime gain. Check whether stored history exists before interpreting it. Different repositories can have different tracking start dates.

For a practical comparison, record the repository URL, current stored count, available capture dates, absolute difference, percentage, and anything you could not establish. Keep candidates with missing history separate from candidates with measured zero change. If you apply a percentage threshold, remember that a repository without a usable percentage can be excluded because of missing data, not because it failed to attract interest.

## Turn the signal into a useful next check

Start with a relevant category in the [awesome-list directory](/lists/) or a specific catalog search. Compare growth only among projects relevant to your task. Then open a candidate's upstream repository and read what changed, whether it reached a release, and whether it affects the capability you need.

GitHub's [Pulse view summarizes issue, pull-request, and commit activity](https://docs.github.com/en/repositories/viewing-activity-and-data-for-your-repository/using-pulse-to-view-a-summary-of-repository-activity) for a selected period. Use that context rather than treating a count increase as a verdict about the work. For the wider decision, use the [repository-shortlisting worksheet](/blog/how-to-shortlist-github-repositories/) to check fit, licensing, failure behavior, and a small real trial.

Keep the conclusion narrow: “This project gained this many observed stars over these available dates, so I will inspect it.” That is a defensible next step. “This percentage proves the project is the best choice” is not.
