# Item 124: Consider Static Analysis via `typing` to Obviate Bugs


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

> [!NOTE]
>
> Most type-checkers won’t work on raw jupyter notebooks due to the mix
> of python code, metadata and human text. So for this chapter, all the
> examples are also provided as standalone scripts that can be accessed
> through the github.

- Documentation is provided to provide usage help to consumers and
  maintainers (See [Item 118](../Item_118/item_118.qmd))
- However,
  - Not comprehensive
  - Can be misused and lead to further bugs
    - e.g. Documentation diverging from source code
- Compile-time type checking is a programmatic way of verifying usage of
  APIs
  - Common to many languages
  - Not supported by Python (See [Item
    3](../../Chapter_01/Item_003/item_003.qmd))
- Python has introduced syntax for *gradual typing* to enable *static
  type checking*
  - Supported by in-built syntax and the `typing` built-in module
  - variables, classes, fields, functions, methods, parameters, return
    values etc. can be given type information
    - Called *type hints* since they are not enforced at runtime
  - Referred to as gradual typing since it is optional
    - Can be slowly or partially introduced to a codebase
- *static analysis* tools can use type information to verify usage
  patterns
  - `typing` doesn’t do this itself

  - Performed by external tools like

    1.  [`mypy`](https://github.com/python/mypy)
    2.  [`pyright`](https://github.com/microsoft/pyright)
    3.  [`pyre`](https://pyre-check.org/)
    4.  [`pytype`](https://github.com/google/pytype)
    5.  [`ty`](https://docs.astral.sh/ty/)

  - This tools typically have multiple levels of enforcement

    - Generally (especially with greenfield projects) consider using
      `--strict` or equivalent (if supported by your type checker)

    > [!NOTE]
    >
    > In this section, we’ll mostly use `ty` since the logs it produces
    > tend to be elaborate and easy to understand. Occasionally we’ll
    > also use `mypy` since `mypy --strict` has different behaviour for
    > untyped variables than `ty`
- Static analysis tools complement other testing frameworks (See [Item
  109](../../Chapter_13/Item_109/item_109.qmd))
  - Can typically be integrated as a check on code before it is run
- Consider, the code below has an obvious bug (See
  [subtract.py](./Examples/01_Subtract/subtract.py))
  - It has been called with a string type
  - Might seem intuitively obvious
    - But currently nothing in `subtract` identifies or enforces this
  - A static type checker could verify this behaviour without the need
    to run a test

``` python
def subtract(a, b):
    return a - b


subtract(10, "5")
```

    TypeError: unsupported operand type(s) for -: 'int' and 'str'
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[1], line 5
          1 def subtract(a, b):
          2     return a - b
    ----> 5 subtract(10, "5")

    Cell In[1], line 2, in subtract(a, b)
          1 def subtract(a, b):
    ----> 2     return a - b

    TypeError: unsupported operand type(s) for -: 'int' and 'str'

- Parameter and variable annotations are denoted by a colon after the
  name
- Return type annotations from a function or method are preceded by an
  arrow `->` following the argument list (but before the colon) (See
  [subtract_typed.py](./Examples/01_Subtract/subtract_typed.py))

``` python
def subtract(a: int, b: int) -> int:  # Added type annotations
    return a - b


subtract(10, "5")  # Oops: passed string value
```

- The `ty` type-checker will identify this misuse and provide helpful
  diagnostics

``` shell
$ uv run ty check subtract_typed.py

error[invalid-argument-type]: Argument to function `subtract` is incorrect
 --> subtract_typed.py:5:14
  |
5 | subtract(10, "5")  # Oops: passed string value
  |              ^^^ Expected `int`, found `Literal["5"]`
  |
info: Function defined here
 --> subtract_typed.py:1:5
  |
1 | def subtract(a: int, b: int) -> int:  # Added type annotations
  |     ^^^^^^^^         ------ Parameter declared here
2 |     return a - b
  |
info: rule `invalid-argument-type` is enabled by default

Found 1 diagnostic
```

- Type annotations also work at the class level (See
  [class.py](./Examples/02_Class/class.py))
  - The following code demonstrates two common bugs

    1.  `add` doesn’t correctly reference the object’s attribute
        `self.value` but rather creates a local variable `value`
    2.  `get` doesn’t correctly return a value

``` python
# class.py
#
# Demonstrates the use of typing with a class


class Counter:
    def __init__(self):
        self.value: int = 0

    # first issue, not assigning to self.value parameter
    def add(self, offset):
        value += offset

    def get(self) -> int:
        self.value


counter = Counter()

# second issue, missing return
found = counter.get()
assert found == 0, found
```

    AssertionError: None
    ---------------------------------------------------------------------------
    AssertionError                            Traceback (most recent call last)
    Cell In[2], line 22
         20 # second issue, missing return
         21 found = counter.get()
    ---> 22 assert found == 0, found

    AssertionError: None

- Both bugs are easily identified by type-checkers

``` shell
$ uv run ty check class.py

error[unresolved-reference]: Name `value` used when not defined
  --> class.py:12:9
   |
10 |     # first issue, not assigning to self.value parameter
11 |     def add(self, offset):
12 |         value += offset
   |         ^^^^^
13 |
14 |     def get(self) -> int:
   |
info: An attribute `value` is available: consider using `self.value`
info: rule `unresolved-reference` is enabled by default

error[invalid-return-type]: Function always implicitly returns `None`, which is not assignable to return type `int`
  --> class.py:14:22
   |
12 |         value += offset
13 |
14 |     def get(self) -> int:
   |                      ^^^
15 |         self.value
   |
info: Consider changing the return annotation to `-> None` or adding a `return` statement
info: rule `invalid-return-type` is enabled by default
```

- Static typing is a trade-off against python’s *duck-typing* paradigm
  - i.e. One implementation accepting any type that provides the
    appropriate interface (See [Item
    25](../../Chapter_04/Item_025/item_025.qmd) and [Item
    57](../../Chapter_07/Item_057/item_057.qmd))
  - Has the advantage that we can be broad in what objects are accepted
    - Downside is that it can be hard to properly handle narrowing an
      interface
- For example, if we write a mathematical function that we expect to
  work on any real number the following failure might be non-obvious to
  a consumer (See
  [real_number.py](./Examples/03_RealNumber/real_number.py))

``` python
def combine(func, values):
    assert (len(values)) > 0

    result = values[0]
    for next_value in values[1:]:
        result = func(result, next_value)

    return result


def add(x, y):
    return x + y


inputs = [1, 2, 3, 4j]  # complex number fulfills number interface, but not expected
result = combine(add, inputs)
assert result == 10, result  # Fails
```

    AssertionError: (6+4j)
    ---------------------------------------------------------------------------
    AssertionError                            Traceback (most recent call last)
    Cell In[3], line 17
         15 inputs = [1, 2, 3, 4j]  # complex number fulfills number interface, but not expected
         16 result = combine(add, inputs)
    ---> 17 assert result == 10, result  # Fails

    AssertionError: (6+4j)

- How do we properly restrict a function’s arguments without being
  sacrificing too much flexibility to be type generic?
  - `typing` provides support for generics (See
    [real_number_typed.py](./Examples/03_RealNumber/real_number_typed.py))
  - Other modules will typically also define types that support their
    interfaces
    - e.g. `collections.abc` provides type generic abstract collection
      types
  - `TypeVar` is used to define a name to represent a generic or
    parameterised type
    - Optionally accepts a positional list of acceptable types
    - e.g. for real numbers those types might be `int` and `float`

``` python
# real_number_typed.py
#
# Function operating on real numbers
# Demonstrates using generics for typing

from collections.abc import Callable
from typing import TypeVar

Value = TypeVar("Value")
Func = Callable[[Value, Value], Value]


def combine(func: Func[Value], values: list[Value]) -> Value:
    assert len(values) > 0

    result = values[0]
    for next_value in values[1:]:
        result = func(result, next_value)

    return result


Real = TypeVar("Real", int, float)


def add(x: Real, y: Real) -> Real:
    return x + y


inputs = [1, 2, 3, 4j]  # Includes a complex number so not a list[Real] type
result = combine(add, inputs)
assert result == 10
```

- Running `ty` above catches no errors, as `ty` tries to be generous in
  how it handles untyped variables
  - However running `mypy --strict`

``` shell
uv run mypy --strict real_number_typed.py

real_number_typed.py:31: error: Argument 1 to "combine" has incompatible type "Callable[[Real, Real], Real]"; expected "Callable[[complex, complex], complex]"  [arg-type]
Found 1 error in 1 file (checked 1 source file)
```

- Since Python 3.12 the preferred way to define generics is using the
  *type parameter list* syntax
- The above example becomes

``` python
%reset
from collections.abc import Callable

# Combine function  signature parameterised on `Value` type
def combine[Value](func: Callable[[Value, Value], Value], values: list[Value]) -> Value:
    assert len(values) > 0

    result = values[0]
    for next_value in values[1:]:
        result = func(result, next_value)

    return result

# Add parameterised on the `Real` type which must be an `int` or `float`
def add[Real: (int, float)](x: Real, y: Real) -> Real:
    return x + y


inputs = [1, 2, 3, 4j]  # Includes a complex number so not a list[Real] type
result = combine(add, inputs)
assert result == 10
```

- Running again through `mypy`

``` shell
$ uv run mypy --strict real_number_type_list.py

real_number_type_list.py:25: error: Argument 1 to "combine" has incompatible type "Callable[[Real, Real], Real]"; expected "Callable[[complex, complex], complex]"  [arg-type]
Found 1 error in 1 file (checked 1 source file)
```

- Type-checking can also handle unexpectedly receiving a `None` value
  (See [Item 32](../../Chapter_05/Item_032/item_032.qmd))
  - For example, where we might expect to receive an object instead (See
    [get_or_default.py](./Examples/04_GetOrDefault/get_or_default.py))

``` python
def get_or_default(value, default):
    if value is not None:
        return value  # bug
    return value


found = get_or_default(3, 5)
assert found == 3
print("Test 1 passed!")

found = get_or_default(None, 5)
assert found == 5, found
print("Test 2 passed!")
```

    Test 1 passed!

    AssertionError: None
    ---------------------------------------------------------------------------
    AssertionError                            Traceback (most recent call last)
    Cell In[4], line 12
          9 print("Test 1 passed!")
         11 found = get_or_default(None, 5)
    ---> 12 assert found == 5, found
         13 print("Test 2 passed!")

    AssertionError: None

- To support this we can use *union types*
  - Provide a list of types joined by the `|` (or) operator
    - The operator syntax was introduced in Python 3.10, prior you had
      to use the `Union` syntax explicitly

    - For unions with `None` explicitly there is also the `Optional`
      type

    - The following are all equivalent,

      ``` python
        from typing import Union, Optional

        optional_1: int | None = 0
        optional_2: Union[int, None] = 0
        optional_3: Optional[int] = 0
      ```
  - Can be used to indicate that a parameter or variable can come from a
    set of types
  - By combining union types with normal types we can do *null checking*
    (See
    [get_or_default_typed.py](./Examples/04_GetOrDefault/get_or_default_typed.py))
    - We accept a union type with a `None`
    - But then must return a non-`None` type

``` shell
$ uv run ty check get_or_default_typed.py

error[invalid-return-type]: Return type does not match returned value
 --> get_or_default_typed.py:6:56
  |
6 | def get_or_default(value: int | None, default: int) -> int:
  |                                                        --- Expected `int` because of return type
7 |     if value is not None:
8 |         return value  # type narrows to `int`
9 |     return value  # does not match signature since if of type `int | None`
  |            ^^^^^ expected `int`, found `None`
  |
info: rule `invalid-return-type` is enabled by default

Found 1 diagnostic
```

- The `typing` library is extensive and constantly evolving
  - The best way to keep up to date is by exploring the
    [docs](https://docs.python.org/3/library/typing.html)
- *However*, unlike Java, exceptions are not supporting by Python’s type
  checking ecosystem
  - Not considered part of the interface
  - Must be caught verified via testing
- Historically resolving forward-references has been problematic in
  python (See [Item 122](../Item_122/item_122.qmd) for a similar
  concept)
  - Occurs when a type annotation relies on a type that is not yet fully
    defined
  - Common when writing classes that have methods returning an instance
    of themselves
  - Or collaborating classes (See \[forward_references.py\])
- Consider the following code
  - Perfectly valid, runs without issue without type hints

``` python
class FirstClass:
    def __init__(self, value):
        self.value = value


class SecondClass:
    def __init__(self, value):
        self.value = value


second = SecondClass(5)
first = FirstClass(second)
print("No problems!")
```

    No problems!

- Now suppose that `FirstClass` accepts a `value` that is of type
  `SecondClass` we might type this as

``` python
# forward_references_annotated.py
#
# type annotated version
# breaks for python < 3.14 or without `from __future__ import annotations`

# if python version < 3.13
# from __future__ import annotations

class FirstClass:
    def __init__(self, value: FirstClass) -> None:
        self.value = value


class SecondClass:
    def __init__(self, value: int) -> None:
        self.value = value


second = SecondClass(5)
first = FirstClass(second)
print("No problems!")
```

- Type checking shouldn’t identify any errors
- But if we run the program in Python 3.13 or earlier it will likely
  fail

``` shell
$ uv run python3.12 forward_references_type_annotated.py

Traceback (most recent call last):
  File ".../EffectivePython/Chapter_14/Item_124/Examples/05_ForwardReferences/forward_references_type_annotated.py", line 7, in <module>
    class FirstClass:
  File ".../EffectivePython/Chapter_14/Item_124/Examples/05_ForwardReferences/forward_references_type_annotated.py", line 8, in FirstClass
    def __init__(self, value: SecondClass) -> None:
                              ^^^^^^^^^^^
NameError: name 'SecondClass' is not defined
```

- Occurs because types are evaluated when they are encountered

  - Which can before they are defined

- Since Python 3.14 this behaviour is changed and types can be forward
  referenced safely

- Prior to Python 3.14 there are two solutions

  1.  Use `from __future__ import annotations`
      - Uses an old style of resolving forward references proposed in
        [PEP 563](https://peps.python.org/pep-0563/)
        - Based on converting type annotations to strings
        - Resulted in runtime overhead
        - Issues were not resolved and it was instead replaced
        - Will eventually be deprecated and removed
      - The Python 3.14 solution is instead based off of [PEP
        649](https://peps.python.org/pep-0649/)
        - Uses an alternative form of lazy evaluation
      - Should require no syntactical change
  2.  Use quoted type annotations
      - Use string as the type annotation matching the type name of the
        forward reference
      - Supported by most tools

``` python
# forward_references_str_annotated.py
#
# str annotated versions
# Uses stringifyed type annotation to resolve forward reference
# Works for Python < 3.14


class FirstClass:
    def __init__(self, value: "SecondClass") -> None:
        self.value = value


class SecondClass:
    def __init__(self, value: int) -> None:
        self.value = value


second = SecondClass(5)
first = FirstClass(second)
print("No problems!")
```

- When and how should you use type hints?

  1.  Avoid using them to start

      - Lose the fast prototyping advantages of Python

      - Follow a strategy of

        1.  Prototype
        2.  Test
        3.  Type

  2.  Type hints are most important at boundaries

      - Function signatures within a code base
      - API boundaries to external callers
      - Complement
        - tests (See [Item 108](../../Chapter_13/Item_108/item_108.qmd))
        - warnings (see [Item 123](../Item_123/item_123.qmd))
      - Provide guidance to callers on how to use an API

  3.  Apply Type Hints to the most complex parts of a codebase

      - Provide assurance and stability to complicated error-prone code
      - Often overkill providing a fully-typed codebase

  4.  Include static analysis as part of automated testing and building

      - Ensures all commits are checked for common errors
      - Configuration should be consistent and source-controlled across
        a project

  5.  Run the type checker as type information is added

      - Easier to resolve type errors gradually rather than all at once

- When should you avoid type hints?

  - Small self-contained programs with obvious use patterns
  - Ad-hoc or testing code
    - E.g. interactive notebook sessions
  - Legacy codebases
    - Though this can be useful as part of a refactor / transition
  - Prototyping
    - Type hints may be overkill and overly constrain a system

## Things to Remember

- Python has special type annotation syntax supported by the `typing`
  built-in module
- Static type checkers utilise the type annotation system to identify
  common bugs before runtime
- Use best practices to support typed APIs that provide structure and
  clarity while still taking advantage of python’s rapid prototyping
  system
