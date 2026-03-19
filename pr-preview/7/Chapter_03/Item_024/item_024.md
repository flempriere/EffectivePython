# Item 24: Consider `itertools` for Working with Iterators and
Generators


- [Notes](#notes)
  - [Linking Iterators Together](#linking-iterators-together)
    - [`Chain`](#chain)
    - [`repeat`](#repeat)
    - [`cycle`](#cycle)
    - [`tee`](#tee)
    - [`zip_longest`](#zip_longest)
  - [Filtering Items from an
    Iterator](#filtering-items-from-an-iterator)
    - [`islice`](#islice)
    - [`takewhile`](#takewhile)
    - [`dropwhile`](#dropwhile)
    - [`filterfalse`](#filterfalse)
  - [Producing Combinations of Items from
    Iterators](#producing-combinations-of-items-from-iterators)
    - [`batched`](#batched)
    - [`pairwise`](#pairwise)
    - [`accumulate`](#accumulate)
    - [`product`](#product)
    - [`permutations`](#permutations)
    - [`combinations`](#combinations)
    - [`combinations_with_replacement`](#combinations_with_replacement)
- [Things to Remember](#things-to-remember)

## Notes

- `itertools` is a built-in module providing functions for advanced
  interactions with iterators
- When you need to perform complex iteration code first check the
  [itertools
  documentation](https://docs.python.org/3/library/itertools.html)

### Linking Iterators Together

#### `Chain`

- Combine multiple iterators into one sequential iterator
  - Iterators are processed in the order they are passed to `chain`

``` python
import itertools

it = itertools.chain([1, 2, 3], [4, 5, 6])
print(list[it])
```

    list[<itertools.chain object at 0x7f0cb660ca60>]

- An alternative version is `chain.from_iterable()`
  - Consumes an iterator of iterators
  - Produces a single flat output iterator

``` python
import itertools

it1 = [i * 3 for i in ("a", "b", "c")]
it2 = [i * 2 for i in ("x", "y", "z")]
nested = [it1, it2]
it = itertools.chain.from_iterable(nested)

print(list(it))
```

    ['aaa', 'bbb', 'ccc', 'xx', 'yy', 'zz']

#### `repeat`

- Use to repeat a single value a specified number of times or infinitely
  - By default, repeats infinitely, else provide the second argument

``` python
import itertools

it = itertools.repeat("hello", 3)
print(list(it))
```

    ['hello', 'hello', 'hello']

#### `cycle`

- Repeat an iterators items forever

``` python
import itertools

it = itertools.cycle([1, 2])

result = [next(it) for _ in range(10)]
print(result)
```

    [1, 2, 1, 2, 1, 2, 1, 2, 1, 2]

#### `tee`

- Split a single iterator into $n$ parallel iterators
  - Memory usage grows if iterators don’t progress at the same speed

``` python
import itertools

it1, it2, it3 = itertools.tee(["first", "second"], 3)

print(list(it1))
print(list(it2))
print(list(it3))
```

    ['first', 'second']
    ['first', 'second']
    ['first', 'second']

#### `zip_longest`

- `zip` variant that iterates until the longest iterator is exhausted
- Missing values are replaced with a user-specified default or `None`

``` python
import itertools

keys = ["one", "two", "three"]
values = [1, 2]

normal = list(zip(keys, values))
print("zip:     ", normal)

it = itertools.zip_longest(keys, values, fill_value="nope")
longest = list(it)
print("zip_longest: ", longest)
```

    zip:      [('one', 1), ('two', 2)]

    TypeError: zip_longest() got an unexpected keyword argument
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[6], line 9
          6 normal = list(zip(keys, values))
          7 print("zip:     ", normal)
    ----> 9 it = itertools.zip_longest(keys, values, fill_value="nope")
         10 longest = list(it)
         11 print("zip_longest: ", longest)

    TypeError: zip_longest() got an unexpected keyword argument

### Filtering Items from an Iterator

- Filter functions take an iterator and return a subset of the items

#### `islice`

- Slice an iterator by numerical indices without copying
- Three different call structures
  1.  Specify the end
  2.  Specify the start and end
  3.  Specify the start, end and step
- Similar logic to that of standard slicing and striding

``` python
import itertools

values = [i for i in range(1, 11)]

first_five = itertools.islice(values, 5)
print("First five: ", list(first_five))

middle_odds = itertools.islice(values, 2, 8, 2)
print("Middle odds:", list(middle_odds))
```

    First five:  [1, 2, 3, 4, 5]
    Middle odds: [3, 5, 7]

#### `takewhile`

- Returns items from an iterator until a predicate function returns
  `False`
  - All remaining items consumed (but not returned)

``` python
import itertools

values = [i for i in range(1, 11)]

less_than_seven = lambda x : x < 7
it = itertools.takewhile(less_than_seven, values)
print(list(it))
```

    [1, 2, 3, 4, 5, 6]

#### `dropwhile`

- Opposite of `dropwhile`
- Skips items from an iterator until a predicate returns `False`
  - All remaining items are returned

``` python
import itertools

values = [i for i in range(1, 11)]

less_than_seven = lambda x : x < 7
```

#### `filterfalse`

- Opposite of the built-in `filter` function
- Returns all items for which a predicate is `False`

``` python
import itertools

values = [i for i in range(1, 11)]
evens = lambda x : x % 2 == 0

filter_result = filter(evens, values)
print("Filter:      ", list(filter_results))

filter_false_result = itertools.filterfalse(evens, values)
print("Filter false:    ", list(filter_false_result))
```

    NameError: name 'filter_results' is not defined
    ---------------------------------------------------------------------------
    NameError                                 Traceback (most recent call last)
    Cell In[10], line 7
          4 evens = lambda x : x % 2 == 0
          6 filter_result = filter(evens, values)
    ----> 7 print("Filter:      ", list(filter_results))
          9 filter_false_result = itertools.filterfalse(evens, values)
         10 print("Filter false:    ", list(filter_false_result))

    NameError: name 'filter_results' is not defined

### Producing Combinations of Items from Iterators

- These produce combinations of items from iterators

#### `batched`

- Create an iterator of fixed size, non-overlapping groups of items from
  a single iterator
- Second argument is the batch size
- Useful when processing data together
  - E.g. for efficiency
  - Or constraint satisfaction

``` python
import itertools

it = itertools.batched([i for i in range(1, 11)], 3)
print(list(it))
```

    [(1, 2, 3), (4, 5, 6), (7, 8, 9), (10,)]

- You can see from above in the case that the iterator doesn’t evenly
  divide into batches the last batch may be smaller than the batch size

#### `pairwise`

- Iterate through each adjacent pair in the input iterator
- Adjacent generated pairs overlap, i.e. `[a, b, c]` generates
  `[(a, b), (b, c)]`
  - Every item except the ends appears twice
- Can be useful for graph-traversal algorithms that need to traverse
  sequential sets of vertices or endpoints

``` python
import itertools

route = ["Los Angeles", "Bakersfield", "Modesto", "Sacramento"]
it = itertools.pairwise(route)
print(list(it))
```

    [('Los Angeles', 'Bakersfield'), ('Bakersfield', 'Modesto'), ('Modesto', 'Sacramento')]

#### `accumulate`

- Fold items from an iterator into a running value
- Works by applying a two parameter function (first is the current
  value, second is the next item from the iterator)
- By default, sums the elements

``` python
import itertools

# basic example, defaults to sum
values = [i for i in range(1, 11)]
sum_reduce = itertools.accumulate(values)
print("Sum:     ", list(sum_reduce))

# advanced example, specifying our own function
def sum_modulo_20(first, second):
    output = first + second
    return output % 20

modulo_reduce = itertools.accumulate(values, sum_modulo_20)
print("Sum Modulo 20:   ", list(module_reduce))
```

    Sum:      [1, 3, 6, 10, 15, 21, 28, 36, 45, 55]

    NameError: name 'module_reduce' is not defined
    ---------------------------------------------------------------------------
    NameError                                 Traceback (most recent call last)
    Cell In[13], line 14
         11     return output % 20
         13 modulo_reduce = itertools.accumulate(values, sum_modulo_20)
    ---> 14 print("Sum Modulo 20:   ", list(module_reduce))

    NameError: name 'module_reduce' is not defined

- Effectively the same as the `functools` `reduce` function
  - But outputs are yielded one at a time

#### `product`

- Returns the cartesian product from one or more iterators
  - Optional `repeat` lets you calculate the product of an iterator with
    `repeat - 1` copies of itself
- Provides a good alternative to deeply nested comprehensions

``` python
import itertools

# product of A, with itself
single = itertools.product([1, 2], repeat=2)
print("Single:  ", list(single))

# product of two distinct lists
multiple = itertools.product([1, 2], ["a", "b", "c"])
print("Multiple:", list(multiple))
```

    Single:   [(1, 1), (1, 2), (2, 1), (2, 2)]
    Multiple: [(1, 'a'), (1, 'b'), (1, 'c'), (2, 'a'), (2, 'b'), (2, 'c')]

#### `permutations`

- Returns unique, ordered permutations of length $n$ from an iterator
  - $n$ is the second argument

``` python
import itertools

it = itertools.permutations([1, 2, 3, 4], 2)
print(list(it))
```

    [(1, 2), (1, 3), (1, 4), (2, 1), (2, 3), (2, 4), (3, 1), (3, 2), (3, 4), (4, 1), (4, 2), (4, 3)]

#### `combinations`

- Returns the unordered combinations of length $n$ from an iterator
  - Items are not repeated

``` python
import itertools

it = itertools.combinations([1, 2, 3, 4], 2)
print(list(it))
```

    [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]

#### `combinations_with_replacement`

- Same as `combinations` but replacements are allowed
- Compared to `permutations` the same value can be repeated in the same
  output group e.g. `(1,1)`

## Things to Remember

- `itertools` functions fall into three main categories
  1.  Linking iterators together
  2.  Filtering iterator outputs
  3.  Producing combinations from iterators
- There are more advanced functions and some of the functions specified
  have additional parameters
  - Refer to the documentation
- The official documentation demonstrates several useful recipes
