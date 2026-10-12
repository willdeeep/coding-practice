"""After refactoring: shared iteration machinery lives in one place.

FibonacciSequence and TriangleNumberSequence no longer each define
their own __init__/__iter__/__next__ — that behaviour was identical
in both, so it now lives once on the abstract base class `Sequence`.
Each subclass is left with exactly the one thing that actually differs
between them: the formula for `term(n)`.

`Sequence` is declared abstract (via `abc.ABC` + `@abstractmethod`) so
it can never be instantiated directly, and so every subclass is forced
to implement `term` or fail at class-definition/instantiation time
rather than with a confusing runtime AttributeError later. See
sequence.py in this folder for the "before" this was refactored from.
"""

from abc import ABC, abstractmethod


class Sequence(ABC):
    """Abstract base for a sequence you can iterate over `length` terms of.

    Subclasses only need to implement `term(n)` — the n-th value of
    the sequence. This class owns everything about *how* to walk
    through those terms (the iterator protocol), so that logic exists
    in exactly one place instead of being copy-pasted per sequence.
    """

    def __init__(self, length=10):
        """Store how many terms to produce and reset the iteration cursor."""
        self.length = length
        self.index = 0

    def __iter__(self):
        """A Sequence is its own iterator."""
        return self

    def __next__(self):
        """Produce the next term, or stop once `length` terms are yielded.

        Delegates to `self.term`, which is supplied by whichever
        concrete subclass (Fibonacci, Triangle, ...) is being iterated.
        """
        if self.index < self.length:
            n = self.term(self.index)
            self.index += 1
            return n
        else:
            raise StopIteration

    @abstractmethod
    def term(self, n):
        """Return the n-th term of the sequence (n >= 0).

        Left unimplemented on purpose: every concrete sequence has its
        own formula for this, and `ABC` + `@abstractmethod` mean Python
        will refuse to instantiate any subclass that forgets to
        override it.
        """
        pass


class FibonacciSequence(Sequence):
    """Fibonacci sequence: term(n) = term(n-1) + term(n-2), term(0)=term(1)=1.

    Only `term` needs defining here — iteration (`__iter__`/`__next__`)
    and setup (`__init__`) are inherited unchanged from `Sequence`.
    """

    def term(self, n):
        """Return the n-th Fibonacci term via naive recursion."""
        if n < 0:
            raise Exception("Not defined for indices < 0")

        if n < 2:
            # Base case: the first two terms are both defined as 1.
            return 1

        return self.term(n - 1) + self.term(n - 2)


class TriangleNumberSequence(Sequence):
    """Triangular numbers: term(n) = 0.5 * (n+1) * (n+2), a closed form.

    As with FibonacciSequence, only `term` is defined here; everything
    else comes from `Sequence`.
    """

    def term(self, n):
        """Return the n-th triangular number via the closed-form formula."""
        if n < 0:
            raise Exception("Not defined for indices < 0")

        if n < 1:
            # Base case: term(0) is defined as 1.
            return 1

        return round(0.5 * (n + 1) * (n + 2))


if __name__ == "__main__":
    # Same checks as the pre-refactor version, to prove behaviour is
    # unchanged: refactoring should never change what the code does,
    # only how it's structured.
    fib_seq = FibonacciSequence(10)
    fib_seq_list = [i for i in fib_seq]
    print("Fibonacci: ", fib_seq_list)
    assert(fib_seq_list == [1, 1, 2, 3, 5, 8, 13, 21, 34, 55])

    tri_seq = TriangleNumberSequence(10)
    tri_seq_list = [i for i in tri_seq]
    print("Triangle Numbers: ", tri_seq_list)
    assert(tri_seq_list == [1, 3, 6, 10, 15, 21, 28, 36, 45, 55])
