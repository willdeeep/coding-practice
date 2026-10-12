# AGENTS.md — `coding-practice` repo root

Orientation for a coding agent opening this repo for the first time. This
file is about the **repo as a whole** — layout, environment, and how to add
or maintain exercises. It does not duplicate the exercise-running process;
that lives in the identical `AGENTS.md` inside every exercise folder. Read
*that* file before running an exercise session with the user. Read *this*
file before touching repo structure, dependencies, or creating a new
exercise.

## What this repo is

A growing collection of self-directed practice exercises for a Data
Engineering interview-communication skill: taking technical understanding
the user already has and making it legible under interview conditions
(orient → prioritise → reason → calibrate → close). Each subfolder is one
exercise. New exercises get added over time as the user wants fresh,
unseen material.

## Environment

One shared virtual environment for the whole repo — exercises no longer
carry their own `.venv`.

- Manifest: `pyproject.toml` at repo root, managed with `uv`.
- Setup/update: `cd` to repo root, run `uv sync`.
- Run any exercise script with the root venv active, e.g.:
  `.venv/bin/python orders-etl-refactoring/etl_ref.py`, or activate once
  with `source .venv/bin/activate` and run scripts normally from anywhere —
  they resolve their own paths via `__file__`, not cwd.
- Adding a new exercise that needs a package not already installed: add it
  to `pyproject.toml`'s `dependencies`, then re-run `uv sync` from root.
  Do **not** create a per-exercise `.venv`.

## Layout

```
coding-practice/
├── pyproject.toml / uv.lock / .venv/   shared env (see above)
├── .gitignore                          .venv, caches, .DS_Store, generated data/*.db, data/*.csv
├── AGENTS.md                           this file
└── <exercise-folder>/
    ├── AGENTS.md                       identical pedagogical framework — copy verbatim, don't edit per-exercise
    ├── .answer-key.md                  planted-issue catalogue — assistant-only, don't read before the user's own critique completes
    ├── <name>.py                       clean reference copy (critique+refactor exercises only)
    ├── <name>_ref.py                   the user's working copy, started as a copy of <name>.py
    └── data/                           generated at runtime (gitignored) — not committed
```

Current exercises, for reference:

- `sequence-refactoring-abc` — class-hierarchy duplication (sequences). Oldest exercise; predates some of the conventions below (has extra files like `GUIDE.md`, `FURTHER_REFACTORING_TASKS.md`, a `template_safety.py` variant) — don't treat those extras as the pattern to copy.
- `orders-etl-refactoring` — CSV → transform → SQLite ETL. `etl.py`/`etl_ref.py` pair.
- `warehouse-modeling-refactoring` — SQL warehouse modeling/queries. Single-file critique, no refactor copy.
- `s3-ingest-pipeline-refactoring` — moto-mocked S3 ingestion. Single-file critique, no refactor copy.
- `quick-drills` — many small single-issue, single-file, cold-read drills (≈5 min each) rather than one multi-issue exercise; its own `.answer-key.md` covers every drill in the folder.

Two exercise shapes exist — pick whichever fits the new material:

1. **Critique + refactor** — ship a pristine `<name>.py` plus a `<name>_ref.py` the user edits in place, so there's a before/after diff. Use when the exercise should produce a concrete rewritten artifact.
2. **Read-only critique** — ship just `<name>.py`. Use when the point is spotting and explaining issues verbally, not producing a refactor.

`quick-drills` is a third, distinct shape (many tiny independent files) — only replicate it if deliberately adding another rapid-cycle drill set, not for a normal multi-issue exercise.

## Adding a new exercise

1. Pick a Data Engineering-relevant scenario not already covered (ETL, warehouse/SQL modeling, cloud ingestion, sequences/algorithms, config/validation, streaming, orchestration, etc.) — vary the surface so exercises don't train pattern-matching on a single shape.
2. Decide critique+refactor vs read-only (see shapes above) and create the file(s) accordingly.
3. Write genuinely working code, then plant 2–5 realistic issues spanning categories — duplication/design smell, performance, correctness bug, "gotcha" (works but indefensible, e.g. the SQL-injection style issue in `quick-drills/drill_01`). Integrate issues naturally; don't make the code read like a checklist.
4. Copy an existing exercise's `AGENTS.md` into the new folder unchanged — it's the shared pedagogical contract, not exercise-specific content.
5. Write `.answer-key.md`: one entry per planted issue, with location, category, tier (Critical/Worthwhile/Stylistic — see "Feedback on missed issues" in the per-exercise `AGENTS.md`), and what a good fix looks like. Without this, a future session can't tell "planted gotcha" from "code that just happens to look rough." Every exercise folder owns exactly one `.answer-key.md` of its own — never shared across folders. If the folder holds several small files (quick-drills style), that single file still covers all of them, since they're sub-units of the same exercise folder, not separate exercises.
6. If new dependencies are needed, add them to root `pyproject.toml` and run `uv sync` from repo root.
7. Smoke-test: run the script against the root `.venv` and confirm it completes cleanly before considering the exercise done.

## Monitoring / maintaining existing exercises

- After any dependency change, re-smoke-test the other exercises too — the venv is now shared, so a version bump for one exercise can affect another.
- If an exercise script is edited later, check `.answer-key.md` is still accurate — issues added, fixed, or moved should be reflected there.
- Before committing, check for stray generated artifacts that shouldn't be tracked: `data/*.db`, `data/*.csv`, `__pycache__/`, `.ruff_cache/`, `.mypy_cache/`, `.DS_Store` (the root `.gitignore` already excludes these).
- Never read an exercise's `.answer-key.md` (or equivalent like `sequence-refactoring-abc/GUIDE.md`) while the user's own analysis for that exercise is still in progress — same discipline as stated in every per-exercise `AGENTS.md`, repeated here since this is likely the first file a fresh agent opens.
