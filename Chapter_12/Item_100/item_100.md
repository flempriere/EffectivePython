# Item 100: Sort by Complex Criteria using the `key` Parameter

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- `list` provides a built-in `sort` method
  - Don’t confuse it with the `sorted` built-in function (See [Item
    101](../Item_101/item_101.qmd))
  - Default `sort` orders is the *natural ascending* order
  - e.g. numbers from smallest to largest, strings alphabetically

``` python
numbers = [93, 86, 11, 68, 70]
numbers.sort()
print(numbers)
```

    [11, 68, 70, 86, 93]

- For non-trivial or user-defined types `sort` often fails
  - Need to define the underlying comparison operators
  - Here we have a lightweight class with a simple `repr` method (See
    [Item 12](../../Chapter_02/Item_012/item_012.qmd))

``` python
class Tool:
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight

    def __repr__(self):
        return f"Tool({self.name!r}, {self.weight})"


tools = [
    Tool("level", 3.5),
    Tool("hammer", 1.25),
    Tool("screwdriver", 0.5),
    Tool("chisel", 0.25),
]

tools.sort()
```

    TypeError: '<' not supported between instances of 'Tool' and 'Tool'
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[2], line 17
          7         return f"Tool({self.name!r}, {self.weight})"
         10 tools = [
         11     Tool("level", 3.5),
         12     Tool("hammer", 1.25),
         13     Tool("screwdriver", 0.5),
         14     Tool("chisel", 0.25),
         15 ]
    ---> 17 tools.sort()

    TypeError: '<' not supported between instances of 'Tool' and 'Tool'

- When we have a natural ordering, consider defining the comparison
  operators
  - Let’s `sort` work out of the box
- For complex objects and record types it often doesn’t make sense to
  have a *natural* ordering (See [Item 104](../Item_104/item_104.qmd)
  and [Item 57](../../Chapter_07/Item_057/item_057.qmd))
  - For example, A list of songs, might sort,
    - On the name of the artist
    - The length of the song
- For simple cases `sort` provides the `key` parameter
  - Is a function that takes in an element of a list and returns a
    comparable object (See [Item
    48](../../Chapter_07/Item_048/item_048.qmd))
- We can use `lambda` or `functools.partial` to help define glue
  functions (See [Item 39](../../Chapter_05/Item_039/item_039.qmd))
  - Here we can sort the `Tool` objects alphabetically by name

``` python
class Tool:
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight

    def __repr__(self):
        return f"Tool({self.name!r}, {self.weight})"


tools = [
    Tool("level", 3.5),
    Tool("hammer", 1.25),
    Tool("screwdriver", 0.5),
    Tool("chisel", 0.25),
]

print("Unsorted:    ", repr(tools))
tools.sort(key=lambda x: x.name)
print("\nSorted:    ", tools)
```

    Unsorted:     [Tool('level', 3.5), Tool('hammer', 1.25), Tool('screwdriver', 0.5), Tool('chisel', 0.25)]

    Sorted:     [Tool('chisel', 0.25), Tool('hammer', 1.25), Tool('level', 3.5), Tool('screwdriver', 0.5)]

- Instead we could sort on `weight`

``` python
class Tool:
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight

    def __repr__(self):
        return f"Tool({self.name!r}, {self.weight})"


tools = [
    Tool("level", 3.5),
    Tool("hammer", 1.25),
    Tool("screwdriver", 0.5),
    Tool("chisel", 0.25),
]

print("Unsorted:    ", repr(tools))
tools.sort(key=lambda x: x.weight)
print("\nSorted:    ", tools)
```

    Unsorted:     [Tool('level', 3.5), Tool('hammer', 1.25), Tool('screwdriver', 0.5), Tool('chisel', 0.25)]

    Sorted:     [Tool('chisel', 0.25), Tool('screwdriver', 0.5), Tool('hammer', 1.25), Tool('level', 3.5)]

- The `key` parameter is flexible because it can be implemented as any
  function that matches the interface
  - Can access item attributes
  - Index into items
    - Sequences
    - Tuples
    - Dictionaries
  - Use any valid expression
- For example, with string types we can use `key` to transform the
  input, e.g. cleaning
  - For example, we might use `strip` and `lower` to remove extra
    whitespace and convert to lowercase before comparing

``` python
places = ["home", "work", "New York", " Paris"]
places.sort()
print("Case Sensitive Sort: ", places)
places.sort(key=lambda x: x.lower())
print("Case Insensitive Sort:   ", places)
```

    Case Sensitive Sort:  [' Paris', 'New York', 'home', 'work']
    Case Insensitive Sort:    [' Paris', 'home', 'New York', 'work']

- How do we handle sorting on multiple fields?
  - e.g. We want to use a second field to split ties in a first field
  - For example sorting tools by weight, then name
- A simple way to do this is using a `tuple` (See [Item
  56](../../Chapter_7/Item_056/item_056.qmd))
  - By default, tuples are naturally ordered
  - Each index is compared in sequence

``` python
saw = (5, "circular saw")
jackhammer = (40, "jackhammer")

assert not (jackhammer < saw)  # Matches expectation
print("Jackhammer compares less than  saw")

drill = (4, "drill")
sander = (4, "sander")

assert drill[0] == sander[0]  # Same weight
assert drill[1] < sander[1]  # Alphabetically less
assert drill < sander
print("Drill compares less than sander")
```

    Jackhammer compares less than  saw
    Drill compares less than sander

