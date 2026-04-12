# Item 31: Return Dedicated Result Objects instead of Requiring Function
Callers to Unpack more than Three Variables


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Unpacking lets Python functions emulate multiple return values
- E.g. consider a function that returns the statistical summary of a
  dataset
  - Here just the minimum and maximum values encountered

``` python
def get_stats(numbers):
    minimum = min(numbers)
    maximum = max(numbers)

    return minimum, maximum

lengths = [63, 73, 72, 60, 67, 66, 71, 61, 72, 70]

minimum, maximum = get_stats(lengths) # Two return values

print(f"Min: {minimum}, Max: {maximum}")
```

    Min: 60, Max: 73

- Technically the multiple values are returned as *one* tuple
  - The tuple is then unpacked into the separate variable names

``` python
first, second = 1, 2

assert first == 1
assert second == 2


def my_function():
    return 1, 2


first, second = my_function()
assert first == 1
assert second == 2
```

- We can use catch-all unpacking even with function returns (See [Item
  16](../../Chapter_02/Item_016/item_016.qmd))
  - E.g. Say we have a function that computes the ordered ratio of the
    size of values in a list to the average of that list

``` python
def get_avg_ratio(numbers):
    average = sum(numbers) / len(numbers)
    scaled = [x / average for x in numbers]
    scaled.sort(reverse=True)
    return scaled


lengths = [63, 73, 72, 60, 67, 66, 71, 61, 72, 70]

longest, *middle, shortest = get_avg_ratio(lengths)

print(f"Longest: {longest:4.0%}")
print(f"Shortest: {shortest:4.0%}")
```

    Longest: 108%
    Shortest:  89%

- Now suppose the requirements change again
  - Want a full set of statistics, including mean and median lengths,
    and total population size
- We could stick with the unpacking approach,

``` python
def get_median(numbers):
    count = len(numbers)
    sorted_numbers = sorted(numbers)
    middle = count // 2  # floored division
    if count % 2 == 0:
        lower = sorted_numbers[middle - 1]
        upper = sorted_numbers[middle]
        median = (lower + upper) / 2
    else:
        median = sorted_numbers[middle]
    return median


def get_stats_more(numbers):
    minimum = min(numbers)
    maximum = max(numbers)
    count = len(numbers)
    average = sum(numbers) / count
    median = get_median(numbers)
    return minimum, maximum, average, median, count


lengths = [63, 73, 72, 60, 67, 66, 71, 61, 72, 70]

minimum, maximum, average, median, count = get_stats_more(lengths)

print(f"Min: {minimum}, Max: {maximum}")
print(f"Average: {average}, Median: {median}, Count: {count}")
```

    Min: 60, Max: 73
    Average: 67.5, Median: 68.5, Count: 10

- The approach is problematic
  1.  All the return values are numeric
      - Thus easy to accidentally reorder them
      - This is hard to spot
  2.  The unpacking line is long and likely to get wrapped
      - Wrapping generally hurts readability even when following PEP8
        (See [Item 2](../../Chapter_01/Item_002/item_002.qmd))
- As a general rule of them, never use more than three variables when
  unpacking return values
  - E.g. by using a catch-all
- If you need to unpack more values, instead prefer defining a
  lightweight class
  - Return an instance of that class

``` python
from dataclasses import dataclass


@dataclass
class Stats:
    minimum: float
    maximum: float
    average: float
    median: float
    count: int


def get_median(numbers):
    count = len(numbers)
    sorted_numbers = sorted(numbers)
    middle = count // 2  # floored division
    if count % 2 == 0:
        lower = sorted_numbers[middle - 1]
        upper = sorted_numbers[middle]
        median = (lower + upper) / 2
    else:
        median = sorted_numbers[middle]
    return median


def get_stats_obj(numbers):
    return Stats(
        minimum=min(numbers),
        maximum=max(numbers),
        count=len(numbers),
        average=sum(numbers) / len(numbers),
        median=get_median(numbers),
    )


lengths = [63, 73, 72, 60, 67, 66, 71, 61, 72, 70]
result = get_stats_obj(lengths)
print(result)
```

    Stats(minimum=60, maximum=73, average=67.5, median=68.5, count=10)

- The code is clearer, cleaner and easier to refactor down the line

## Things to Remember

- Functions can return multiple values via tuple-unpacking
- Multiple return values from a function can also be unpacked using
  catch-all starred expressions
- Unpacking into four or more variables is error prone and should be
  avoided
  - Instead define a lightweight results class and return an instance of
    that class
