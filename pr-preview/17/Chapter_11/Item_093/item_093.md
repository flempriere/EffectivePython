# Item 93: Optimise Performance-Critical Code Using `timeit`
Micro-benchmarks


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Once a bottleneck has been identified via profiling (See [Item
  92](../Item_092/item_092.qmd)) other techniques can then be used to
  improve performance
  - Often a new data structure or architecture can then improve the
    performance
- Hot-spots may continue to remain even after rounds of refactoring
  - Rather than considering drastic solutions (See [Item
    94](../Item_094/item_094.qmd))
  - Consider *micro-benchmarks* via `timeit`
- `timeit` allows for accurate measurement of small code snippets
  - Allows for comparing different code solutions
  - Allows for narrow scoping of performance optimisation
- Use case is straight forward, e.g. to time the addition of two
  integers

``` python
import timeit

delay = timeit.timeit(stmt="1+2")
print(delay)
```

    0.01099376599995594

- `timeit.timeit` calculates the time to run one million iterations of
  the provided `stmt` argument
  - This number is adjustable

``` python
import timeit

delay = timeit.timeit(stmt="1+2", number=100)
print(delay)
```

    1.8020000425167382e-06

- The risk with smaller iteration numbers is that there is a risk that
  the computer’s noise will obfuscate the test results
  - Need to use a large number to ensure accuracy
  - `timeit` will also disable the garbage collector while running
    - Provides a more consistent result, but may not entirely match
      reality
- In general always provide `number` explicitly
  - Helps for conducting follow on statistics

``` python
import timeit

count = 1_000_000

delay = timeit.timeit(stmt="1+2", number=count)
print(f"{delay / count * 1e9:.2f} nanoseconds")
```

    11.08 nanoseconds

- Often there needs to be some surrounding scaffolding or test harness
  to support a benchmark, e.g.
  - Setting up a data structure
  - Warming a cache
- `timeit` provides a `setup` argument
  - Run’s once before all iterations
  - Excluded from final timing
- For example, measuring the time to find a number in a randomised list
  - Don’t want to include the time spent generating the list and
    randomising
  - Put this in a `setup` function

``` python
import timeit
import random

count = 100_000

delay = timeit.timeit(
    setup="""
numbers=list(range(10_000))
random.shuffle(numbers)
probe = 7_777
""",
    stmt="""
probe in numbers
""",
    globals=globals(),
    number=count,
)

print(f"{delay / count * 1e9:.2f} nanoseconds")
```

    5809.73 nanoseconds

- Once a baseline is established we can modify the approach and compare
  the behaviours
  - For example, instead of using a `list` we use a `set` to find our
    number

``` python
import timeit
import random

count = 100_000

delay = timeit.timeit(
    setup="""
numbers=set(range(10_000))
probe = 7_777
""",
    stmt="""
probe in numbers
""",
    globals=globals(),
    number=count,
)

print(f"{delay / count * 1e9:.2f} nanoseconds")
```

    34.00 nanoseconds

- We should see that checking for membership in a `set` over our `list`
  takes on the order of nanoseconds as opposed to microseconds
  - This is because a `set` gives constant time membership tests
  - `list` has a linear time membership test
- Often when microbenchmarking we’re attempting to time the kernel of a
  mathematical function
  - Common in tight loops
- For example, consider summing a list of numbers

``` python
import timeit


def loop_sum(items):
    total = 0
    for i in items:
        total += i
    return total


count = 1000

delay = timeit.timeit(
    setup="numbers = list(range(10_000))",
    stmt="loop_sum(numbers)",
    globals=globals(),
    number=count,
)

print(f"{delay / count * 1e9:.2f} nanoseconds")
```

    288644.74 nanoseconds

- Above measures how long each call to `loop_sum` takes
  - Meaningless as we are interested in the timing of the inner loop
  - Need to normalise by the number of inner loop iterations
    - In the above it’s hardcoded

``` python
import timeit


def loop_sum(items):
    total = 0
    for i in items:
        total += i
    return total


count = 1000

delay = timeit.timeit(
    setup="numbers = list(range(10_000))",
    stmt="loop_sum(numbers)",
    globals=globals(),
    number=count,
)

print(f"{delay / count / 10_000 * 1e9:.2f} nanoseconds")
```

    28.85 nanoseconds

- Can see the cost of the function now *per item*
- `timeit` can also be used as a command-line tool
- For example we might want to compare dictionary key lookup methods
  (See [Item 26](../../Chapter_04/Item_026/item_026.qmd))
  1.  Using the `in` operator

      ``` shell
       $ uv run python3.14 -m timeit \
       > --setup='my_dict = {"key":  123}' \
       > 'if "key" in my_dict: my_dict["key"]'
       10000000 loops, best of 5: 21.5 nsec per loop
      ```

  2.  Using the `get` method

      ``` shell
       $  uv run python 3.14 -m  timeit \
       > --setup='my_dict = {"key": 123}' \
       > 'if (value := my_dict.get("key")) is not None: value'
       10000000 loops, best of 5: 22.6 nsec per loop
      ```

  3.  Catching an exception

      ``` shell
       $ uv run python3.14 -m timeit \
       > --setup='my_dict = {"key": 123}' \
       > 'try: my_dict["key"]
       > except KeyError: pass'
       20000000 loops, best of 5: 12.2 nsec per loop
      ```
- The command line interface automatically determines the number of
  loops to run
  - Also repeats the result five times and takes the best
  - This accounts for system variance to give a best case lower bound
- From our result, we can see that for keys that are expected to exist
  in the dictionary
  - exception catching is the fastest
  - `in` is the slowest
  - Might not be intuitively obvious given the extra machinery to set up
    exceptions
- Note, this hasn’t timed the impact of looking for keys that *don’t*
  exist which might differ

## Things to Remember

- `timeit` is a built-in module for micro-benchmarking short python
  statements
  - Good for optimising performance critical hot code
- Use the `setup` argument to make micro-benchmarks robust
  - Allows for defining code that is run *once* before all iterations
  - This function’s execution time is ignored
- Normalise micro-benchmark results to make them robust and comparable
- `timeit` can be run as a command-line utility via the python `-m` flag
