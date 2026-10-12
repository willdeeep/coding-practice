# AGENTS.md — `sequence-refactoring-abc`

> See repo root `AGENTS.md` for the practice-session process and repo-wide
> conventions. This file covers only what's specific to this exercise.

**Scenario:** Class-hierarchy duplication across two number-sequence
iterators (`FibonacciSequence`, `TriangleNumberSequence`) — identical
`__init__`/`__iter__`/`__next__` machinery, differing only in the term
formula. Classic case for extracting a shared (abstract) base class.

**Shape:** Non-standard — this is the oldest exercise and predates the
rest of the repo's conventions. Don't use it as the template for a new
exercise; see root `AGENTS.md` → "Adding a new exercise" instead.

**Files:**
- `sequence.py` — the "before" state; this is the critique target.
- `template.py` — the "after": the refactored reference solution.
- `template_ref.py`, `template_safety.py` — further elaborations
  (caching, input validation) exploring the extension tasks below.
- `GUIDE.md` — walks through the refactor and a second worked example
  (taxable `Employee`s); doubles as this exercise's answer key.
- `FURTHER_REFACTORING_TASKS.md` — extension tasks beyond the base
  refactor.
- `exceptions_notes.md` — the user's own notes on generic-exception
  handling, written during this exercise.
- `sequence_critique_review.md` — a completed critique session log from
  a prior run-through. Contains spoilers; don't read before a fresh
  attempt.

**Answer key:** No `.answer-key.md` here — use `GUIDE.md` (and
`FURTHER_REFACTORING_TASKS.md` for extension-task intent) instead.
