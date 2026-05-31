# Item 102: Consider Searching Sorted Sequences with `bisect`

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Searching an already sorted list of data is a common task, e.g.
  - Searching a dictionary for a word
  - Looking through a list of financial transactions
- Using the `index` method to search for a value takes linear time
  - Designed for arbitrarily organised data

``` python
data = list(range(10**5))
index = data.index(91234)
assert index == 91234
print("Found item!")
```

    Found item!

- If we have a sorted list and want to check if it contains a value we
  can search until we reach an upper bound or lower bound
  - Depending on the order of the search
  - The below computes the index of the smallest value greater than or
    equal to the given goal
  - Still linear though

``` python
data = list(range(10**5))


def find_closest(sequence, goal):
    for index, value in enumerate(sequence):
        if goal < value:
            return index
    raise ValueError(f"{goal} is out of bounds")


index = find_closest(data, 91234.56)
assert index == 91235
print("Found an upper bound")
```

    Found an upper bound

- The built-in `bisect` module provides binary-search style methods for
  searching through ordered lists
  - `bisect_left` returns an index such that,
    - If the item exists, the item is already there
    - If the item doesn’t, this is where the item should be inserted to
      maintain sorted order (relative to the list start)

``` python
from bisect import bisect_left

data = list(range(10**5))

index = bisect_left(data, 91234)  # Exact match
assert index == 91234
print("Found exact match")

index = bisect_left(data, 91234.56)  # Closest match
assert index == 91235
print("Found insertion point")
```

    Found exact match
    Found insertion point

- Binary search has logarithmic complexity
  - Scales much better as list size grows
- We can compare `bisect_left` vs `index` via `timeit` (See [Item
  93](../../Chapter_11/Item_093/item_093.qmd))

``` python
from bisect import bisect_left
import random
import timeit

size = 10**5
iterations = 1000

data = list(range(size))
to_lookup = [random.randint(0, size - 1) for _ in range(iterations)]


def run_linear(data, to_lookup):
    for index in to_lookup:
        data.index(index)


def run_bisect(data, to_lookup):
    for index in to_lookup:
        bisect_left(data, index)


baseline = (
    timeit.timeit(stmt="run_linear(data, to_lookup)", globals=globals(), number=10) / 10
)
print(f"Linear search takes {baseline:.6f}s")

comparison = (
    timeit.timeit(stmt="run_bisect(data, to_lookup)", globals=globals(), number=10) / 10
)
print(f"Bisect search takes {comparison:.6f}s")

slowdown = 1 + ((baseline - comparison) / comparison)
print(f"{slowdown:.1f}x slower")
```

    Linear search takes 0.520559s
    Bisect search takes 0.000342s
    1521.4x slower

- `bisect` works on any sequence type (See [Item
  57](../../Chapter_07/Item_057/item_057.qmd))
  - As long as the underlying elements support a natural ordering (See
    [Item 104](../Item_104/item_104.qmd))
- `bisect` also provides additional functionality (e.g. `bisect_right`)
  - As per usual, [read the
    docs](https://docs.python.org/3/library/bisect.html)

## Things to Remember

- Using index to search a list for a value takes linear time
  - But can work on unsorted data
- The `bisect` uses binary-search algorithms to provide fast
  range-queries for values in a sorted list
  - Can also work on generic sequence types
