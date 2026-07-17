# AI Research OS — Agent Operating Rules

This repository is a static GitHub Pages site for Michael Kit's AI Research OS.

## Mission

Continuously improve the website as a professional AI research database and editorial dashboard. Preserve the live site at:

- https://kitmike.github.io/ai-research-os/
- https://github.com/kitmike/ai-research-os

## Required workflow

1. Pull/rebase latest `main` before editing.
2. Read `STYLE_GUIDE.md` and preserve the editorial/Gwern-inspired design direction.
3. Use the best available skills for the task: `github-static-site-automation`, `frontend-design`, `deep-research`, `code-review-and-quality`, `performance-optimization`, `github-pr-workflow`.
4. Use MCPs opportunistically when available:
   - `codebase-memory` for code structure/indexing/impact if the site grows beyond trivial static HTML.
   - `context7` for up-to-date docs on web standards/libraries/actions if adding dependencies.
   - Browser/Playwright for live-site QA when available.
5. Keep the site dependency-light unless a clear user-facing benefit justifies complexity.
6. Validate before commit: JSON parses, key HTML sentinels exist, GitHub Pages workflow YAML parses or is syntactically plausible, and live URL works after deployment.
7. Commit only meaningful changes. If no improvement is warranted, leave git clean and report no-op.
8. Switch GitHub CLI to `kitmike` before GitHub API/git operations.

## Quality bar

- No invented citations or sources.
- Maintain professional UI: readable typography, source ledger, archive, concept dashboard, mobile responsiveness, restrained motion.
- Optimize for robustness: idempotent updates, no duplicate records, no broken links introduced, graceful empty-state handling.
