# AGENTS.md — `warehouse-modeling-refactoring`

> See repo root `AGENTS.md` for the practice-session process and repo-wide
> conventions. This file covers only what's specific to this exercise.

**Scenario:** A small sales-warehouse pipeline. Generates synthetic
customers, products, sales, and refunds; loads them into local SQLite; and
runs analytical queries — top customers by region, customer lifetime
value, and net revenue per product after refunds.

**Shape:** Read-only critique — single file, no refactor copy.

**Files:**
- `warehouse.py` — the exercise.
- `data/` — generated at runtime (gitignored), not committed.

**Answer key:** `.answer-key.md`.

**Notes:** `SNOWFLAKE_CONN` is an unused dict with a planted hardcoded
password — a "gotcha," not a real connection. The script actually runs
against the local SQLite file.
