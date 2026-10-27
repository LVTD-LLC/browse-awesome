# Compare GitHub repositories — public implementation contract

Intent owner: `/tools/compare-github-repositories/`. Compare two exact catalog
identities with dated observations and awesome-list source context; never a
quality score, security scan, licensing decision or popularity winner.

## Verifiable sources (method checked October 27, 2026)

- Stored observations and observation clocks: `apps/repos/models.py`, repository
  metadata ingestion, and `apps/repos/comparison.py`. Form submission is a bounded
  local database lookup, not a live GitHub refresh or code execution.
- Archive flag: [GitHub archival documentation](https://docs.github.com/en/repositories/archiving-a-github-repository/archiving-repositories).
  Archived repositories are read-only; not archived does not certify maintenance.
  Missing metadata sync must remain not checked.
- Stars: [GitHub stars documentation](https://docs.github.com/en/get-started/exploring-projects-on-github/saving-repositories-with-stars).
  A stored star count is neither quality nor a measured growth window.
- License labels: [GitHub licensing documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository).
  Public visibility and detected labels do not replace checking actual terms.
- API field meanings: [GitHub repository metadata reference](https://docs.github.com/en/rest/repos/repos#get-a-repository).
  A push is not a release. Method verification date is not observation freshness.

## Interaction and maintenance

Two exact identities, bounded input and source previews, neutral errors and
unobserved states. Default examples depend on actual catalog availability;
Requests/HTTPX demonstrate an evidence question, not interchangeable behavior.
Query results are noindex/follow; the base tool owns indexable discovery.
No outbound fetch, paid lookup, mutation, migration or new client-side module.

Reverify when metadata ingestion, public visibility, source-list routing or the
comparison schema changes. Test per-entry sync/date boundaries; do not hardcode
current GitHub statistics into prose. Keep pair observations and private analytics
outside Git. Separate code/CI, actual browser behavior, deployment and acquisition
outcomes; a checked-in summary does not prove any of them.
