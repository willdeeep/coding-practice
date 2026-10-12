# AGENTS.md — `s3-ingest-pipeline-refactoring`

> See repo root `AGENTS.md` for the practice-session process and repo-wide
> conventions. This file covers only what's specific to this exercise.

**Scenario:** A small S3-triggered order-ingestion pipeline. Simulates the
shape of a Lambda function triggered by new order files landing in an S3
bucket: lists objects under a prefix, downloads and parses each as CSV,
and loads the parsed rows into a local SQLite table.

**Shape:** Read-only critique — single file, no refactor copy.

**Files:**
- `ingest.py` — the exercise.
- `data/` — generated at runtime (gitignored), not committed.

**Answer key:** `.answer-key.md`.

**Notes:** AWS is mocked in-process with `moto` — no real account, network
access, or credentials needed to run it. `AWS_ACCESS_KEY_ID` /
`AWS_SECRET_ACCESS_KEY` are fake, hardcoded values and are themselves a
planted "gotcha," not something to actually configure.
