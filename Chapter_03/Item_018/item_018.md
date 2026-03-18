# Item 18: Use `zip` to Process Iterators in Parallel


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- It is common to end up with lists or sequences of related objects
  - For example, list comprehensions allow us to derive a new list from
    a source list via an expression
  - Below, we take a list of names and convert it to a list of name
    lengths

``` python
names = ["Alice", "Bob", "Charlie"]
counts = [len(n) for n in names]
print(counts)
```

    [5, 3, 7]

- This technique leads to a concept called *parallel arrays*
  - Here the items in the *same* index in each list are related
  - e.g. the length of the $i$-th name, is the $i$-th value in `counts`
- If we wanted to iterate over both bits of data at the same time the
  naive approach would be to use `enumerate` or `range` to perform an
  index-based lookup
  - e.g. to find the longest name

``` python
names = ["Alice", "Bob", "Charlie"]
counts = [len(n) for n in names]

# Range-based loop
longest_name = None
max_count = 0

for i in range(len(names)):
    count = counts[i]
    if count > max_count:
        longest_name = names[i]
        max_count = count

print(f"Longest name (range-based loop): {longest_name}")

longest_name = None
max_count = 0

for i, name in enumerate(names):
    count = counts[i]
    if count > max_count:
        longest_name = name
        max_count = count

print(f"Longest name (enumerate-based approach): {longest_name}")
```

    Longest name (range-based loop): Charlie
    Longest name (enumerate-based approach): Charlie

- The `enumerate` method is cleaner
  - Don’t need to index into the `names` list
- In someway though it breaks the symmetry
  - We have to index `counts` but *not* `names`
- Doesn’t save any lines of code
- Instead we should use the `zip` operator
  - `zip` wraps multiple iterators in a lazy generator
  - Yields tuples containing the *next* element from *each* iterator
  - Can unpack them as for `enumerate`

``` python
names = ["Alice", "Bob", "Charlie"]
counts = [len(n) for n in names]

longest_name = None
counts = 0

for name, count in zip(names, counts):
    if count > max_count:
        longest_name = name
        max_count = count
```

    TypeError: 'int' object is not iterable
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[3], line 7
          4 longest_name = None
          5 counts = 0
    ----> 7 for name, count in zip(names, counts):
          8     if count > max_count:
          9         longest_name = name

    TypeError: 'int' object is not iterable

- `zip` consumes elements one at a time from each iterator
- Provides memory efficient access to long generators
  - Or infinite generators
- `zip` stops yielding when *any* of the wrapped iterators are exhausted
  - Means that if iterators of different size are combined the shortest
    determines the length of the loop

``` python
names = ["Alice", "Bob", "Charlie"]
counts = [len(n) for n in names]

names.append("Danielle")

for name, count in zip(names, counts):
    print(f"{name}: {count}")
```

    Alice: 5
    Bob: 3
    Charlie: 7

- Since Python 3.10, `zip` supports the `strict` keyword argument
  - If `False` default behaviour is assumed
  - If `True` a `ValueError` is raised if `zip` exhausts one of the
    iterators

``` python
names = ["Alice", "Bob", "Charlie"]
counts = [len(n) for n in names]

names.append("Danielle")

for name, count in zip(names, counts, strict=True):
    print(f" {name}: {count}")
```

     Alice: 5
     Bob: 3
     Charlie: 7

    ValueError: zip() argument 2 is shorter than argument 1
    ---------------------------------------------------------------------------
    ValueError                                Traceback (most recent call last)
    Cell In[5], line 6
          2 counts = [len(n) for n in names]
          4 names.append("Danielle")
    ----> 6 for name, count in zip(names, counts, strict=True):
          7     print(f" {name}: {count}")

    ValueError: zip() argument 2 is shorter than argument 1

- `strict` is designed for providing a run time check that the iterators
  are of the same length
  - It’s not designed to allow you to continue to iterate until all
    iterators are exhausted
- If you want to continue until the *end* of the *longest* iterator, use
  `zip_longest` from the `itertools` built-in module
  - Let’s you pad exhausted iterators with a default value (by default
    this is `None`)

``` python
import itertools

names = ["Alice", "Bob", "Charlie"]
counts = [len(n) for n in names]

names.append("Danielle")

for name, count in itertools.zip_longest(names, counts, fillvalue="Missing"):
    print(f" {name}: {count}")
```

     Alice: 5
     Bob: 3
     Charlie: 7
     Danielle: Missing

## Things to Remember

- `zip` is a built-in function for iterating over multiple iterators in
  parallel
- `zip` creates a lazy generator returning tuples
  - One element from each wrapped iterator is returned in each tuple
  - As a lazy generator arbitrary large generators can be used
- `zip` silently truncates the length of the shortest wrapped iterator
- The `strict` keyword is introduced in python 3.10
  - Rather than silently truncating mismatched iterator lengths will
    raise a `ValueError`
