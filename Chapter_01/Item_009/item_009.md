# Item 9: Consider `match` for Destructuring in Flow Control; Avoid When

`if` Statements are Sufficient

- [Notes](#notes)
  - [`match` is for Destructuring](#match-is-for-destructuring)
  - [Semi-structured Data vs Encapsulated
    Data](#semi-structured-data-vs-encapsulated-data)
- [Things to Remember](#things-to-remember)

## Notes

- `match` was introduced in Python 3.10
- `match` has it’s own mini-language embedded in python
- `match` appears to provide `switch`-like capabilities
  - e.g. The `if` statement based construct below,

``` python
def take_action(light):
    if light == "red":
        print("Stop")
    elif light == "yellow":
        print("Slow")
    elif light == "green":
        print("Go")
    else:
        raise RuntimeError

take_action("red")
take_action("yellow")
take_action("green")
```

    Stop
    Slow
    Go

- We can convert this a `match` structure by adding `case` clauses

``` python
def take_match_action(light):
    match light:
        case "red":
            print("Stop")
        case "yellow":
            print("Slow")
        case "green":
            print("Go")
        case _:
            raise RuntimeError


take_match_action("red")
take_match_action("yellow")
take_match_action("green")
```

    Stop
    Slow
    Go

- `match` looks cleaner
  - Only one reference now to the variable `light`
  - No need for the `==`
- Issue is that we’re using string literals
  - Effectively makes them magic constants
  - Prefer instead to use module level constants

``` python
# module level constants
RED = "red"
YELLOW = "yellow"
GREEN = "green"


def take_constant_action(light):
    match light:
        case RED:
            print("Stop")
        case YELLOW:
            print("Slow")
        case GREEN:
            print("Go")


take_constant_action("red")
take_constant_action("yellow")
take_constant_action("green")
```

    SyntaxError: name capture 'RED' makes remaining patterns unreachable (393847243.py, line 9)
      Cell In[3], line 9
        case RED:
             ^
    SyntaxError: name capture 'RED' makes remaining patterns unreachable

- This generates a confusing error
- This is because `match` is for structural matching
  - simple variable names are *capture patterns*
- If we have the same `match` above, but with only the `RED` branch and
  pass `GREEN`:

``` xpcwrexe:
def truncated_action(light):
    match light:
        case RED:
            print(f"{RED=}, {light=}: Stop")


truncated_action(GREEN)
```

- Naively we would expect this to resolve to `case "red" != "green"`
- However, the first case *is* executed
  - We can see from the debug output above `RED` was reassigned the
    value of `light`, here `GREEN`
- `match` is best thought of as analogous to variable unpacking
  - Tries to match the structure of the received argument

  - Python here is checking that the multiple assignment below, executes
    without error

    ``` python
      (RED, ) = (light, )
    ```

  - We could write this in longform

``` python
def take_unpacking_action(light):
    try:
        (RED,) = (light,)
    except TypeError:
        # did not match
        raise RuntimeError
    else:
        # Matched
        print(f"{RED=}, {light=}")


take_unpacking_action(GREEN)
```

    RED='green', light='green'

- This explains why we couldn’t have our switch like style work
  - The `YELLOW` and `GREEN` cases have the same structure as the
    initial `RED`
  - Python determines that these cases are thus unreachable and throws a
    syntax error

  ``` python
    def match_light(light):
        match light:
            case RED:
                ...
            case YELLOW:
                ...
            case GREEN:
                ...
  ```

- A workaround is to ensure the case label has a `.` operator
  - Causes python to do an attribute look up
  - This means to emulate standard switch behaviour we can use an `Enum`

``` python
import enum


class ColourEnum(enum.StrEnum):
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"


def take_enum_action(light):
    match light:
        case ColourEnum.RED:
            print("Stop")
        case ColourEnum.YELLOW:
            print("Slow")
        case ColourEnum.GREEN:
            print("Go")
        case _:
            raise RuntimeError


take_enum_action("red")
take_enum_action("yellow")
take_enum_action("green")
```

    Stop
    Slow
    Go

- The code works as expected
- But we’ve had to add a whole load of boilerplate to get it to work as
  intended

### `match` is for Destructuring

- *Destructuring* means extracting components from a complex nested data
  structure
- multiple assignment and tuple unpacking is an example of
  destructuring, e.g.

``` python
for index, value in enumerate("abc"):
    print(f"Index is {index} and value is {value}")
```

    Index is 0 and value is a
    Index is 1 and value is b
    Index is 2 and value is c

- We’ve seen that unpacking for lists and tuples can be used on deeply
  nested constructs too
  - `match` emulates this for dictionaries, sets and user-defined
    classes
  - This is restricted purely to determining control flow
- *Structural pattern matching* is useful for dealing with heterogeneous
  objects
  - Or *semi-structured data*
  - Similar concepts are *algebraic data types*, *sum types*, *tagged
    unions*
- Let’s look at using structural matching to help us search for a value
  in a binary tree
  - Tree is represented as a 3-tuple, indexed as,
    1. The stored value
    2. Left child (lower-valued)
    3. Right child (higher-valued)
  - We use `None` to represent a missing child
  - A leaf node is represented by an inlined value rather than
    `(value, None, None)`
  - A nested tree containing $7, 9, 10, 11, 13$ might then be defined as

``` python
my_tree = (10, (7, None, 9), (13, 11, None))
```

- A recursive search using the `if...elif...else` can be written as
  below

``` python
def contains(tree, value):
    if not isinstance(tree, tuple):
        return tree == value

    pivot, left, right = tree

    if value < pivot:
        return contains(left, value)
    elif value > pivot:
        return contains(right, value)
    else:
        return value == pivot

assert contains(my_tree, 9)
assert not contains(my_tree, 14)
```

- We could instead implement this using `match`

``` python
my_tree = (10, (7, None, 9), (13, 11, None))


def contains_match(tree, value):

    match tree:
        case pivot, left, _ if value < pivot:
            return contains_match(left, value)
        case pivot, _, right if value > pivot:
            return contains_match(right, value)
        case (pivot, _, _) | pivot:
            return pivot == value


assert contains_match(my_tree, 9)
assert not contains_match(my_tree, 14)
```

- Eliminates the call to `isinstance` relies on the implicit unpacking
- Code structure is regularised
- Logic is more compact and inline
- How does this work?
  - Each clause tries to extract the contents of `tree` to the given
    pattern
  - If the structure matches, must then pass any subsequent `if`
    statements
    - `if` clauses are sometimes called *guard expressions*
    - Statements in the case block are only evaluated if the guard
      expression is `True`
  - If the statement fails to match, we fall through to the next case
  - The pipe operator `|` is used to combine patterns
    - Means that either pattern must match
    - The second capture pattern is simple variable assignment so will
      catch anything
      - Used to capture leaf nodes
- Now suppose we want to use class structure to capture our nodes

``` python
class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right
```

- Recreating our tree
  - leaf nodes still specified by a simple value

``` python
obj_tree = Node(value=10, left=Node(value=7, right=9), right=Node(value=13, left=11))
```

- The `if` statement construction is straightforward to update

``` python
def contains_class(tree, value):
    if not isinstance(tree, Node):
        return tree == value
    elif value < tree.value:
        return contains_class(tree.left, value)
    elif value > tree.value:
        return contains_class(tree.right, value)
    else:
        return tree.value == value


assert contains_class(obj_tree, 9)
assert not contains_class(obj_tree, 14)
```

- Pretty similar to the original
  - We trade the namespace resolution of `tree.` for not having to do
    the tuple unpacking
- The `match` version can also be updated

``` python
def contains_match_class(tree, value):
    match tree:
        case Node(value=pivot, left=left) if value < pivot:
            return contains_match_class(left, value)
        case Node(value=pivot, right=right) if value > pivot:
            return contains_match_class(right, value)
        case Node(value=pivot) | pivot:
            return pivot == value


assert contains_match_class(obj_tree, 9)
assert not contains_match_class(obj_tree, 14)
```

- Each clause implicitly does an `isinstance` check
  - Test’s if `tree` is a `Node` object
  - Then extracts the object attributes into the capture pattern
  - Can use the captured variables in the guard clauses and case blocks

### Semi-structured Data vs Encapsulated Data

- `match` also useful when serialisation of data and interpretation are
  decoupled
- e.g. Deserializing a JSON object
  - The Deserialized object is a nested structure of
    1. Dictionaries
    2. Lists
    3. Strings
    4. Numbers
- Responsibilities are not clearly encapsulated like with a class
  hierarchy
- The nesting structure gives the semantic meaning for a program
- For example, billing software looking to deserialize JSON customer
  records
  - Some customers might be individuals
  - Some might be businesses

``` python
record_person = """{"customer": {"last": "Ross", "first": "Bob"}}"""
record_business = """{"customer": {"entity": "Steve's Painting Co."}}"""
```

- Naturally we want to convert these into proper python objects
  - Easier to integrate into data processes
  - UI widgets
  - etc.

``` python
from dataclasses import dataclass

@dataclass
class PersonCustomer:
    first_name: str
    last_name: str

@dataclass
class BusinessCustomer:
    company_name: str
```

- We can use `match` to convert the JSON data to the appropriate class
  structure

``` python
import json


def deserialize(data):
    record = json.loads(data)
    match record:
        case {"customer": {"last": last_name, "first": first_name}}:
            return PersonCustomer(first_name, last_name)
        case {"customer": {"entity": company_name}}:
            return BusinessCustomer(company_name)
        case _:
            raise ValueError("Unknown record type")


print("Record for a person: ", deserialize(record_person))
print("Record for a business: ", deserialize(record_business))
```

    Record for a person:  PersonCustomer(first_name='Bob', last_name='Ross')
    Record for a business:  BusinessCustomer(company_name="Steve's Painting Co.")

- `match` supports a bunch of other forms of matching
  1. set patterns
  2. `as` patterns
  3. Positional constructor patterns (with `__match_args__`
      customisation)
  4. Exhaustiveness checking with type annotations
  5. and more…
- Refer to the official [tutorial](https://peps.python.org/pep-0636/)

## Things to Remember

- `match` statements can replace simple `if` statements but doing so is
  error prone
  - Structural nature of capture patterns in `case` clauses is
    unintuitive
- `match` statements give an way to combine `isinstance` checks and
  destructuring to manage control flow
  - Useful for processing heterogeneous data
  - Interpreting semantic meaning of semi-structured data
- `case`patterns can be used with built-in data structures and
  user-defined classes
  - Each type has unique semantics that aren’t immediately obvious
