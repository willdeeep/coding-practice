# Refactoring to a Shared Abstract Base Class

This guide walks through the [refactoring exercise](https://python.pages.doc.ic.ac.uk/2020/modules/lab-refactoring/exercise)
in this folder: `sequence.py` is the "before", `template.py` is the
"after". It also generalises the pattern with a second example
(taxable `Employee`s) and compares two ways to express "subclasses
must implement this method": `abc.ABC` + `@abstractmethod` versus
plain `NotImplementedError`.

## 1. What was duplicated

`sequence.py` has two classes, `FibonacciSequence` and
`TriangleNumberSequence`. Side by side, `__init__`, `__iter__` and
`__next__` are **identical** in both:

```python
def __init__(self, length=10):
    self.length = length
    self.index = 0

def __iter__(self):
    return self

def __next__(self):
    if self.index < self.length:
        n = self.term(self.index)
        self.index += 1
        return n
    else:
        raise StopIteration
```

The only thing that actually varies between the two classes is the
body of `term(n)` — the formula for the n-th value. Everything else is
copy-pasted "how do I walk through `length` terms" bookkeeping. That's
the smell this refactor targets: **duplicated behaviour with one
varying piece**, which is exactly what inheritance (or, for
non-behavioural cases, composition) is for.

## 2. The refactor: extract a base class

`template.py` pulls the shared code up into a base class, `Sequence`,
and leaves each subclass with only its own `term`:

```python
from abc import ABC, abstractmethod

class Sequence(ABC):
    def __init__(self, length=10):
        self.length = length
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < self.length:
            n = self.term(self.index)
            self.index += 1
            return n
        else:
            raise StopIteration

    @abstractmethod
    def term(self, n):
        pass


class FibonacciSequence(Sequence):
    def term(self, n):
        if n < 0:
            raise Exception("Not defined for indices < 0")
        if n < 2:
            return 1
        return self.term(n - 1) + self.term(n - 2)


class TriangleNumberSequence(Sequence):
    def term(self, n):
        if n < 0:
            raise Exception("Not defined for indices < 0")
        if n < 1:
            return 1
        return round(0.5 * (n + 1) * (n + 2))
```

Behaviour is unchanged — both versions print the same Fibonacci and
triangular-number lists and pass the same asserts — but there is now
exactly one copy of the iteration logic instead of two. Add a third
sequence (say, powers of two) and it costs one `term` method, not a
whole new `__init__`/`__iter__`/`__next__` trio.

This is the classic **Template Method pattern**: the base class
defines the *shape* of an algorithm (`__next__`: "compute the next
term, advance, or stop"), and defers one *step* of it (`term`) to
subclasses.

## 3. Why declare `Sequence` as abstract at all?

Nothing stops you from writing `Sequence` as an ordinary class with a
`term` method that does nothing:

```python
class Sequence:
    ...
    def term(self, n):
        pass
```

This "works" — subclasses can still override `term` — but it has two
problems the exercise is implicitly asking you to notice:

1. **`Sequence()` can be instantiated directly.** Iterating over a
   bare `Sequence` would silently produce `[None, None, None, ...]}`
   instead of failing loudly. A sequence with no `term` formula isn't
   a valid concept in this domain — it should be impossible to create
   one.
2. **A subclass that forgets to override `term`** is only caught the
   first time someone iterates it (or worse, never, if `None` happens
   to flow through unnoticed downstream code). The mistake is
   detected far from where it was made.

`abc.ABC` + `@abstractmethod` fix both:

```python
from abc import ABC, abstractmethod

class Sequence(ABC):
    @abstractmethod
    def term(self, n):
        pass
```

* `Sequence(...)` now raises `TypeError: Can't instantiate abstract
  class Sequence with abstract method term` immediately.
* Any subclass that doesn't implement every `@abstractmethod` is
  *also* uninstantiable, with the same clear error, naming the exact
  missing method — at the moment you try to construct it, not the
  moment you happen to call it.

Try it in this folder:

```python
>>> from template import Sequence
>>> Sequence()
TypeError: Can't instantiate abstract class Sequence without an implementation for abstract method 'term'
```

## 4. A second example: `Employee` and tax

Sequences are a small example. Here's a more "business logic" shaped
one, since the same duplication pattern shows up constantly outside
maths exercises: three kinds of employee, each taxed differently, but
sharing everything about pay itself.

### Before: duplicated `payslip`/`net_pay` logic

```python
class TemporaryEmployee:
    def __init__(self, name, gross_pay):
        self.name = name
        self.gross_pay = gross_pay

    def tax(self):
        return self.gross_pay * 0.20  # flat rate, no allowances

    def net_pay(self):
        return self.gross_pay - self.tax()


class FullTimeEmployee:
    def __init__(self, name, gross_pay):
        self.name = name
        self.gross_pay = gross_pay

    def tax(self):
        return max(0, self.gross_pay - 1000) * 0.30  # tax-free allowance

    def net_pay(self):
        return self.gross_pay - self.tax()


class Contractor:
    def __init__(self, name, gross_pay):
        self.name = name
        self.gross_pay = gross_pay

    def tax(self):
        return self.gross_pay * 0.15  # flat contractor rate

    def net_pay(self):
        return self.gross_pay - self.tax()
```

Same smell as `sequence.py`: `__init__` and `net_pay` are identical
three times over; only `tax()` differs.

### After: `Employee` base class with an abstract `tax`

```python
from abc import ABC, abstractmethod

class Employee(ABC):
    def __init__(self, name, gross_pay):
        self.name = name
        self.gross_pay = gross_pay

    def net_pay(self):
        return self.gross_pay - self.tax()

    @abstractmethod
    def tax(self):
        """Return the tax owed on this employee's gross pay."""


class TemporaryEmployee(Employee):
    def tax(self):
        return self.gross_pay * 0.20


class FullTimeEmployee(Employee):
    def tax(self):
        return max(0, self.gross_pay - 1000) * 0.30


class Contractor(Employee):
    def tax(self):
        return self.gross_pay * 0.15
```

`net_pay` — the thing every employee has in common — is written once.
`tax` — the thing that legitimately differs per employment type — is
the one abstract seam. And just as with `Sequence`, `Employee()` can't
be constructed on its own, and forgetting `tax()` on a new employee
type (say, `Freelancer`) is caught at construction, not the first time
payroll runs.

## 5. Mimicking `abstractmethod` with plain exceptions

You don't strictly need `abc` to signal "subclasses must override
this" — it's common (and often seen in older code, or languages
without a formal ABC facility) to write:

```python
class Employee:
    def __init__(self, name, gross_pay):
        self.name = name
        self.gross_pay = gross_pay

    def net_pay(self):
        return self.gross_pay - self.tax()

    def tax(self):
        raise NotImplementedError("Subclasses must implement tax()")
```

This *reads* similarly and communicates intent to another developer.
But it enforces the contract at a different — and weaker — point in
time:

| | `ABC` + `@abstractmethod` | `raise NotImplementedError` |
|---|---|---|
| **When a missing override is caught** | At instantiation (`Employee()` / a subclass missing `tax`) — fails immediately, before any real work happens | Only when `tax()` is actually *called* — could be much later, deep in a payroll run |
| **Can the base class be instantiated?** | No — `TypeError: Can't instantiate abstract class ... without an implementation for abstract method 'tax'` | Yes — `Employee("Al", 1000)` succeeds; only blows up if you call `.tax()` |
| **Discoverability for a reader/IDE** | `@abstractmethod` + inheriting `ABC` is a recognised, tool-supported signal (type checkers and IDEs flag incomplete subclasses) | Just a docstring-and-convention; nothing stops a subclass from "half-implementing" and no static tool will warn you |
| **Enforced where multiple abstract methods exist** | Every unimplemented `@abstractmethod` blocks instantiation at once | Each missing method only fails independently, the first time it's called |

Concretely, the plain-exception version lets this happen silently
until it's too late:

```python
underpaid = Employee("New Hire", 2000)   # no error — Employee isn't abstract
print(underpaid.net_pay())               # NotImplementedError, mid payroll run
```

...whereas the `ABC` version stops the mistake before an `Employee` —
or an incomplete subclass of it — can even be built:

```python
underpaid = Employee("New Hire", 2000)
# TypeError: Can't instantiate abstract class Employee without an
# implementation for abstract method 'tax'
```

**When plain `NotImplementedError` is a reasonable choice:** for a
truly optional override (a hook a subclass *may* customise but has a
sensible default-that-happens-to-be-"not supported"), or in small
scripts/exercises where pulling in `abc` is more ceremony than the
problem warrants. **When to reach for `ABC`:** as soon as "every
subclass must implement this" is a real invariant of the design (as it
is for both `Sequence.term` and `Employee.tax` here) — the earlier and
louder failure is worth the one extra import.

## 6. Takeaways from this exercise

* Duplicated method bodies across sibling classes, differing in only
  one part, is the signal to extract a shared base class (Template
  Method pattern).
* `abc.ABC` + `@abstractmethod` turns "please override this" from a
  comment/convention into something Python enforces at instantiation
  time, for both the base class itself and any incomplete subclass.
* `NotImplementedError` mimics the *documentation* of that contract
  but not the *enforcement* — the failure just moves later and gets
  quieter.
* Refactoring should be behaviour-preserving: both `sequence.py` and
  `template.py` produce identical output and pass the same asserts —
  that's how you know the restructuring didn't change what the code
  does, only how it's organised.