- We could implement this behaviour using a `lambda` to work with our
  `Tool` class

``` python
class Tool:
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight

    def __repr__(self):
        return f"Tool({self.name!r}, {self.weight})"


power_tools = [
    Tool("drill", 4),
    Tool("circular saw", 5),
    Tool("jackhammer", 40),
    Tool("sander", 4),
]

power_tools.sort(key=lambda x: (x.weight, x.name))
print(power_tools)
```

    [Tool('drill', 4), Tool('sander', 4), Tool('circular saw', 5), Tool('jackhammer', 40)]

- What happens if we want to `sort` in the opposite order,
  e.g. descending rather than ascending
- Can so via the `reverse` parameter

``` python
class Tool:
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight

    def __repr__(self):
        return f"Tool({self.name!r}, {self.weight})"


power_tools = [
    Tool("drill", 4),
    Tool("circular saw", 5),
    Tool("jackhammer", 40),
    Tool("sander", 4),
]

power_tools.sort(key=lambda x: (x.weight, x.name), reverse=True)
print(power_tools)
```

    [Tool('jackhammer', 40), Tool('circular saw', 5), Tool('sander', 4), Tool('drill', 4)]

- `tuple` approach is difficult to generalise if we want to have mixed
  ascending and descending sorting
  - By default all fields are compared in the same way
- For numerical types we can get around this by using the negation
  operator.
- For example, if we want to sort by `weight` in descending, but name is
  ascending we can write

``` python
class Tool:
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight

    def __repr__(self):
        return f"Tool({self.name!r}, {self.weight})"


power_tools = [
    Tool("drill", 4),
    Tool("circular saw", 5),
    Tool("jackhammer", 40),
    Tool("sander", 4),
]

power_tools.sort(key=lambda x: (-x.weight, x.name))  # Descending Weight, Ascending name
print(power_tools)
```

    [Tool('jackhammer', 40), Tool('circular saw', 5), Tool('drill', 4), Tool('sander', 4)]

- Obviously, doesn’t work for types for which negation isn’t defined,
  e.g.
  - Can’t *negate* a `str`

``` python
class Tool:
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight

    def __repr__(self):
        return f"Tool({self.name!r}, {self.weight})"


power_tools = [
    Tool("drill", 4),
    Tool("circular saw", 5),
    Tool("jackhammer", 40),
    Tool("sander", 4),
]

power_tools.sort(key=lambda x: (x.weight, -x.name))  # Negated name
print(power_tools)
```

    TypeError: bad operand type for unary -: 'str'
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[10], line 17
          7         return f"Tool({self.name!r}, {self.weight})"
         10 power_tools = [
         11     Tool("drill", 4),
         12     Tool("circular saw", 5),
         13     Tool("jackhammer", 40),
         14     Tool("sander", 4),
         15 ]
    ---> 17 power_tools.sort(key=lambda x: (x.weight, -x.name))  # Negated name
         18 print(power_tools)

    Cell In[10], line 17, in <lambda>(x)
          7         return f"Tool({self.name!r}, {self.weight})"
         10 power_tools = [
         11     Tool("drill", 4),
         12     Tool("circular saw", 5),
         13     Tool("jackhammer", 40),
         14     Tool("sander", 4),
         15 ]
    ---> 17 power_tools.sort(key=lambda x: (x.weight, -x.name))  # Negated name
         18 print(power_tools)

    TypeError: bad operand type for unary -: 'str'

- For this case can *chain* sorts together since `sort` is *stable*
  - Means that order of equal keys is preserved
- We can repeat the descending weight, ascending name example using two
  chained sorts

``` python
class Tool:
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight

    def __repr__(self):
        return f"Tool({self.name!r}, {self.weight})"


power_tools = [
    Tool("drill", 4),
    Tool("circular saw", 5),
    Tool("jackhammer", 40),
    Tool("sander", 4),
]

power_tools.sort(key=lambda x: x.name)  # First sort on the name ascending
print("Sorted on name:  ", power_tools)
power_tools.sort(key=lambda x: x.weight, reverse=True)
print("Then sorted on weight:   ", power_tools)
```

    Sorted on name:   [Tool('circular saw', 5), Tool('drill', 4), Tool('jackhammer', 40), Tool('sander', 4)]
    Then sorted on weight:    [Tool('jackhammer', 40), Tool('circular saw', 5), Tool('drill', 4), Tool('sander', 4)]

- The caveat is that we have to do the sort calls in reverse order, i.e.
  - Call the *least* important `sort` key first
  - Call the *most* important `sort` key last
- When you can get away with it prefer using the tuple approach
  - Especially when it can be combined with negation
  - It’s more concise and more readable

## Things to Remember

- `sort` can be used to rearrange a list in-place
  - Built-in types can typically be sorted out of the box due to
    *natural orderings*
- `sort` doesn’t work for types that don’t define the comparison
  operators
  - Common for most non-primitive types
- `key` parameter lets you pass a function to perform the comparison on
  - Interface accepts an item from a list
  - Returns a comparable value
- Multiple sort criteria can be combined by using a `tuple` as the
  return value from `key`
  - Tuple indices are compared in sequence
  - Unary minus can be used to reverse the sort order of numeric fields
- For non-negatable types `sort` is stable, so calls can be chained
  - Allows for combining different `key` and `reverse` orders
  - Must be called in order of least important sort key to most
    important
