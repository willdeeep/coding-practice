# Exceptions

## The Problem with Generic Excpetions: Masking Distinct Failure Modes
The primary concern is that catching a generic base Exception (like System.Exception or Exception) prevents the caller from distinguishing between different failure modes, leading to incorrect or unsafe recovery actions.

### Key issues include:
- **Undefined Program State:** Catching all exceptions leaves the program in an undefined state because you cannot determine if the failure was recoverable (e.g., **missing file**) or catastrophic (e.g., **out of memory**). This makes it impossible to know what operations were completed and which were not.
- **Masking Bugs:** A generic catch block may silently swallow critical errors like `NullPointerException` or `DivideByZero`, hiding bugs that should be fixed immediately rather than allowing the program to continue with corrupted data or infinite loops.
- **Loss of Specific Context:** Different exceptions represent different problems requiring different handling (e.g., retrying on network timeout vs. failing fast on invalid input). A base exception handler cannot apply this nuanced logic, often resulting in generic logging that makes debugging root causes difficult.
- **Violation of Separation of Concerns:** Lower-level libraries should typically *re-throw* or *wrap* exceptions to provide context, rather than catching and handling them generically. Handling all exceptions at a high level is appropriate for **top-level boundary handlers** (facades) to prevent crashes, but not for selective handling within application logic.

In short, specificity is required for correct error handling; catching only the base exception usually indicates a lack of understanding of the specific risks and a high likelihood of incorrect behavior.


**Masking a bug with a retry loop**

```python
def process_order(order_id: int):
    try:
        order = db.get_order(order_id)   # returns None if not found
        order.status = "shipped"         # AttributeError if order is None
    except Exception as e:
        print(f"Failed, retrying: {e}")
        return process_order(order_id)   # infinite recursion — it's a bug, not transient
```

**Wrong recovery action**

```python
def load_config(path: str) -> Config:
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        # Assumes missing file — overwrites user's config with defaults
        with open(path, "w") as f:
            json.dump(DEFAULT_CONFIG, f)
        return DEFAULT_CONFIG
```

If the real problem was `json.JSONDecodeError` (malformed file), this silently **destroys the user's config**.

```python
# Correct: distinguish the cases
def load_config(path: str) -> Config:
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        # Genuinely missing — create default
        with open(path, "w") as f:
            json.dump(DEFAULT_CONFIG, f)
        return DEFAULT_CONFIG
    except json.JSONDecodeError:
        # Corrupt — alert the user, do NOT overwrite
        raise ConfigError(f"Corrupt config at {path}, please fix manually") from None
```

**Hiding resource exhaustion**

```python
def fetch_rows(sql: str) -> list[Row]:
    try:
        conn = pool.acquire()
        return conn.execute(sql).fetchall()
    except Exception:
        return cached_rows  # silently masks pool exhaustion / OOM
```

---

## When a Generic `except Exception` Is Appropriate

### 1. Top-level boundary (last line of defence)

```python
import sys

def main():
    try:
        run_application()
    except Exception as e:
        logger.critical("Unhandled error", exc_info=e)
        show_crash_dialog(e)
        sys.exit(1)
```

You log and exit — you never try to continue.

### 2. Best-effort ancillary code

```python
def on_page_view(user_id: int):
    try:
        analytics.send("page_view", user_id)
    except Exception:
        pass  # analytics must never break the user's session
```

The response is identical regardless of *why* it failed.

### 3. Catch-and-rethrow for cross-cutting concerns

```python
def instrumented(handler):
    @functools.wraps(handler)
    def wrapper(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except Exception as e:
            metrics.record_error(handler.__name__, e)
            raise  # bare rethrow — preserves type and traceback
    return wrapper
```

You observe and re-raise; the real handler further up still sees the specific exception.

### 4. Untrusted / third-party callbacks

```python
def notify_all(event):
    for listener in _listeners:
        try:
            listener(event)
        except Exception as e:
            logger.error("Listener %s crashed: %s", listener.name, e)
            # continue to next listener
```

You can't enumerate every exception a plugin might raise.

### 5. Batch processing — one item's failure shouldn't halt the batch

```python
def process_batch(items: list[Item]) -> BatchResult:
    successes, failures = [], []
    for item in items:
        try:
            successes.append(process(item))
        except Exception as e:
            failures.append((item, e))
    return BatchResult(successes, failures)
```

---

## The Rule of Thumb (Python-specific notes)

| Situation | `except SpecificError` | `except Exception` |
|---|---|---|
| Different recovery per error type | ✅ | ❌ |
| Response identical for all failures | unnecessary | ✅ |
| Process boundary / `main()` | ❌ | ✅ |
| Logging + bare `raise` | ❌ | ✅ |
| Swallowing and continuing | ❌ almost always | ⚠️ only if truly non-critical |

**Python-specific gotchas to avoid:**

- **Never use bare `except:`** — it also catches `BaseException` subclasses like `KeyboardInterrupt` and `SystemExit`, which you almost never want to swallow.
- **Always prefer `except SpecificError`** when you can name it. The standard library is well-structured: `OSError` family, `ValueError`, `TypeError`, `KeyError`, etc.
- **Use `raise ... from e`** (or `from None`) when wrapping, so the original exception is preserved in `__cause__` for post-mortem debugging.
- **`except Exception` is safe at the boundary** — it will *not* catch `SystemExit` or `KeyboardInterrupt` because those inherit from `BaseException`, not `Exception`. This is Python doing you a favour over C#.


## Handling Nested Try-Except in Python

### 1. Use `else` to avoid unnecessary nesting

