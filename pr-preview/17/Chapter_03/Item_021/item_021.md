# Item 21: Be Defensive when Iterating Over Arguments


- [Notes](#notes)
  - [Example: American Tourism
    Numbers](#example-american-tourism-numbers)
- [Things to Remember](#things-to-remember)

## Notes

- Often when a function accepts a list of values it wants to iterate
  over them
  - Sometimes multiple times

### Example: American Tourism Numbers

- Given a dataset of visitors to a city (in the millions)
- Calculate what percentage of overall tourism each city receives
- Have to normalise the dataset
  - First sum the dataset
  - Second divide through the dataset

``` python
def normalise(numbers):
    total = sum(numbers)
    result = []
    for value in numbers:
        percent = 100 * value / total
        result.append(percent)
    return result


visits = [15, 35, 80]
percentages = normalise(visits)
print(percentages)
assert sum(percentages) == 100.0
```

    [11.538461538461538, 26.923076923076923, 61.53846153846154]

- To scale this up use a generator from a file
  - However, returns an empty list!

``` python
import os


def normalise(numbers):
    total = sum(numbers)
    result = []
    for value in numbers:
        percent = 100 * value / total
        result.append(percent)
    return result


def read_visits(path):
    with open(path) as f:
        for line in f:
            yield int(line)


try:
    # generate some fake data
    visits = [15, 35, 80]
    path = "temp.txt"
    with open(path, "w") as f:
        f.writelines([f"{visit}\n" for visit in visits])

    # use the fake data
    it = read_visits(path)
    percentages = normalise(it)
    print(percentages)
except Exception as e:
    print(f"{type(e)}: {e}")
finally:
    if os.path.exists(path):
        os.remove(path)
```

    []

- Example above fails because an iterator only produces it’s results
  once
- Once it raises a `StopIteration` exception it won’t return anything
  further
  - Note, that a `StopIteration` is raised once
- Constructors that expect `StopIteration` can’t tell the difference
  between an iterator that returns nothing and an exhausted iterator

``` python
import os


def read_visits(path):
    with open(path) as f:
        for line in f:
            yield int(line)


try:
    # generate some fake data
    visits = [15, 35, 80]
    path = "temp.txt"
    with open(path, "w") as f:
        f.writelines([f"{visit}\n" for visit in visits])

    it = read_visits(path)
    print(list(it))  # generates a list
    print(list(it))  # already consumed
except Exception:
    pass
finally:
    if os.path.exists(path):
        os.remove(path)
```

    [15, 35, 80]
    []

- To get around the problem
  - Can explicitly exhaust a generator into a list
  - Has the downside that the generator’s content need to be read into
    memory
  - Doesn’t work for large or arbitrarily long generators

``` python
import os


def read_visits(path):
    with open(path) as f:
        for line in f:
            yield int(line)


def normalise_copy_into_list(numbers):
    numbers_copy = list(numbers)  # copy the iterator
    total = sum(numbers_copy)
    result = []
    for value in numbers_copy:
        percent = 100 * value / total
        result.append(percent)
    return result


try:
    # generate some fake data
    visits = [15, 35, 80]
    path = "temp.txt"
    with open(path, "w") as f:
        f.writelines([f"{visit}\n" for visit in visits])

    it = read_visits(path)
    percentages = normalise_copy_into_list(it)
    print(percentages)
    assert sum(percentages) == 100.0
except Exception:
    pass
finally:
    if os.path.exists(path):
        os.remove(path)
```

    [11.538461538461538, 26.923076923076923, 61.53846153846154]

- We wrote the generator approach to avoid having to load the entire
  dataset into memory in the first place!
- Alternative solution, accept a function that returns an iterator each
  time it’s called

``` python
import os


def read_visits(path):
    with open(path) as f:
        for line in f:
            yield int(line)


def normalise_receive_iterator(get_iter):
    total = sum(get_iter())
    result = []
    for value in get_iter():
        percent = 100 * value / total
        result.append(percent)
    return result


try:
    # generate some fake data
    visits = [15, 35, 80]
    path = "temp.txt"
    with open(path, "w") as f:
        f.writelines([f"{visit}\n" for visit in visits])

    percentages = normalise_receive_iterator(lambda: read_visits(path))
    print(percentages)
    assert sum(percentages) == 100.0
except Exception:
    pass
finally:
    if os.path.exists(path):
        os.remove(path)
```

    [11.538461538461538, 26.923076923076923, 61.53846153846154]

- This works, but it’s clumsy
  - We have to pass a lambda `lambda : read_visits(path)` to our
    normalise function
- Better solution to use a container that supports the *iterator*
  protocol
  - The protocol that `for` loops and related syntax use to traverse a
    container
  - `for x in foo:` is syntactic sugar for the `iter(foo)`
    - Returns the iterator to loop through
  - `iter` built-in calls the `foo.__iter__` dunder method
  - `__iter__` method must return an iterator object
    - Iterator object must support the `__next__` method
  - `for` loop repeatedly calls `__next__` built-in function on the
    iterator until its exhausted
    - Via the `StopIteration` exception
- The easy way to implement this is to implement `__iter__` as a method
  - See the sample implementation below

``` python
import os


class ReadVisits:
    def __init__(self, path):
        self.path = path

    def __iter__(self):
        with open(self.path) as f:
            for line in f:
                yield int(line)


def normalise(numbers):
    total = sum(numbers)
    result = []
    for value in numbers:
        percent = 100 * value / total
        result.append(percent)
    return result


try:
    # generate some fake data
    visits = [15, 35, 80]
    path = "temp.txt"
    with open(path, "w") as f:
        f.writelines([f"{visit}\n" for visit in visits])

    it = ReadVisits(path)
    percentages = normalise(it)
    print(percentages)
    assert sum(percentages) == 100.0
except Exception:
    pass
finally:
    if os.path.exists(path):
        os.remove(path)
```

    [11.538461538461538, 26.923076923076923, 61.53846153846154]

- We define a lightweight class that `yields` lines from the specified
  file
- We can then pass this to the original `normalise` implementation
  - The built-in `sum` function calls the `ReadVisits.__iter__` method
  - Creates a new iterator object
  - the normalisation `for` loop again calls `ReadVisits.__iter__`
    - Accesses a second iterator object
  - Each iterator advances and exhausts independently
- Downside of the above is that it reads the data twice
- We can invert the order of control so that the functions ensure the
  parameters aren’t just iterators
  - An iterator passed to `iter` must return the iterator itself
  - When a container is passed to `iter` a new iterator is returned
  - Provides a testable behaviour we can use to switch on

``` python
import os


def normalise_defensive(numbers):

    if iter(numbers) is numbers:
        raise TypeError("Must supply a container")
    total = sum(numbers)
    result = []
    for value in numbers:
        percent = 100 * value / total
        result.append(percent)
    return result


# works on a list
numbers_list = [15, 35, 80]
numbers_percentage = normalise_defensive(numbers_list)
assert sum(numbers_percentage) == 100.0
print("Successfully normalised numbers list")

# fails on an iterator
numbers_iter = iter(numbers_list)
normalise_defensive(numbers_iter)  # should raise an exception
```

    Successfully normalised numbers list

    TypeError: Must supply a container
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[7], line 24
         22 # fails on an iterator
         23 numbers_iter = iter(numbers_list)
    ---> 24 normalise_defensive(numbers_iter)  # should raise an exception

    Cell In[7], line 7, in normalise_defensive(numbers)
          4 def normalise_defensive(numbers):
          6     if iter(numbers) is numbers:
    ----> 7         raise TypeError("Must supply a container")
          8     total = sum(numbers)
          9     result = []

    TypeError: Must supply a container

- Alternatively can import the `Iterator` class from the abstract
  collections built-in module (`collections.abc`)

``` python
from collections.abc import Iterator


def normalise_defensive(numbers):

    if isinstance(numbers, Iterator):
        raise TypeError("Must supply a container")

    total = sum(numbers)
    result = []
    for value in numbers:
        percent = 100 * value / total
        result.append(percent)
    return result


# works on a list
numbers_list = [15, 35, 80]
numbers_percentage = normalise_defensive(numbers_list)
assert sum(numbers_percentage) == 100.0
print("Successfully normalised numbers list")


# works on our custom class
class ReadVisits:
    def __init__(self, path):
        self.path = path

    def __iter__(self):
        with open(self.path) as f:
            for line in f:
                yield int(line)


try:
    # generate some fake data
    path = "temp.txt"
    with open(path, "w") as f:
        f.writelines([f"{visit}\n" for visit in numbers_list])

    it = ReadVisits(path)
    percentages = normalise_defensive(it)
    print(percentages)
    assert sum(percentages) == 100.0
    assert percentages == numbers_percentages
    print("Successfully normalised ReadVisits object")
except Exception:
    pass
finally:
    if os.path.exists(path):
        os.remove(path)

# fails on an iterator
numbers_iter = iter(numbers_list)
normalise_defensive(numbers_iter)  # should raise an exception
```

    Successfully normalised numbers list
    [11.538461538461538, 26.923076923076923, 61.53846153846154]

    TypeError: Must supply a container
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[8], line 55
         53 # fails on an iterator
         54 numbers_iter = iter(numbers_list)
    ---> 55 normalise_defensive(numbers_iter)  # should raise an exception

    Cell In[8], line 7, in normalise_defensive(numbers)
          4 def normalise_defensive(numbers):
          6     if isinstance(numbers, Iterator):
    ----> 7         raise TypeError("Must supply a container")
          9     total = sum(numbers)
         10     result = []

    TypeError: Must supply a container

- Expecting a container works if you don’t want to copy the full
  iterator
  - Requires us to perform multiple iterations over the data though
- As you can see above, `normalise_defensive` accepts the built-in
  `list` and our user-defined `ReadVisits` class
  - In theory any other `Iterator` class
- Can also extend this approach to asynchronous iterators

## Things to Remember

- Beware of functions and methods that iterate over input arguments
  multiple times
  - If arguments are *iterators* you might see strange behaviour and
    missing values
- Python’s iterator protocol defines the `iter` and `next` built-ins
  - Defines how `for` loops and related constructs operate
- You can define your own iterable container via the `__iter__` dunder
  method
- You can detect that a value is an iterator
  - Calling `iter` on an iterator returns itself
  - Calling `iter` on a container returns a new iterator
  - Alternatively `containers.abc` supplies the `Iterator` class
    - You can test for it with `isinstance`
