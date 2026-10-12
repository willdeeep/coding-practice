# Further Refactoring Practice

Self-test tasks that pick up where `GUIDE.md` left off — after the
`Sequence(ABC)` extraction, a few smaller smells remain in
`template.py`. Each task names the refactoring method to apply, why
it's the right tool here, and what it should achieve. No code is
given — implement each one yourself, then re-run the file and confirm
the existing `assert` checks still pass (behaviour-preserving is the
whole point of a refactor).

Work through them in order; later tasks assume earlier ones are done.

## 1. Pull Up the Duplicated Guard Clause

**Pattern:** Pull Up Method (extract identical code from sibling
subclasses into their shared base class) — the same technique already
used for `__init__`/`__iter__`/`__next__`, applied one level deeper.

**Why appropriate:** the negative-index check at the top of both
`FibonacciSequence.term` and `TriangleNumberSequence.term` is
byte-for-byte identical. That's the exact kind of duplication this
whole exercise is about — it just wasn't visible until the first round
of extraction made `term` the only thing left in each subclass.

**What it achieves:** a single source of truth for "what counts as a
valid index," instead of two copies that could silently drift apart if
one is ever edited and the other forgotten.

**Think about:** where the check should live — inside `__next__`
(which already owns `index`), as a separate helper method the base
class provides, or somewhere else. Each placement has different
implications for whether `term()` stays safe to call directly with an
arbitrary `n`, outside of normal iteration.

## 2. Evaluate "Replace Conditional with Tuple/Collection Membership"

**Pattern:** collapsing a chain of `or`-joined equality checks against
a small, fixed set of values into a single membership test against a
tuple (or set) of those values.

**Applicability check — do this before changing anything:** for each
guard clause, ask whether it tests membership in a finite, discrete
set of values, or an open-ended range/threshold.

- The negative-index guard from Task 1 is unbounded below — there's no
  finite tuple that represents "every negative number," so this
  pattern **does not apply** to it.
- The Fibonacci base-case check, by contrast, is only ever evaluated
  once negativity has already been ruled out, so it's really asking
  "is this one of exactly two special indices?" — a genuinely discrete
  set, and a legitimate candidate.

**Why appropriate (where it fits):** stating the special-cased values
explicitly can better communicate intent when those values are
conceptually specific facts about the sequence's definition (its first
two terms), rather than an arbitrary cutoff.

**What it achieves:** a (possibly) more self-documenting condition in
the one spot where it genuinely applies. Treat it as a judgment call,
not a mandatory change — try it, then decide for yourself whether it
reads better than the range comparison, and be ready to explain your
reasoning either way.

## 3. Replace the Generic Exception Type

**Pattern:** Replace a broad, generic exception with a specific
built-in (or custom) exception type.

**Why appropriate:** `raise Exception(...)` is considered an
anti-pattern in most style guides — a caller can't catch it selectively
without also catching every other kind of failure, and the type itself
tells a reader nothing about what went wrong.

**What it achieves:** the exception type documents the failure mode,
and calling code can catch precisely the error it knows how to handle
without swallowing unrelated bugs.

## 4. Eliminate Redundant Recomputation in `FibonacciSequence.term`

**Pattern:** this one isn't a duplication fix — it's a performance
smell to learn to recognise. Consider it alongside memoisation /
caching, or reworking the calculation to build on previously computed
terms instead of recursing from scratch each time.

**Why appropriate:** as written, `term(n)` recomputes every earlier
term from zero on every call, which is exponential in `n`. A
correctness-preserving refactor from Task 1–3 wouldn't touch this, but
it's exactly the kind of thing a thorough review should still flag —
duplication isn't the only smell worth refactoring away.

**What it achieves:** turns an exponential-time computation into a
linear one. Invisible at `length=10`; very much not invisible once
`length` grows.

## 5. Extract the Duplicated Verification Logic in `__main__`

**Pattern:** Extract Method — pull a repeated "do X, then check the
result" sequence into a single reusable function.

**Why appropriate:** the `__main__` block builds a sequence into a
list, prints it, and asserts it against an expected result — twice,
once per sequence type, in an identical shape with only the data
differing. It's the same "same shape, different data" duplication that
motivated the class-level refactor, just relocated to the script's
entry point.

**What it achieves:** a single small "check this sequence against this
expectation" routine, and a `__main__` block that reads as a short list
of checks rather than two near-identical blocks of setup/print/assert.
