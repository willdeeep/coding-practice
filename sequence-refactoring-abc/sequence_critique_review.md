# Critique Review — `sequence.py` (2026-09-27)

Exercise: first structured critique pass under the `AGENTS.md` process, run
as a dry test of that process against an exercise already completed
(`sequence.py`, original pre-refactor version). Format follows the "Final
feedback" headings defined in `AGENTS.md`, plus two sections the process
doesn't explicitly capture but are worth tracking over time: process
self-corrections, and best-practice principles raised.

## TL;DR

Correctly identified both headline issues in the file (duplication →
Template Method / `ABC`; naive recursion → exponential time) and reasoned
soundly about a third (generic `Exception` → specific types), but needed
probing to get from "noticed something's off" to "named the actual
mechanism" on two of the three. Strongest single trait: genuine,
well-calibrated uncertainty — flagged what needed research rather than
guessing, and dropped an incorrect claim (Liskov Substitution) the moment
it didn't hold up under its own logic.

## Refactoring issues identified

| Issue | Refactoring | Found unprompted? |
|---|---|---|
| Duplicated `__init__`/`__iter__`/`__next__` across `FibonacciSequence`/`TriangleNumberSequence` | Pull Up Method into a `Sequence` base class | Yes |
| Base class could be instantiated with no valid `term` | `ABC` + `@abstractmethod` (Template Method pattern) | Yes |
| Duplicated negative-index guard inside both `term` methods | Pull Up Method (guard as its own concern, separate from calculation) | Yes |
| Repeated build/print/assert shape in `__main__` | Extract Method | Yes |
| `FibonacciSequence.term` — naive recursion, exponential time (`O(2ⁿ)`-ish) | Memoisation, or rebuild iteratively from base cases | **No — surfaced only after direct probing** |
| `raise Exception(...)` — generic exception type | Split into `TypeError` (wrong type) / `ValueError` (wrong value), matching the convention already used in this repo's `_validate_index` | **No — surfaced only after direct probing** |

## Process — self-corrections made during the session

Worth tracking over time, separately from the technical findings — these
are moments reasoning was adjusted *during* the exercise, not mistakes
that simply went uncorrected:

- **Liskov Substitution → retracted.** Initial claim: making `Sequence`
  abstract was required by LSP. Retracted correctly, unprompted, once
  asked to state precisely what would break — recognised a concrete
  do-nothing `term` would still be substitutable, so LSP wasn't actually
  the mechanism at play.
- **"Why abstract" conflated with DRY, then disentangled.** The retraction
  above first landed on "avoids duplicate logic," which explains the
  *guard clause* pull-up but not the abstract-method decision. A second
  round of probing separated the two: DRY justifies deduplicating the
  guard; **fail-fast** (catching a missing override at construction,
  not at first use) justifies the abstract base.
- **Factorial → exponential.** First attempt at the recursion's growth
  rate landed on "factorial," with the arithmetic itself trailing off
  mid-calculation. Corrected after being pointed at the actual branching
  mechanism (2 children per call) rather than an ordering/arrangement
  count.

## Best-practice principles raised (correctly, and where terminology landed)

- **DRY** — arrived at correctly, named correctly, once prompted.
- **Fail-fast** — the general principle ("caught at construction, not in
  production") was self-generalised well, after the ABC/DRY conflation
  above was resolved.
- **Template Method pattern** — named correctly and unprompted for the
  base-class/hook shape.
- **Specific exception types over generic ones** — reasoning was sound
  and well-illustrated (retryable vs. fatal failure example) even before
  being connected to this file's actual code; correctly extended to spot
  that a *type* check was missing from the guard entirely, not just that
  its exception type was too generic. (Fuller treatment of this topic
  already lives in `exceptions_notes.md` — this session's contribution
  was applying it to a concrete guard clause, not the general principle
  itself.)
- **Recursion / memoisation** — named "recursive" unprompted as the key
  property of `FibonacciSequence.term` (after initially describing the
  mechanism without naming it), and correctly named memoisation as the
  standard fix once the complexity issue was resolved.

## Assessment against the `AGENTS.md` rubric

**Prioritisation.** Right call (duplication as the top issue), but arrived
reconstructed through conversation rather than stated as a clean "top two,
because X" up front. The recursion issue wasn't in the original priority
list at all, despite being the more textbook finding.

**Terminology.** Good range (SOLID, Template Method, `ABC`, DRY,
recursion). Two gaps worth deliberate review: **factorial vs. exponential**
growth is a real conceptual gap, not a naming slip; and "geometric vs.
arithmetic progression" isn't the right frame for generalising to new
sequence types — **linear recurrence relation** (Fibonacci-shaped) vs.
**closed-form/explicit formula** (Triangle-shaped) is.

**Uncertainty calibration.** Strongest trait this session. Flagged
extensibility and large-`n` optimisation as needing research rather than
guessing, and correctly separated "haven't looked yet" from "genuinely
can't be determined from what's here" once pushed (part of the
"optimisation" question was actually just readable from the code — the
recursion itself — not a research question at all).

**Communication and compression.** Opening critique blended prioritisation
and reasoning rather than leading with the headline first. See the
compressed version below.

**Answer closure.** Consistently good — every round, including the
follow-up probes, closed when the point landed rather than over-extending.

## A stronger version of the opening answer

> "Two things I'd prioritise: first, the duplicated `__init__`/`__iter__`/
> `__next__` plus the duplicated guard clause inside `term` — Pull Up
> Method into a `Sequence` base using `ABC`/`@abstractmethod` (Template
> Method pattern), so the base can't be instantiated without a real
> `term`, and a missing override in a new subclass fails immediately at
> construction instead of silently returning `None` or crashing
> confusingly downstream. Second, `FibonacciSequence.term` is naive
> recursion with overlapping, uncached subproblems — exponential time,
> unusable much past `n≈35` — fixable by memoising or building
> iteratively from the base cases up. After that I'd extract the repeated
> build/print/assert pattern in `__main__` — Extract Method."

## Glossary candidates (for the terms/definitions notes)

New or sharpened this session — cross-check against what's already
captured elsewhere before duplicating:

- Template Method pattern
- Pull Up Method / Extract Method (refactoring-pattern names, as distinct
  from the *reason* to apply them)
- Fail-fast (as distinct from, and complementary to, DRY)
- Exponential vs. factorial time complexity — the distinguishing question:
  is this counting *arrangements* (factorial) or *branching calls*
  (exponential)?
- Linear recurrence relation vs. closed-form/explicit formula
- `TypeError` vs. `ValueError` as a matched pair for guard clauses
  (type-check vs. value-check) — general exception-type material already
  lives in `exceptions_notes.md`

---

*Written by request, as a session record for the user's own markdown
notes project. Structure follows the "Final feedback" section of
`AGENTS.md` in this repo — a future session reading both files should be
able to reconstruct not just what was found in `sequence.py`, but how
this critique is progressing over time, which is what `AGENTS.md`'s
"Progression of difficulty" section depends on being tracked somewhere.*
