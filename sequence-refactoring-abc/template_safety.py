"""Shared iteration machinery lives once on the abstract base class `Sequence`;
each concrete subclass supplies only its own term-computation formula.

`_validate_length(length)` runs once, when a sequence is constructed, to
reject a non-int or negative `length` before it's ever stored. It is
NOT a general-purpose guard for arbitrary term indices — it is only
ever called with `length`, from `__init__`.

`compute_term(n)` is the `@abstractmethod` hook each subclass implements
with its own formula. `__next__` calls it directly with `self.index`,
which is always a valid, non-negative int by construction (starts at 0,
only ever incremented by 1) — so `compute_term` is never independently
validated per call; it relies entirely on the index values `__next__`
itself is guaranteed to produce.

`Sequence` is declared abstract (via `abc.ABC` + `@abstractmethod`) so
it can never be instantiated directly, and so every subclass is forced
to implement `compute_term` or fail at class-definition/instantiation
time rather than with a confusing runtime AttributeError later.
"""

from abc import ABC, abstractmethod


class Sequence(ABC):
    """Abstract base for a sequence you can iterate over `length` terms of.

    Subclasses only need to implement `compute_term(n)` — the formula
    for the n-th value of the sequence. This class owns the iterator
    protocol (`__iter__`/`__next__`) and validates `length` once, at
    construction, via `_validate_length`.
    """

    def __init__(self, length=10):
        """Validate `length`, then reset the iteration cursor to 0."""
        self.length = self._validate_length(length)
        self.index = 0

    def __iter__(self):
        """A Sequence is its own iterator."""
        return self

    def __next__(self):
        """Produce the next term, or stop once `length` terms are yielded.

        Calls `self.compute_term(self.index)` directly. `self.index`
        is always a valid, non-negative int by construction (set to 0
        in `__init__`, only ever incremented by 1 here), so no
        validation happens on this call — `compute_term` trusts the
        index it's given.
        """
        if self.index < self.length:
            n = self.compute_term(self.index)
            self.index += 1
            return n
        else:
            raise StopIteration

    def _validate_length(self, length: int) -> int:
        """Reject a non-int or negative `length`; otherwise return it unchanged.

        Called exactly once, from `__init__`. Not used anywhere else —
        per-term indices produced during iteration are never
        independently validated, since `__next__` only ever supplies
        values it already knows are valid.
        """
        if not isinstance(length, int):
            raise TypeError(f"length must be an integer, got {type(length).__name__}")
        if length < 0:
            raise ValueError(f"Got {length}: length must not be negative")

        return length

    @abstractmethod
    def compute_term(self, n):
        """Compute the n-th term of the sequence — the part each subclass owns.

        Called directly by `__next__` with `self.index`, which is
        always a valid, non-negative int; this method performs no
        validation of its own. Concrete subclasses implement only
        this method.
        """


class FibonacciSequence(Sequence):
    """Fibonacci sequence: compute_term(n) = compute_term(n-1) + compute_term(n-2),
    compute_term(0) = compute_term(1) = 1.

    Only `compute_term` is defined here — iteration, setup, and
    length validation are all inherited unchanged from `Sequence`.
    """

    def compute_term(self, n: int) -> int:
        """Return the n-th Fibonacci term by building the sequence up from the start.

        Builds a local list from the two base terms up through index
        `n`, one addition at a time — O(n), not the exponential cost
        of naive recursion. Nothing persists between calls; each call
        rebuilds its own list from scratch.
        """
        fib = [1, 1]

        for i in range(2, n + 1):
            fib.append(fib[i - 1] + fib[i - 2])

        return fib[n]


class TriangleNumberSequence(Sequence):
    """Triangular numbers: compute_term(n) = 0.5 * (n+1) * (n+2), a closed form.

    As with FibonacciSequence, only `compute_term` is defined here;
    iteration, setup, and length validation all come from `Sequence`.
    """

    def compute_term(self, n: int) -> int:
        """Return the n-th triangular number via the closed-form formula.

        O(1) — no iteration or recursion needed, unlike
        FibonacciSequence.
        """

        for i in range(1, n+1):
            if n < 1: # Base case: the sequence's 0th term is always defined as 1.
                return 1
            return round(0.5 * (n + 1) * (n + 2))


if __name__ == "__main__":
    # Same checks as the pre-refactor version, to prove behaviour is
    # unchanged: refactoring should never change what the code does,
    # only how it's structured.

    # Return the list of given sequence 
    def return_list(sequence):
        return([i for i in sequence])
    
    # Testing the return_list function
    def test_sequence(sequence, test_list):
        print(f'Checking: {type(sequence).__name__} against {test_list}')
        assert return_list(sequence) == test_list, f'Check failed: {type(sequence).__name__} against {test_list}'
    

    cl = FibonacciSequence(10)
    test_list = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
    test_sequence(cl, test_list) 
    n = 10
    cl = FibonacciSequence(n)
    print(f'Fibonacci to {n} terms: {return_list(cl)}')


    cl = TriangleNumberSequence(10)
    test_list = [1, 3, 6, 10, 15, 21, 28, 36, 45, 55]
    test_sequence(cl, test_list)
    cl = TriangleNumberSequence(n)
    print(f'Triangle Numbers to {n} terms: {return_list(cl)}')
