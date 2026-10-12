"""Shared iteration machinery lives once on the abstract base class `Sequence`;
each concrete subclass supplies only its own list-building formula.

`_validate_length(length)` runs once, when a sequence is constructed, to
reject a non-int or negative `length` before it's ever stored — `length`
only governs the default iteration protocol (`__iter__`/`__next__`); it
does not bound what `return_sequence`/`return_nth_term` can be asked for.

`compute_sequence(n)` is the `@abstractmethod` hook each subclass implements:
it builds and returns a list of the first `n + 1` terms. `_terms(n)` caches
the result as a single, monotonically growing prefix — "the most terms
computed for this instance so far." A request for an `n` already covered
by that prefix is free (just a slice/index); only a request past the
current high-water mark calls `compute_sequence` again. Because every
caller (`__next__`, `return_sequence`, `return_nth_term`) shares that one
growing cache, there's never ambiguity about what it represents.

`Sequence` is declared abstract (via `abc.ABC` + `@abstractmethod`) so
it can never be instantiated directly, and so every subclass is forced
to implement `compute_sequence` or fail at class-definition/instantiation
time rather than with a confusing runtime AttributeError later.
"""

from abc import ABC, abstractmethod


class Sequence(ABC):
    """Abstract base for a sequence you can iterate over `length` terms of,
    or query directly for an arbitrary number of terms.

    Subclasses only need to implement `compute_sequence(n)` — building the
    list of the first `n + 1` values of the sequence. This class owns the
    iterator protocol (`__iter__`/`__next__`, driven by `length`), validates
    `length` and any explicitly-requested `n` (via `_validate_index`), and
    caches computed terms (via `_terms`) as a single growing prefix so no
    term is ever computed from scratch twice.
    """

    def __init__(self, length=10):
        """Validate `length`, reset the iteration cursor, and clear the term cache."""
        self.length = self._validate_index(length, "length")
        self.index = 0
        self._cache = []

    def __iter__(self):
        """A Sequence is its own iterator."""
        return self

    def __next__(self):
        """Produce the next term, or stop once `length` terms are yielded.

        Reads from the cached term list (see `_terms`) instead of calling
        `compute_sequence` directly, so advancing through all `length`
        terms costs one list build in total, not one per term.
        """
        if self.index < self.length:
            n = self._terms(self.length - 1)[self.index]
            self.index += 1
            return n
        else:
            raise StopIteration

    def _terms(self, n):
        """Ensure the cache covers at least the first `n + 1` terms, then return it.

        The cache holds one monotonically growing prefix — "the most terms
        computed for this instance so far." A request within that range is
        free; only a request past the current high-water mark triggers a
        (single) rebuild via `compute_sequence`. Every caller shares this
        one cache, so there's no ambiguity about what it represents: a
        request for a smaller `n` always slices cleanly out of it.
        """
        if n >= len(self._cache):
            self._cache = self.compute_sequence(n)
        return self._cache

    def _validate_index(self, value: int, name: str) -> int:
        """Reject a non-int or negative `value`; otherwise return it unchanged.

        Used both for `length` (once, at construction) and for any `n`
        passed to `return_sequence`/`return_nth_term`, since both are
        term-count/index values subject to the same constraint.
        """
        if not isinstance(value, int):
            raise TypeError(f"{name} must be an integer, got {type(value).__name__}")
        if value < 0:
            raise ValueError(f"Got {value}: {name} must not be negative")

        return value

    @abstractmethod
    def compute_sequence(self, n):
        """Build and return a list of the first `n + 1` terms — the part each subclass owns.

        Called by `_terms` whenever a request exceeds what's already
        cached. Concrete subclasses implement only this method.
        """

    def return_sequence(self, n):
        """Return the list of the first `n + 1` terms."""
        n = self._validate_index(n, "n")
        return list(self._terms(n)[: n + 1])

    def return_nth_term(self, n):
        """Return the n-th term (0-indexed)."""
        n = self._validate_index(n, "n")
        return self._terms(n)[n]


class FibonacciSequence(Sequence):
    """Fibonacci sequence: term(n) = term(n-1) + term(n-2), term(0) = term(1) = 1.

    Only `compute_sequence` is defined here — iteration, setup, and
    length validation are all inherited unchanged from `Sequence`.
    """

    def compute_sequence(self, n: int) -> list:
        """Return a list of the first `n + 1` Fibonacci terms, built up from the start.

        Builds the list from the two base terms up through index `n`,
        one addition at a time — O(n), not the exponential cost of
        naive recursion.
        """
        fib = [1, 1]

        for i in range(2, n + 1):
            fib.append(fib[i - 1] + fib[i - 2])

        return fib


class TriangleNumberSequence(Sequence):
    """Triangular numbers: term(n) = 0.5 * (n+1) * (n+2), a closed form.

    As with FibonacciSequence, only `compute_sequence` is defined here;
    iteration, setup, and length validation all come from `Sequence`.
    """

    def compute_sequence(self, n: int) -> list:
        """Return a list of the first `n + 1` triangular numbers via the closed-form formula.

        Each term is O(1) to compute — no iteration or recursion needed
        per term, unlike FibonacciSequence — but building the list still
        takes one pass over `0..n`.
        """

        tri = [1]  # Base case: the sequence's 0th term is always defined as 1.

        for i in range(1, n + 1):
            tri.append(round(0.5 * (i + 1) * (i + 2)))

        return tri


if __name__ == "__main__":
    # Same checks as the pre-refactor version, to prove behaviour is
    # unchanged: refactoring should never change what the code does,
    # only how it's structured.

    # Return the list of given sequence 
    def return_list(sequence):
        return([i for i in sequence])
    
    # Testing the return_list function
    def test_sequence(sequence, test_list):
        print(f'Validating 1st 10 {type(sequence).__name__} terms against {test_list}')
        assert return_list(sequence) == test_list, f'Check failed: {type(sequence).__name__} against {test_list}'
    

    cl = FibonacciSequence()
    test_list = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
    test_sequence(cl, test_list) 
    n = 15
    nth_term = cl.return_nth_term(n)
    first_n_terms = cl.return_sequence(n)
    print(f'Fibonacci to {n} terms: {first_n_terms} with nth term being {nth_term}')


    cl = TriangleNumberSequence()
    test_list = [1, 3, 6, 10, 15, 21, 28, 36, 45, 55]
    test_sequence(cl, test_list)
    n = 15
    nth_term = cl.return_nth_term(n)
    first_n_terms = cl.return_sequence(n)
    print(f'Triangle Numbers to {n} terms: {first_n_terms} with nth term being {nth_term}')
