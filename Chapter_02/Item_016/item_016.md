# Item 16: Prefer Catch-All Unpacking over Slicing

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- A limitation of basic unpacking is that you must know the length of
  the sequence being unpacked
  - For example, lets say we want to extract the two oldest car’s from a
    list
  - Below fails because it expects two items but encounters more than
    two

``` python
car_ages = [0, 9, 4, 8, 7, 20, 19, 1, 6, 15]
car_ages_descending = sorted(car_ages, reverse=True)
oldest, second_oldest = car_ages_descending
```

    ValueError: too many values to unpack (expected 2, got 10)
    ---------------------------------------------------------------------------
    ValueError                                Traceback (most recent call last)
    Cell In[1], line 3
          1 car_ages = [0, 9, 4, 8, 7, 20, 19, 1, 6, 15]
          2 car_ages_descending = sorted(car_ages, reverse=True)
    ----> 3 oldest, second_oldest = car_ages_descending

    ValueError: too many values to unpack (expected 2, got 10)

- It seems natural to attempt to resolve the above with indices and
  slicing (see [Item 14](../Item_014/item_014.qmd))

``` python
car_ages = [0, 9, 4, 8, 7, 20, 19, 1, 6, 15]
car_ages_descending = sorted(car_ages, reverse=True)
oldest = car_ages_descending[0]
second_oldest = car_ages_descending[1]
others = car_ages_descending[2:]
print(f"oldest: {oldest}, second oldest: {second_oldest}, others: {others}")
```

    oldest: 20, second oldest: 19, others: [15, 9, 8, 7, 6, 4, 1, 0]

- Works but is noisy
  - Would be nice to have the clean syntax of the unpacking
- Also prone to off-by-one errors
  - If we modify the size of one set, we have to make sure the other
    subsets are synchronised
- Python provides *catch-all* unpacking via the `*` operator
  - Let’s part of an unpacking expression receive all other values that
    aren’t matched

``` python
car_ages = [0, 9, 4, 8, 7, 20, 19, 1, 6, 15]
car_ages_descending = sorted(car_ages, reverse=True)
oldest, second_oldest, *others = car_ages_descending
print(f"oldest: {oldest}, second oldest: {second_oldest}, others: {others}")
```

    oldest: 20, second oldest: 19, others: [15, 9, 8, 7, 6, 4, 1, 0]

- Code is shorter, easier to read and less brittle to changes
- Starred expression can appear at any point in an unpacking
  - Start, end, middle etc.
  - Benefits any time we have one optional slice
  - E.g. if we instead wanted to extract the oldest and the youngest car

``` python
car_ages = [0, 9, 4, 8, 7, 20, 19, 1, 6, 15]
car_ages_descending = sorted(car_ages, reverse=True)
oldest, *others, youngest = car_ages_descending

print(f"oldest: {oldest}, youngest: {youngest}, others: {others}")
```

    oldest: 20, youngest: 0, others: [19, 15, 9, 8, 7, 6, 4, 1]

- Whenever you use a star expression, you must have at least one
  required match,
  - e.g. Below generates a syntax error

``` python
car_ages = [0, 9, 4, 8, 7, 20, 19, 1, 6, 15]
car_ages_descending = sorted(car_ages, reverse=True)
*others = car_ages_descending
```

    SyntaxError: starred assignment target must be in a list or tuple (1007003615.py, line 3)
      Cell In[5], line 3
        *others = car_ages_descending
        ^
    SyntaxError: starred assignment target must be in a list or tuple

- You can only use *one* catch-all expression in an unpacking at the
  same level
  - e.g. Below fails too

``` python
first, *middle, *second_middle, last = [1,2,3,4]
```

    SyntaxError: multiple starred expressions in assignment (1671393997.py, line 1)
      Cell In[6], line 1
        first, *middle, *second_middle, last = [1,2,3,4]
        ^
    SyntaxError: multiple starred expressions in assignment

- You can use multiple catch-all’s for different levels in a nested
  structure
  - Generally try to avoid this
  - It can make things hard to read

``` python
car_inventory = {
    "Downtown": ("Silver Shadow", "Pinto", "DMC"),
    "Airport" : ("Skyline", "Viper", "Gremlin", "Nova"),
}

((loc1, (best1, *rest1)),
 (loc2, (best2, *rest2))) = car_inventory.items()

print(f"Best at {loc1} is {best1}, others are {rest1}")
print(f"Best at {loc2} is {best2}, others are {rest2}")
```

    Best at Downtown is Silver Shadow, others are ['Pinto', 'DMC']
    Best at Airport is Skyline, others are ['Viper', 'Gremlin', 'Nova']

- Starred expressions always become lists
- If there is nothing left to unpack then the list is empty
  - Very useful when working with lists of at least $N$ elements

``` python
short_list = [1, 2]
first, second, *rest = short_list

print(f"First: {first}, Second: {second}, Rest: {rest}")
```

    First: 1, Second: 2, Rest: []

- You can unpack arbitrary iterators
  - Typically not very useful with basic multiple assignment
  - Here we unpack values iterating over a range
  - In this case probably more useful to assign to a list matching the
    unpacking pattern

``` python
it = iter(range(1, 3))
first, second = it
print(f"{first} and {second}")
```

    1 and 2

- Much more useful when we have starred expressions
- E.g. iterating over CSV data
  - Iterator yields rows from the CSV (+ the header)

We could process this using indices and slices

``` python
def generate_csv():
    yield ("Date", "Make", "Model", "Year", "Price")
    for i in range(100):
        yield ("2019-03-25", "Honda", "Fit", "2010", "$3400")
        yield ("2019-03-26", "Ford", "F150", "2008", "$2400")

all_csv_rows = list(generate_csv())
header = all_csv_rows[0]
rows = all_csv_rows[1:]
print("CSV header:", header)
print("Row count:", len(rows))
```

    CSV header: ('Date', 'Make', 'Model', 'Year', 'Price')
    Row count: 200

- But we can also easily unpack using a starred expression

``` python
def generate_csv():
    yield ("Date", "Make", "Model", "Year", "Price")
    for i in range(100):
        yield ("2019-03-25", "Honda", "Fit", "2010", "$3400")
        yield ("2019-03-26", "Ford", "F150", "2008", "$2400")


it = generate_csv()
header, *rows = it
print("CSV header:", header)
print("Row count:", len(rows))
```

    CSV header: ('Date', 'Make', 'Model', 'Year', 'Price')
    Row count: 200

- One thing to be careful is that the unpacking assignment will result
  in the entire iterator being read into memory
  - This could cause your program to crash
  - Only use catch-all unpacking for iterators when you have a good
    understanding of their size and can ensure it will fit in memory

## Things to Remember

- Unpacking assignments may include a starred expression to store all
  values not matching by any other variable capture
- Starred expressions may appear in any position of the unpacking
  - But only once per level of unpacking
  - There must be at least one variable assignment that is not to the
    starred expression
- The variable assigned by a starred expression will always be a list
  - If nothing is assigned to the variable, the list is empty
- When dividing a list into non-overlapping parts, catch-all unpacking
  is less error-prone and cleaner to read than using separate slicing
  and indexing statements
