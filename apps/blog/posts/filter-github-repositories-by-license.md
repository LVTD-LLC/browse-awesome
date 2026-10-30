---
title: "Filter GitHub repositories by license, then check the files"
seo_title: Filter GitHub repositories by license | Browse Awesome
description: >-
  To filter GitHub repositories by license, choose a stored license label to narrow
  your search, then inspect each candidate's upstream files at a fixed revision.
  An exact-label filter can omit a dual-licensed project. Remove the label before
  ruling out a candidate, and record what the source actually declares.
meta_description: Filter GitHub repositories by license, recover overlooked dual-licensed projects, and check a pinned ripgrep example before narrowing your shortlist.
published_at: 2026-10-30T22:21:00+00:00
updated_at: 2026-10-30T22:21:00+00:00
author: Browse Awesome Team
author_type: Organization
image: /static/brand/awesome-repos-social.png
image_alt: Browse Awesome repository discovery
categories:
  - Repository evaluation
tags:
  - Licenses
  - Repository discovery
keywords:
  - filter GitHub repositories by license
  - GitHub license label
  - dual licensed repository discovery
---

A license filter helps you narrow a repository search. It cannot inventory every license in each project. The distinction matters when a project declares alternatives: its catalog record may carry one label even though its source names another option you are looking for.

This walkthrough follows **ripgrep** from Browse Awesome's stored `Unlicense` label to upstream files declaring `Unlicense OR MIT`. The catalog and linked source files were checked on October 30, 2026, UTC. The purpose is to recover a discovery candidate worth reviewing, not to approve a license, settle compatibility, or certify the files in a release.

1. Start with a task and a license label.
2. Remove the label to check what it excludes.
3. Read the upstream declaration at a fixed commit.
4. Save a scoped evidence note and a next check.

## 1. Filter GitHub repositories by a stored license label