The most common mistake is nesting a second `try` inside the first `try` when the second operation only runs if the first succeeded. The `else` clause solves this:

```python
# ❌ Nested — the inner try is inside the outer try
try:
    data = json.load(f)
    try:
        result = process(data)
    except ValueError:
        log.warning("Bad data format")
except FileNotFoundError:
    log.error("Config missing")

# ✅ Flat — else runs only if the try block succeeded
try:
    data = json.load(f)
except FileNotFoundError:
    log.error("Config missing")
else:
    try:
        result = process(data)
    except ValueError:
        log.warning("Bad data format")
```

The `else` block only executes when no exception was raised in the `try` block, so you get the same logical dependency without the indentation penalty.

### 2. Extract to functions when nesting exceeds two levels

If you find yourself at three or more levels of nesting, the code is doing too much in one place. Break it up:

```python
# ❌ Three levels deep — hard to follow
def handle_request(req):
    try:
        conn = acquire_connection()
        try:
            cursor = conn.cursor()
            try:
                cursor.execute(req.query)
            except OperationalError:
                rollback(conn)
            except ProgrammingError:
                log.error("Bad SQL")
        except ConnectionError:
            reconnect()
    except TimeoutError:
        log.warning("Timed out")
```

```python
# ✅ Each level of responsibility gets its own function
def handle_request(req):
    try:
        with acquire_connection() as conn:
            execute_query(conn, req)
    except TimeoutError:
        log.warning("Timed out")

def execute_query(conn, req):
    try:
        with conn.cursor() as cursor:
            cursor.execute(req.query)
    except OperationalError:
        conn.rollback()
    except ProgrammingError:
        log.error("Bad SQL: %s", req.query)
```

Each function has a single, clear error-handling contract. The nesting is still there in the call stack, but it's no longer visually nested in one function body.

### 3. Fallback chain — try alternatives in sequence

When you're trying one thing after another until one works, a loop is cleaner than nested `try` blocks:

```python
# ❌ Deeply nested fallback
try:
    result = parse_v3(data)
except ParseError:
    try:
        result = parse_v2(data)
    except ParseError:
        try:
            result = parse_v1(data)
        except ParseError:
            raise UnsupportedFormat("All parsers failed")

# ✅ Flat loop with break
parsers = [parse_v3, parse_v2, parse_v1]
for parser in parsers:
    try:
        result = parser(data)
        break
    except ParseError:
        continue
else:
    raise UnsupportedFormat("All parsers failed")
```

The `for...else` construct runs the `else` block only if the loop was **not** exited via `break` — i.e., all parsers failed.

### 4. Context managers replace `try/finally` nesting

Resource cleanup is the most common reason for nested `try`/`finally`. The `with` statement eliminates it entirely:

```python
# ❌ Manual cleanup with try/finally
try:
    conn = db.connect()
    try:
        cur = conn.cursor()
        try:
            cur.execute(sql)
        finally:
            cur.close()
    finally:
        conn.close()

# ✅ Context managers handle cleanup automatically
with db.connect() as conn, conn.cursor() as cur:
    cur.execute(sql)
```

If you need a custom context manager that also handles exceptions:

```python
from contextlib import contextmanager

@contextmanager
def retry_on_timeout(max_attempts=3):
    for attempt in range(1, max_attempts + 1):
        try:
            yield
            return  # success — exit the context manager
        except TimeoutError:
            if attempt == max_attempts:
                raise
            log.warning("Timeout, retrying (%d/%d)", attempt, max_attempts)

# Usage
with retry_on_timeout():
    response = http.get(url)
```

### 5. Inner catches must not accidentally swallow outer concerns

A subtle bug: the inner `except` catches an exception that the outer handler was supposed to see.

```python
# ❌ Inner except swallows what the outer handler needs
try:
    try:
        value = int(user_input)
    except ValueError:
        value = 0  # silently coerces — outer code never knows
    expensive_operation(value)
except Exception as e:
    log.critical("Pipeline failed: %s", e)  # never fires for bad input
```

```python
# ✅ Inner handler either recovers fully or re-raises
try:
    try:
        value = int(user_input)
    except ValueError:
        log.warning("Invalid input %r, using default", user_input)
        value = 0
    expensive_operation(value)
except Exception as e:
    log.critical("Pipeline failed: %s", e)
```

The rule: **an inner `except` should only catch what it can genuinely recover from.** If recovery means "pretend it didn't happen and continue," make sure that's actually the correct semantics.

### 6. Exception chaining for context across levels

When an inner handler wraps and re-raises, use `from` so the outer handler sees the full causal chain:

```python
def load_config(path):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise ConfigError(f"Missing config: {path}") from e
    except json.JSONDecodeError as e:
        raise ConfigError(f"Corrupt config: {path}") from e

# Caller
try:
    config = load_config("/etc/app.conf")
except ConfigError as e:
    # e.__cause__ is the original FileNotFoundError or JSONDecodeError
    log.error("Startup failed: %s (caused by %s)", e, e.__cause__)
```

The traceback shows both the original exception and the wrapper, so you get context at every level without losing the root cause.

---

## Summary

| Pattern | When to use |
|---|---|
| `try / except / else` | Second operation depends on first succeeding |
| Extract to function | Nesting > 2 levels; each layer has its own contract |
| `for` loop + `break`/`else` | Fallback chain (try A, then B, then C) |
| `with` statement | Resource acquisition + guaranteed cleanup |
| `@contextmanager` with `yield` | Reusable retry / logging / timing wrappers |
| `raise ... from e` | Wrapping an exception while preserving the original |
| Specific `except` in inner block | Only catch what you can genuinely recover from locally |

