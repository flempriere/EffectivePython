# Item 39: Prefer `functools.partial` over `lambda` Expressions for Glue
Functions


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Many Python API’s accept simple functions as part of their interfaces
- Interfaces can be a friction point when their required convention
  doesn’t exactly match your function structure
- e.g. `reduce`
  - Contained in `functools`
  - Allows for calculating a value from an iterable
- For example, calculating the sum of logarithms of numbers

``` python
import functools
import math

def log_sum(log_total, value):
    log_value = math.log(value)
    return log_total + log_value

result = functools.reduce(log_sum, [10, 20, 40], 0)
print(math.exp(result))
```

    8000.0

- However, sometimes the function we might want to pass to `reduce` may
  not match the signature as cleanly as `log_sum`
- For example we might have the order of the next value and the running
  total switched e.g. `log_sum(value, log_total): ...`
- Could define a lambda function to adapt the interface

``` python
import functools
import math

def log_sum_alt(value, log_total):
    log_value = math.log(value)
    return log_total + log_value

result = functools.reduce(lambda total, value: log_sum_alt(value, total), [10 , 20, 40], 0)
print(math.exp(result))
```

    8000.0

- Lambda works fine for one-offs
  - If the call is repeated we might instead want to define a helper
    function

``` python
import functools
import math

def log_sum_alt(value, log_total):
    log_value = math.log(value)
    return log_total + log_value

def log_sum_for_reduce(total, value):
    return log_sum_alt(value, total)

print(math.exp(functools.reduce(log_sum_for_reduce, [10, 20, 40], 0)))
```

    8000.0

- Another situation is when the interface requires extra arguments
  - e.g. our `log_sum` might let you define the base of the logarithm

``` python
import math

def logn_sum(base, logn_total, value):
    logn_sum = math.log(value, base)
    return logn_total + logn_value
```

- Now to pass to `reduce` need to somehow *predefine* the value of
  `base`
  - Called partial application in functional paradigms (or *currying*)
- We could do so using a `lambda` approach

``` python
import functools
import math


def logn_sum(base, logn_total, value):
    logn_value = math.log(value, base)
    return logn_total + logn_value


result = functools.reduce(
    lambda total, value: logn_sum(10, total, value), [10, 20, 40], 0
)
print(math.pow(10, result))
```

    8000.000000000004

- `functools` provides the `partial` function
  - Makes performing partial application / currying easy to read
- Takes function to partially apply as first argument
- Followed by pinned positional arguments

``` python
import functools
import math


def logn_sum(base, logn_total, value):
    logn_value = math.log(value, base)
    return logn_total + logn_value


result = functools.reduce(functools.partial(logn_sum, 10), [10, 20, 40], 0)
print(math.pow(10, result))
```

    8000.000000000004

- `partial` also lets you pin keyword arguments (See [item
  35](../Item_035/item_035.qmd) and [item 37](../Item_037/item_037.qmd))

``` python
import functools
import math

def logn_sum(logn_total, value, *, base=10):
    logn_value = math.log(value, base)
    return logn_total + logn_value

log_sum_e = functools.partial(logn_sum, base=math.e)
print(log_sum_e(3, math.e**10))
```

    13.0

- The equivalent `lambda` expression is complicated

``` python
import math

def logn_sum(logn_total, value, *, base=10):
    logn_value = math.log(value, base)
    return logn_total + logn_value

log_sum_e = lambda *a, base=math.e, **kw: logn_sum(*a, base=base, **kw)
print(log_sum_e(3, math.e**10))
```

    13.0

- `partial` lets you inspect which arguments have been supplied already

``` python
import functools
import math


def logn_sum(logn_total, value, *, base=10):
    logn_value = math.log(value, base)
    return logn_total + logn_value


log_sum_e = functools.partial(logn_sum, base=math.e)
print(log_sum_e.args, log_sum_e.keywords, log_sum_e.func)
```

    () {'base': 2.718281828459045} <function logn_sum at 0x7f727903f950>

- Prefer `partial` over `lambda`
  - More ergonomic interface
  - Provides extra niceties
- `partial` can’t be used to reorder parameters
  - Here we have to use a `lambda`
- If we need more complicated function composition two techniques are
  - Using closures (See [item 33](../Item_033/item_033.qmd))
  - Accepting functions as part of an interface

## Things to Remember

- `lambda` expressions can succinctly adapt two functions interfaces for
  compatibility
  - Enable argument reordering
  - Pinning parameter values
- `functools.partial` is a generic tool for pinning positional and
  keyword arguments
  - Prefer over `lambda` for improved ergonomics
- Use `lambda` instead of `partial` for reordering arguments
