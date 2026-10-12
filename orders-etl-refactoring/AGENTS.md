# AGENTS.md — `orders-etl-refactoring`

> See repo root `AGENTS.md` for the practice-session process and repo-wide
> conventions. This file covers only what's specific to this exercise.

**Scenario:** A small CSV → transform → SQLite ETL pipeline. Generates
synthetic orders, extracts them from CSV, transforms them into per-category
revenue records, rolls up summary views, and loads the result into SQLite.

**Shape:** Critique + refactor.

**Files:**
- `etl.py` — clean reference copy. Don't edit.
- `etl_ref.py` — the user's working copy; this is "the exercise" in
  progress.
- `data/` — generated at runtime (gitignored), not committed.

**Answer key:** `.answer-key.md`.