Open [Browse Awesome's repository search](/repos/) and enter a task term. Expand **More filters**, then use **License label** to choose a stored value. You can search the public catalog without an account. The catalog covers repositories found in awesome lists, not every repository on GitHub.

For this example, compare [a ripgrep search with the MIT label](/repos/?q=ripgrep&license=MIT) with [the same search using Unlicense](/repos/?q=ripgrep&license=Unlicense). These links keep the task text unchanged and vary only the label. They do not ask the catalog to interpret license expressions or determine whether a project meets your organization's requirements.

The filter checks the repository's **exact stored label**, ignoring letter case. It does not expand an alternative expression into every license that appears in it. It also does not inspect every file on each search. The interface's label choices are metadata available in the catalog, not a list of legal conclusions.

GitHub has its own [license search qualifier](https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories#search-by-license). For example, GitHub documents `license:mit` in repository searches. Its license and license-family behavior is a separate interface; do not assume the same query syntax or matching behavior applies to Browse Awesome. Use the catalog field for catalog labels and GitHub's documentation for GitHub search.

**Finish this step with:** the task term, selected label, and repository identity you want to investigate. A matching label is a reason to open the evidence, not permission to reuse the project.

## 2. Remove the license filter before ruling out a candidate

During the check for this article, Browse Awesome's ripgrep record carried `Unlicense`. An exact `MIT` label search therefore did not include that record, while the `Unlicense` search did. That describes this catalog observation; it is not a permanent promise about future results or a conclusion that the record is corrupt.

Open [the ripgrep search without a license filter](/repos/?q=ripgrep). Removing the label preserves the task text, so you can examine candidates the label excluded. When reproducing this with another task, keep the task term and remove the license field rather than replacing your whole search with a broad popularity ranking.

Why do this before discarding a candidate? A filter can answer “which records have this label?” without answering “which projects declare this license anywhere relevant?” Those questions overlap, but they are not identical. A missing result establishes only that it did not match the current search and filters. Save the broader search beside your filtered one so a colleague can repeat the comparison.

If the broader search still misses the project, check its exact owner and repository name upstream. It may be outside Browse Awesome's catalog, excluded by another refinement, or described with different terms. Do not infer a licensing conclusion from a failed discovery query. For help narrowing the task itself, use the [repository shortlisting workflow](/blog/how-to-shortlist-github-repositories/).

**Finish this step with:** either a recovered candidate or an explicit unresolved discovery question. Keep “not found in this search” separate from “checked and unsuitable.”

## 3. Read the upstream files at a fixed revision

Follow the candidate to its original repository. Open its licensing files and save commit-pinned links rather than relying only on a moving default branch. The pinned links let another reader revisit the same text, even after the project changes.

At ripgrep commit `91f5d22`, the project's [COPYING file](https://github.com/BurntSushi/ripgrep/blob/91f5d22ef48bde459d90a8c7dbeab416e97d0f2b/COPYING) describes dual licensing under Unlicense and MIT. The [package's Cargo.toml](https://github.com/BurntSushi/ripgrep/blob/91f5d22ef48bde459d90a8c7dbeab416e97d0f2b/Cargo.toml) declares `Unlicense OR MIT` in its license field. Reading those files answers a narrower, checkable question: what does this project declare at this revision?

That is enough to reopen the candidate for review after an MIT-label search omitted it. It is not enough to approve every intended use. Read the actual license texts referenced by the declaration, identify the files or package you intend to use, and take unresolved obligations or compatibility questions to the person responsible for that review.

GitHub's [license detection documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository#detecting-a-license) explains that multiple licenses or other complexity can affect detection. Its [REST license documentation](https://docs.github.com/en/rest/licenses/licenses#about-licenses) also distinguishes repository license detection from dependency licenses and other documentation references. A recognized repository label is not an inventory of everything your application will include.

Do not combine a current catalog label and a pinned source declaration into a story about every historical version. Record them as separate observations, with their dates. If you intend to use a release rather than the default branch, repeat the file check at that release's corresponding source revision and inspect the artifact you will actually obtain.

**Finish this step with:** a repository identity, exact revision, file paths, and a narrow statement supported by those files. Leave unchecked dependencies, packaged files, or version differences visible.

## 4. Keep a license-evidence note, not a pass badge

Copy the fields below into your candidate worksheet. They keep discovery metadata separate from source evidence and from the decision your team still needs to make.

| Field | What to record |
| --- | --- |
| Candidate and task | Exact owner/repository and the job you need it to do |
| Catalog observation | Stored license label, search filters, and date checked |
| Upstream revision | Commit or release revision you inspected |
| Source evidence | Pinned declaration and license-file links |
| Intended material | Source files, package, or distributed artifact under review |
| Unresolved question | What the files you opened do not establish |
| Next check | A named action, such as reviewing release notices or dependency evidence |

For the worked example, the note would separate the catalog's `Unlicense` label from the pinned project's `Unlicense OR MIT` declaration. Its next action would be to inspect the license texts and the exact material relevant to the intended use. It would not say “MIT-approved” or “all dependencies checked.”

A blank or `NOASSERTION` label also leaves work to do. Browse Awesome treats these as missing or unclassified discovery metadata, not permission to reuse software. Go upstream and record what you find; if the evidence is still unclear, preserve that uncertainty rather than substituting a familiar label.

You can use the [repository comparison tool](/tools/compare-github-repositories/) to keep stored catalog facts beside another candidate. It does not decide license compatibility or assign a winner. Bring the evidence note to the review instead of asking a metadata table to make that decision.

## Check whether the source is the thing you will obtain

A repository and a packaged product can have different licensing information. Before reviewing a candidate, name the thing you intend to obtain: source at a commit, a package version, a downloadable application, or an extension. Record its source or download location so the next reviewer is answering the same question.

For example, [Microsoft's VS Code repository README at a fixed commit](https://github.com/microsoft/vscode/blob/a0c551871c44cd005b777e7a42c818f035adbe16/README.md) points to the source repository's MIT license. Microsoft's [VS Code FAQ](https://code.visualstudio.com/docs/supporting/faq#_what-is-the-difference-between-the-vscode-repository-and-the-microsoft-visual-studio-code-distribution) separately distinguishes that source from the Visual Studio Code distribution and its product license. A repository label should not erase that distinction.

The useful next step is to follow the documentation for the artifact you plan to use, not transfer the repository's label to every related download. This article has not built VS Code, audited its distribution, or reviewed extension terms. The example illustrates which evidence to collect, not what use is permitted. If your intended material changes during evaluation, update the note and repeat the relevant checks instead of carrying the old conclusion forward.

## Common mistakes this workflow avoids

**Treating an omitted result as a rejected project.** The ripgrep example shows a candidate can disappear because of exact-label matching. Clear the relevant filter, keep your task text, and investigate the source before drawing a broader conclusion.

**Turning one declaration into an inventory.** A root file and a package field are useful evidence about those declarations. They do not establish that you inspected every dependency, bundled component, asset, or distributed file.

**Losing the revision.** A saved branch URL may show different content next month. Preserve pinned links in the decision note, and separately check current upstream changes when returning to the candidate.

Start with a [task-specific repository search](/repos/), narrow it with a label when useful, then check what that narrowing leaves out. Stop when you have evidence for the next review, not when a search result looks like an approval.
