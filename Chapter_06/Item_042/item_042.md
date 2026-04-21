# Item 42: Reduce Repetition in Comprehensions with Assignment

Expressions

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- A pattern in comprehensions is re-referencing the same computation
- For Example, consider a program managing orders for a company
  - When we receive a new order we need to validate that we can meet it
  - E.g. We have enough stock and the order meets the minimum threshold
    (say eight)

``` python
stock = {
    "nails": 125,
    "screws": 35,
    "wingnuts": 8,
    "washers": 24,
}

order = ["screws", "wingnuts", "clips"]


def get_batches(count, size):
    return count // size


result = {}
for name in order:
    count = stock.get(name, 0)
    batches = get_batches(count, 8)
    if batches:
        result[name] = batches

print(result)
```

    {'screws': 4, 'wingnuts': 1}

- We could instead use a dictionary comprehension to flatten the looping
  logic (See [Item 40](../Item_040/item_040.qmd))

``` python
stock = {
    "nails": 125,
    "screws": 35,
    "wingnuts": 8,
    "washers": 24,
}

order = ["screws", "wingnuts", "clips"]


def get_batches(count, size):
    return count // size


found = {
    name: get_batches(stock.get(name, 0), 8)
    for name in order
    if get_batches(stock.get(name, 0), 8)
}

print(found)
```

    {'screws': 4, 'wingnuts': 1}

- The code is more compact
- However, we have repeated the call to `get_batches`
  - Now have to keep these parts of the code synchronised
- For example if we update our minimum order size in one location but
  not the other…

``` python
has_bug = {
    name: get_batches(stock.get(name, 0), 4)  # changed this one
    for name in order
    if get_batches(stock.get(name, 0), 8)  # but not this one
}

print("Expected:", found)
print("Found:   ", has_bug)
```

    Expected: {'screws': 4, 'wingnuts': 1}
    Found:    {'screws': 8, 'wingnuts': 2}

- A simple fix is to use assignment expressions (See [Item
  8](../../Chapter_01/Item_008/item_008.qmd))
  - Also called the *walrus operator*

``` python
stock = {
    "nails": 125,
    "screws": 35,
    "wingnuts": 8,
    "washers": 24,
}

order = ["screws", "wingnuts", "clips"]


def get_batches(count, size):
    return count // size


found = {
    name: batches for name in order if (batches := get_batches(stock.get(name, 0), 8))
}

print(found)
```

    {'screws': 4, 'wingnuts': 1}

- Here the assignment expression means `get_batches` is called one and
  it’s result is stored in the variable `batches`
  - We can then reference this in the remaining part of the
    comprehension
- You have to be careful when using the assignment operator
  - You must ensure the variable exists before referencing it
  - Same way if we had two nested loops we can’t reference variables
    defined in the inner loop in the outer loop

``` python
stock = {
    "nails": 125,
    "screws": 35,
    "wingnuts": 8,
    "washers": 24,
}

result = {name: (tenth:= count // 10) for name, count in stock.items() if tenth > 0}
```

    NameError: name 'tenth' is not defined
    ---------------------------------------------------------------------------
    NameError                                 Traceback (most recent call last)
    Cell In[5], line 8
          1 stock = {
          2     "nails": 125,
          3     "screws": 35,
          4     "wingnuts": 8,
          5     "washers": 24,
          6 }
    ----> 8 result = {name: (tenth:= count // 10) for name, count in stock.items() if tenth > 0}

    NameError: name 'tenth' is not defined

- In the example above we have effectively tried to write the following,

``` python
stock = {
    "nails": 125,
    "screws": 35,
    "wingnuts": 8,
    "washers": 24,
}

result = {}
for name, count in stock.items():
    if tenth > 0:
        tenth = count // 10
        result[name] = tenth
```

    NameError: name 'tenth' is not defined
    ---------------------------------------------------------------------------
    NameError                                 Traceback (most recent call last)
    Cell In[6], line 10
          8 result = {}
          9 for name, count in stock.items():
    ---> 10     if tenth > 0:
         11         tenth = count // 10
         12         result[name] = tenth

    NameError: name 'tenth' is not defined

- This makes it obvious what is going on, we’re trying to use `tenth` in
  the control expression before we’ve even defined the variable!
- The fix here is move the assignment expression into the first place
  it’s referenced (here the `if` statement)

``` python
stock = {
    "nails": 125,
    "screws": 35,
    "wingnuts": 8,
    "washers": 24,
}

result = {name: tenth for name, count in stock.items() if (tenth := count // 10) > 0}
print(result)
```

    {'nails': 12, 'screws': 3, 'washers': 2}

- Variables assigned using the walrus operator will leak into the
  containing scope (See [Item
  33](../../Chapter_05/Item_033/item_033.qmd))

``` python
stock = {
    "nails": 125,
    "screws": 35,
    "wingnuts": 8,
    "washers": 24,
}

half = [(squared := last**2) for count in stock.values() if (last := count // 2) > 10]

print(f"Last item of {half} is {last} ** 2 = {squared}")
```

    Last item of [3844, 289, 144] is 12 ** 2 = 144

- This is similar to a normal `for` loop

``` python
stock = {
    "nails": 125,
    "screws": 35,
    "wingnuts": 8,
    "washers": 24,
}

for count in stock.values():
    last = count // 2
    squared = last**2

print(f"{count} // 2 = {last}; {last} ** 2 = {squared}")
```

    24 // 2 = 12; 12 ** 2 = 144

- As with `for` loops you should avoid using these leaked variables (See
  [Item 20](../../Chapter_03/Item_020/item_020.qmd))
- Especially so for comprehensions since they don’t normally leak
  variables

``` python
stock = {
    "nails": 125,
    "screws": 35,
    "wingnuts": 8,
    "washers": 24,
}

half = [count // 2 for count in stock.values()]
print(half)  # Works
print(count)  # Exception because loop variable didn't leak
```

    [62, 17, 4, 12]
    24

- Assignment expressions can also be used in generator comprehensions
  (See [Item 44](../Item_044/item_044.qmd))
- They have the same behaviour such as leakage etc.

``` python
stock = {
    "nails": 125,
    "screws": 35,
    "wingnuts": 8,
    "washers": 24,
}

order = ["screws", "wingnuts", "clips"]


def get_batches(count, size):
    return count // size


found = (
    (name, batches) for name in order if (batches := get_batches(stock.get(name, 0), 8))
)

print(next(found))
print(next(found))
```

    ('screws', 4)
    ('wingnuts', 1)

## Things to Remember

- Assignment expressions let comprehensions and generator expressions
  reuse values from one condition elsewhere in the same comprehension
  - This can improve readability and performance
- It’s possible to use the result of an assignment expression outside of
  the comprehension or generator expression’s condition
  - Avoid doing so as this behaviour is inconsistent
- In comprehensions
  - Variables assigned by an assignment expression leak into the
    enclosing scope
  - Normal loop variables don’t leak
