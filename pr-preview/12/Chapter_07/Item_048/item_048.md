# Item 48: Accept Functions Instead of Classes for Simple Interfaces


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Many built-in API’s accept functions to customise behaviour
- These are sometimes called *hooks*
  - They call back to code while executing
- E.g. `list` has a `sort` method
  - Takes an optional `key` argument, determine’s each indices value for
    sorting
  - For example we might sort a list of names by their length

``` python
names = ["Socrates", "Archimedes", "Plato", "Aristotle"]
names.sort(key=len)
print(names)
```

    ['Plato', 'Socrates', 'Aristotle', 'Archimedes']

- Hooks don’t need to be classes or interfaces
- In python many are stateless functions
  - Just need to match the arguments and return values
- Functions are easier to implement than classes
  - Simpler to explain
  - Works because python supports *first class functions*
    - Means they can be treated like any other variable
- For example, we might want to customise a `defaultdict` (See [Item
  27](../../Chapter_04/Item_027/item_027.qmd))
  - Data structure accepts a function that
    1.  Takes no arguments
    2.  Is called each time a missing key is accessed
    3.  Must return the default value for a missing key
  - We might define a function that logs when a key is missing, and
    returns zero
    - Below demonstrates it’s use

``` python
from collections import defaultdict

current = {"green": 12, "blue": 3}
increments = [
    ("red", 5),
    ("blue", 17),
    ("orange", 9),
]


def log_missing():
    print("Key added")
    return 0


result = defaultdict(log_missing, current)
print("Before:", dict(result))
for key, amount in increments:
    result[key] += amount
print("After: ", dict(result))
```

    Before: {'green': 12, 'blue': 3}
    Key added
    Key added
    After:  {'green': 12, 'blue': 20, 'red': 5, 'orange': 9}

- API’s that accept functions help separate side effects from
  deterministic behaviour
- Could now make our hook for `defaultdict` could the total number of
  missing keys
  - Could use a closure which captures state (See [Item
    33](../../Chapter_05/Item_033/item_033.qmd))
  - Here we define a helper function to use the closure as the default
    value hook

``` python
from collections import defaultdict

current = {"green": 12, "blue": 3}
increments = [
    ("red", 5),
    ("blue", 17),
    ("orange", 9),
]


def increment_with_report(current, increments):
    added_count = 0

    def missing():
        nonlocal added_count  # Stateful closure
        added_count += 1
        return 0

    result = defaultdict(missing, current)
    for key, amount in increments:
        result[key] += amount

    return result, added_count


result, count = increment_with_report(current, increments)
assert count == 2
```

- Stateful closures are harder to read than a stateless function
  - Could instead encapsulate state in a class

``` python
from collections import defaultdict

current = {"green": 12, "blue": 3}
increments = [
    ("red", 5),
    ("blue", 17),
    ("orange", 9),
]


class CountMissing:
    def __init__(self):
        self.added = 0

    def missing(self):
        self.added += 1
        return 0


counter = CountMissing()
result = defaultdict(counter.missing, current)  # Method ref
for key, amount in increments:
    result[key] += amount
assert counter.added == 2
```

- Observe that since functions are first class we can pass the method
  `missing` to the `defaultdict` rather than the entire class
  - Since we can capture the state in a class, it typically makes it
    easy for the method to match the signature
- Helper classes are typically cleaner than the stateful closure
  approach
  - However, the purpose of the class is not clear, we have questions
    like,
    1.  Who constructs a `CountMissing` object?
    2.  Who calls the `missing` method?
    3.  How do we handle if the class needs change over time?
  - It’s usage is tied to `defaultdict` or in general the API it is
    being hooked into
- To clarify you can define a `__call__` method
  - Call let’s a class be *called* like a function
  - Also means class will register `True` to the built-in `callable`
    function
    - Such types are referred to as *Callables*

``` python
class BetterCountMissing:
    def __init__(self):
        self.added = 0

    def __call__(self):
        self.added += 1
        return 0


counter = BetterCountMissing()
assert counter() == 0
assert callable(counter)
```

- We can then use this class directly as the `defaultdict` hook

``` python
from collections import defaultdict

current = {"green": 12, "blue": 3}
increments = [
    ("red", 5),
    ("blue", 17),
    ("orange", 9),
]


class BetterCountMissing:
    def __init__(self):
        self.added = 0

    def __call__(self):
        self.added += 1
        return 0


counter = BetterCountMissing()
result = defaultdict(counter, current)  # Relies on __call__
for key, amount in increments:
    result[key] += amount
assert counter.added == 2
```

- By defining `__call__` we indicate the class with be used in a
  function-like way
  - e.g. API hooks
- The entry point `__call__` is the obvious site for the reader to start
  looking at the class
- `defaultdict` still only sees that it receives a callable
  - Does not care if the callable is a simple function or a
    function-like class
- As we’ve seen function-accepting interfaces are thus flexible in how
  they can be met
  1.  Simple stateless functions
  2.  Stateful closures
  3.  State-managed classes

## Things to Remember

- Instead of defining classes and instantiating them, functions can
  often be passed as hooks to simple interfaces
- References to functions and methods are first class in Python
  - They can be used in expressions
- `__call__` enables class instances to be called like plain Python
  functions
  - They then pass `callable` checks
- When a function needs to maintain state instead consider a class
  implementing `__call__`
