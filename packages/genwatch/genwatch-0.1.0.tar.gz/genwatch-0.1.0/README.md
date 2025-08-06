Here’s a starter **README.md** for your **genwatch** package. Feel free to tweak wording, add badges, or expand the examples as you like.

````markdown
# genwatch

Lightweight decorator and proxy for tracing Python generator internals  
(`send`, `throw`, `close`, and `yield from` delegation) with structured logs.

---

## Features

- **Decorator** (`@genwatch.Reporter`) to wrap any generator function
- **Automatic forwarding** of `send()`, `throw()`, and `close()` calls
- Logs **enter/exit** of each `yield from` delegation
- Captures **generator attributes** (`gi_code`, `gi_frame`, `gi_running`, `gi_suspended`, `gi_yieldfrom`)
- Handles both **generator** and **iterator** delegates (`range`, lists, etc.)
- Early **TypeError** if decorating a non-generator function

---

## Installation

```bash
pip install genwatch
````

Or, if you’re installing from source:

```bash
git clone https://github.com/yourusername/genwatch.git
cd genwatch
pip install -e .[test]
```

---

## Quickstart

```python
import logging
from genwatch import Reporter

# Create a logger (optional – Reporter will default to a StreamHandler)
logger = logging.getLogger("myapp")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s"))
logger.addHandler(handler)

@Reporter(logger=logger)
def countdown(n: int):
    """Yield numbers 0..n-1, then finish."""
    for i in range(n):
        yield i

# Drive the generator
gen = countdown(3)
for x in gen:
    print("Got:", x)
# Logs will show the internal state at each yield.
```

### Delegation example

```python
@Reporter(logger=logger)
def subgen():
    yield "a"
    yield "b"

@Reporter(logger=logger)
def outer():
    # Logs will show entry into `subgen`, its locals, and exit
    yield from subgen()
    yield "done"

for v in outer():
    print(v)
```

---

## API

### `genwatch.Reporter`

Decorator for generator functions. Wraps a function so that:

* Calling the wrapped function returns an iterator that proxies through a `_ProxyReporter`.
* On each `next()`, `send()`, `throw()`, and `close()`, logs generator internals.
* Requires Python 3.8+.

```python
@Reporter
def mygen():
    yield 1
    yield 2
```

**Raises** `TypeError` if applied to a non-generator function.

---

## Running Tests

Your tests live in the `tests/` directory. To install test dependencies and run:

```bash
pip install -e .[test]
pytest
```

You’ll see a suite of **passing** tests, plus a few **xfail** demos highlighting current limitations.

---

## Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/xyz`)
3. Write code, add tests, update docs
4. Open a Pull Request

---

## License

This project is licensed under the **Apache 2.0 License**. See the [LICENSE](LICENSE) file for details.
