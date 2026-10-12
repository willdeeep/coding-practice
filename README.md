# Coding Practice

A self-directed, growing collection of Data Engineering code-critique
exercises — practice for communicating technical reasoning clearly under
interview-like conditions, not just for finding the bugs.

## Why this exists

Understanding code and explaining your reasoning about it out loud, under
time pressure, in front of someone else, are different skills. This repo
is a practice ground for the second one: each exercise is a small,
genuinely-working script deliberately written with realistic issues —
duplication, performance smells, correctness bugs, and "gotchas" that
technically work but are indefensible in production — pulled from
everyday Data Engineering work (ETL pipelines, warehouse modeling, cloud
ingestion, and more).

Exercises are run with an AI coding assistant acting as a structured
practice partner, following a fixed process (**orient → prioritise →
reason → calibrate → close**) so feedback stays consistent from exercise
to exercise rather than varying with however the conversation happens to
go.

## How it works

Each top-level folder is one exercise:

- A realistic script (or a small handful of related files) with planted
  issues.
- A hidden `.answer-key.md` cataloguing exactly what was planted and
  why — not meant to be read before attempting the exercise, by a human
  or an AI assistant, since that defeats the point.
- An `AGENTS.md` describing the practice process itself: how the
  assistant should run the session, when to stay quiet, and how to give
  feedback. This file is identical in every exercise folder.

Exercises come in a few shapes:

- **Critique + refactor** — a clean reference file plus a working copy to
  edit in place, so there's a before/after diff.
- **Read-only critique** — a single file; the point is spotting and
  explaining issues verbally, not producing a rewrite.
- **Quick drills** — many small, single-issue, cold-read files meant to
  take under five minutes each, for rapid-cycle practice.

See the root [`AGENTS.md`](AGENTS.md) for the full repo layout and the
process for adding new exercises.

## Getting started

Requires [`uv`](https://docs.astral.sh/uv/) and Python 3.14.

```bash
git clone <this-repo>
cd coding-practice
uv sync                        # installs the shared environment once
source .venv/bin/activate      # or prefix commands with `uv run`
python orders-etl-refactoring/etl_ref.py
```

All exercises share one environment at the repo root — there's no
per-exercise setup.

## Exercises

| Folder | Scenario |
|---|---|
| [`sequence-refactoring-abc`](sequence-refactoring-abc) | Class-hierarchy duplication across number sequences |
| [`orders-etl-refactoring`](orders-etl-refactoring) | CSV → transform → SQLite ETL pipeline |
| [`warehouse-modeling-refactoring`](warehouse-modeling-refactoring) | SQL warehouse modeling and analytical queries |
| [`s3-ingest-pipeline-refactoring`](s3-ingest-pipeline-refactoring) | Mocked S3-triggered ingestion pipeline |
| [`quick-drills`](quick-drills) | A set of fast, single-issue cold-read drills |

## Spoiler notice

If you're browsing this repo to attempt an exercise yourself, avoid
opening any `.answer-key.md` (or equivalent, like
`sequence-refactoring-abc/GUIDE.md`) before you've worked through it —
they exist for the practice partner, not for you to read first.
