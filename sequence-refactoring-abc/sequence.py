"""Before refactoring: two independent, near-identical sequence iterators.

FibonacciSequence and TriangleNumberSequence duplicate the same
"iterate up to `length` terms" machinery (`__init__`, `__iter__`,
`__next__`), and only differ in the maths inside `term`. This is the
starting point for the refactoring exercise: pull the shared behaviour
into a common base class and leave `term` as the one thing each
sequence must define for itself. See template.py in the sibling
sequence-refactoring-abc copy (or this same folder) for the "after".
"""


class FibonacciSequence:
    """An iterator over the first `length` terms of the Fibonacci sequence.

    Defined recursively as term(n) = term(n-1) + term(n-2), with
    term(0) = term(1) = 1. Recursion here is intentionally naive (no
    memoisation), which is fine for the small `length` used in this
    exercise but means each `__next__` call recomputes prior terms
    from scratch.
    """

    def __init__(self, length=10):
        """Store how many terms to produce and reset the iteration cursor."""
        self.length = length
        self.index = 0

    def term(self, n):
        """Return the n-th Fibonacci term (1-based recursion, n >= 0)."""
        if n < 0:
            raise Exception("Not defined for indices < 0")

        if n < 2:
            # Base case: the first two terms are both defined as 1.
            return 1

        return self.term(n - 1) + self.term(n - 2)

    def __iter__(self):
        """A FibonacciSequence is its own iterator."""
        return self

    def __next__(self):
        """Produce the next term, or stop once `length` terms are yielded."""
        if self.index < self.length:
            n = self.term(self.index)
            self.index += 1
            return n
        else:
            raise StopIteration


class TriangleNumberSequence:
    """An iterator over the first `length` triangular numbers.

    Triangular numbers count objects arranged in an equilateral
    triangle (1, 3, 6, 10, ...); term(n) is given directly by the
    closed-form formula 0.5 * (n+1) * (n+2), so unlike Fibonacci this
    one doesn't need recursion to be efficient.
    """

    def __init__(self, length=10):
        """Store how many terms to produce and reset the iteration cursor."""
        self.length = length
        self.index = 0

    def term(self, n):
        """Return the n-th triangular number (n >= 0)."""
        if n < 0:
            raise Exception("Not defined for indices < 0")

        if n < 1:
            # Base case: term(0) is defined as 1.
            return 1

        return round(0.5 * (n + 1) * (n + 2))

    def __iter__(self):
        """A TriangleNumberSequence is its own iterator."""
        return self

    def __next__(self):
        """Produce the next term, or stop once `length` terms are yielded."""
        if self.index < self.length:
            n = self.term(self.index)
            self.index += 1
            return n
        else:
            raise StopIteration


if __name__ == "__main__":
    # Sanity-check both sequences against known values before refactoring,
    # so the "after" version can be checked against the same expectations.
    fib_seq = FibonacciSequence(10)
    fib_seq_list = [i for i in fib_seq]
    print("Fibonacci: ", fib_seq_list)
    assert(fib_seq_list == [1, 1, 2, 3, 5, 8, 13, 21, 34, 55])

    tri_seq = TriangleNumberSequence(10)
    tri_seq_list = [i for i in tri_seq]
    print("Triangle Numbers: ", tri_seq_list)
    assert(tri_seq_list == [1, 3, 6, 10, 15, 21, 28, 36, 45, 55])
