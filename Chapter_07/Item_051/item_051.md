# Item 51: Prefer `dataclasses` for Defining Lightweight Classes

- [Notes](#notes)
  - [Avoiding `__init__` boilerplate](#avoiding-__init__-boilerplate)
  - [Requiring Initialisation Arguments to Be Passed by
    Keyword](#requiring-initialisation-arguments-to-be-passed-by-keyword)
  - [Providing Default Attribute
    Values](#providing-default-attribute-values)
  - [Representing Objects as Strings](#representing-objects-as-strings)
  - [Converting Objects into Tuples](#converting-objects-into-tuples)
  - [Converting Objects into
    Dictionaries](#converting-objects-into-dictionaries)
  - [Checking Whether Objects are
    Equivalent](#checking-whether-objects-are-equivalent)
  - [Enabling Objects to be Compared](#enabling-objects-to-be-compared)
- [Things to Remember](#things-to-remember)

## Notes

- As code gets more complex, creating types helps to manage data and
  encapsulate behaviours (See [Item
  29](../../Chapter_04/Item_029/item_029.qmd))
- Python classes by default provide heavy object-oriented machinery
  - Can be overkill for simple classes
  - There are techniques to make this more approachable (See [Item
    57](../Item_057/item_057.qmd))
- `dataclasses` is a built-in module
  - Help’s reduce the repeated boilerplate in class definitions
  - Cost of use is a small runtime cost at `import` (due to using
    `exec`)
- `dataclass` is very useful for writing plain-old data (POD) or C-like
  structs
  - i.e. record types
  - See [Item 56](../Item_056/item_056.qmd) for more examples

### Avoiding `__init__` boilerplate

- First step with object’s is creation
- `__init__` special method is called to construct an object
  - Occurs when class name invoked like a function call
- For example, a simple RGB (Red, Green, Blue) colour value

``` python
class RGB:
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

    def __str__(self):
        return f"({self.red}, {self.green}, {self.blue})"


red = RGB(255, 0, 0)
print(red)
```

    (255, 0, 0)

- The `__init__` here doesn’t perform any special logic
- It’s otherwise just verbose, the class variables are referenced three
  times
  - Many opportunities to insert typos or mis-assign variables

``` python
class BadRGB:
    def __init__(
        self, green, red, blue
    ):  # Bad: Order swapped -> doesn't follow the expected Red, Green, Blue logic
        self.red = red
        self.green = green
        self.bloe = blue  # typo!

    def __str__(self):
        return f"({self.red}, {self.green}, {self.blue})"


red = BadRGB(255, 0, 0)
print(red)
```

    AttributeError: 'BadRGB' object has no attribute 'blue'
    ---------------------------------------------------------------------------
    AttributeError                            Traceback (most recent call last)
    Cell In[2], line 14
         10         return f"({self.red}, {self.green}, {self.blue})"
         13 red = BadRGB(255, 0, 0)
    ---> 14 print(red)

    Cell In[2], line 10, in BadRGB.__str__(self)
          9 def __str__(self):
    ---> 10     return f"({self.red}, {self.green}, {self.blue})"

    AttributeError: 'BadRGB' object has no attribute 'blue'

- `dataclasses` provides the `dataclass` decorator
  - Decorates a class to provide default behaviours
- We can reimplement our class using this decorator

``` python
from dataclasses import dataclass


@dataclass
class DataclassRGB:
    red: int
    green: int
    blue: int


red = DataclassRGB(255, 0, 0)
print(red)
```

    DataclassRGB(red=255, green=0, blue=0)

- To use the decorator define the data attributes as if they were class
  attributes
  - Attributes need to be tagged with the corresponding type hint
- Each attribute is defined only once
  - Reordering attributes only needs to update the callers
- Type annotations give us static type checking tools to detect errors
  before program execution
- For example, if we try to construct an RGB object with the wrong
  values

``` python
from dataclasses import dataclass


@dataclass
class DataclassRGB:
    red: int
    green: int
    blue: int


colour = DataclassRGB(1, "red", 3)
colour.red = "also bad"
```

- Then running `ty` to type check

``` {bash}
error[invalid-argument-type]: Argument is incorrect
   --> item_051.qmd:99:26
    |
 99 | colour = DataclassRGB(1, "red", 3)
    |                          ^^^^^ Expected `int`, found `Literal["red"]`
100 | obj.red = "also bad"
101 | ```
    |
info: rule `invalid-argument-type` is enabled by default
```

- You can do the same with a normal `__init__` method

``` python
from dataclasses import dataclass

class RGB:
    def __init__(self, red: int, green: int, blue: int) -> None: # updated signature
        self.red = red
        self.green = green
        self.blue = blue
```

- If you don’t want to deal with type annotations you can always use
  `Any`

``` python
from typing import Any
from dataclasses import dataclass


@dataclass
class DataclassRGB_Any:
    red: Any
    green: Any
    blue: Any


colour = DataclassRGB_Any(255, "green", 0)
print(colour)
```

    DataclassRGB_Any(red=255, green='green', blue=0)

### Requiring Initialisation Arguments to Be Passed by Keyword

- `__init__` accepts arguments like any other function
  - Includes both positional and keyword arguments (See [Item
    35](../../Chapter_05/Item_035/item_035.qmd))
- The following three methods of instantiating an `RGB` object are all
  valid

``` python
class RGB:
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

    def __str__(self):
        return f"({self.red}, {self.green}, {self.blue})"


red = RGB(255, 0, 0)
green = RGB(red=0, green=255, blue=0)
blue = RGB(0, 0, blue=255)

print(f"Red: {red}\nGreen: {green}\nBlue: {blue}")
```

    Red: (255, 0, 0)
    Green: (0, 255, 0)
    Blue: (0, 0, 255)

- Still prone to the issues raised earlier of mixing up the parameters
  in the initializer
- We can use `*` in the argument list to force keyword-only arguments

``` python
class RGB_keywordOnly:
    def __init__(self, *, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

    def __str__(self):
        return f"({self.red}, {self.green}, {self.blue})"


red = RGB_keywordOnly(red=255, green=0, blue=0)  # keyword only construction
print(red)

# positional argument construction fails
green = RGB_keywordOnly(0, 255, 0)
print(green)
```

    (255, 0, 0)

    TypeError: RGB_keywordOnly.__init__() takes 1 positional argument but 4 were given
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[8], line 15
         12 print(red)
         14 # positional argument construction fails
    ---> 15 green = RGB_keywordOnly(0, 255, 0)
         16 print(green)

    TypeError: RGB_keywordOnly.__init__() takes 1 positional argument but 4 were given

- `dataclass` decorated objects by default accept either positional or
  keyword arguments
  - Can pass `kw_only=True` to the decorator to make the `__init__` only
    accept keyword arguments

``` python
from dataclasses import dataclass


@dataclass(kw_only=True)
class DataclassRGB:
    red: int
    green: int
    blue: int


# keyword only construction
red = DataclassRGB(red=255, green=0, blue=0)
print(red)

# positional construction fails
green = DataclassRGB(0, 255, 0)
print(green)
```

    DataclassRGB(red=255, green=0, blue=0)

    TypeError: DataclassRGB.__init__() takes 1 positional argument but 4 were given
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[9], line 16
         13 print(red)
         15 # positional construction fails
    ---> 16 green = DataclassRGB(0, 255, 0)
         17 print(green)

    TypeError: DataclassRGB.__init__() takes 1 positional argument but 4 were given

### Providing Default Attribute Values

- Often useful to specify default values for data attributes
  - Especially when they take on the same value almost all of the time
- For example, our `RGB` class might also want an `alpha` value for
  transparency
  - By default colours are opaque (`alpha = 1`)
- Can be defined via the `__init__` as for any default value

``` python
class RGBA:
    def __init__(self, *, red, green, blue, alpha=1.0):
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha

    def __str__(self):
        return f"({self.red}, {self.green}, {self.blue}, alpha={self.alpha})"


red = RGBA(red=255, green=0, blue=0)
print(red)
```

    (255, 0, 0, alpha=1.0)

- To provide a default value for a dataclass, simply define it in the
  class definition

``` python
from dataclasses import dataclass

@dataclass(kw_only=True)
class DataclassRGBA:
    red: int
    green: int
    blue: int
    alpha: int = 1.0

red = DataclassRGBA(red=255, green=0, blue=0)
print(red)
```

    DataclassRGBA(red=255, green=0, blue=0, alpha=1.0)

- Neither approach works for mutable values (See [Item
  26](../../Chapter_04/Item_026/item_026.qmd) and [Item
  30](../../Chapter_05/Item_030/item_030.qmd))
  - E.g. If we try to pass a `list` as the default value this is shared
    across all calls

``` python
from dataclasses import dataclass


class BadContainer:
    def __init__(self, values=[]):
        self.values = values


obj1 = BadContainer()
obj2 = BadContainer()
obj1.values.append(1)
print(obj2.values)  # We want this to be empty, but it's not!
```

    [1]

- For standard classes we can use the `None` technique, instead
  constructing the default in the body of the `__init__` (See [Item
  36](../../Chapter_05/Item_036/item_036.qmd))

``` python
class MyContainer:
    def __init__(self, *, value=None):
        if value is None:
            value = [] # Create when not supplied
        self.value = value

obj1 = MyContainer()
obj2 = MyContainer()
obj1.value.append(1)
assert obj1.value == [1]
assert obj2.value == []
```

- For a `dataclass` we have to use the `field` helper function
  - Let’s us supply `default_factory`
  - This is a function called to create a new default value for an
    attribute

``` python
from dataclasses import field


@dataclass
class DataClassContainer:
    value: list = field(default_factory=list)


obj1 = DataClassContainer()
obj2 = DataClassContainer()
obj1.value.append(1)
assert obj1.value == [1]
assert obj2.value == []
```

- Refer to the [dataclass
  docs](https://docs.python.org/3/library/dataclasses.html) for more
  information on features they provide

### Representing Objects as Strings

- Recall that when we define a class the default string representation
  simply provides back a memory address

``` python
class RGB:
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue


red = RGB(red=255, green=0, blue=0)
print(red)
```

    <__main__.RGB object at 0x7f4a5c9fc590>

- One can implement either `__repr__` or `__str__` (See [Item
  12](../../Chapter_02/Item_012/item_012.qmd))
- E.g. one might use a format string to construct a representation (See
  [Item 11](../../Chapter_02/Item_011/item_011.qmd))

``` python
class RGB:
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

    def __repr__(self):
        return (
            f"{type(self).__module__}"
            f".{type(self).__name__}("
            f"red={self.red!r}, "
            f"green={self.green!r}, "
            f"blue={self.blue!r})"
        )

red = RGB(red=255, green=0, blue=0)
print(red)
```

    __main__.RGB(red=255, green=0, blue=0)

- `__repr__` is a pain to implement yourself
  - Repetitive and boilerplate
  - Needs to be added to all classes
  - Error prone
    - Need to include *all* the attributes, in the *right* order (else
      positional reconstruction might fail)
- `dataclass` decorator will generate a default `__repr__` string by
  default
  - We’ve seen this already when we’ve called `print` on our dataclasses

### Converting Objects into Tuples

- Often to help with equality testing and sorting it’s useful to convert
  an object to a tuple
- For a standard python class we can define a conversion method

``` python
class RGB:
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

    def __str__(self):
        return f"({self.red}, {self.green}, {self.blue})"

    def _astuple(self):
        return (self.red, self.green, self.blue)

red = RGB(red=255, green=0, blue=0)
print(red._astuple())
```

    (255, 0, 0)

- `_astuple` can be used to construct a copy via unpacking into the
  `__init__` method (See [Item
  34](../../Chapter_05/Item_034/item_034.qmd) and [Item
  16](../../Chapter_02/Item_016/item_016.qmd))

``` python
class RGB:
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

    def __str__(self):
        return f"({self.red}, {self.green}, {self.blue})"

    def _astuple(self):
        return (self.red, self.green, self.blue)


red = RGB(red=255, green=0, blue=0)
print(red._astuple())

red_copy = RGB(*red._astuple())
print(red_copy)

assert red is not red_copy
```

    (255, 0, 0)
    (255, 0, 0)

- Again, like `__repr__` this can be hard to write correctly and
  maintain it
- Dataclasses provides an `astuple` function out of the box that can be
  used to convert any `dataclass`-decorated character

``` python
from dataclasses import dataclass, astuple


@dataclass
class DataclassRGB:
    red: int
    green: int
    blue: int


red = DataclassRGB(red=255, green=0, blue=0)
print(astuple(red))
```

    (255, 0, 0)

### Converting Objects into Dictionaries

- Data serialisation is often aided by using an intermediate conversion
  into a dictionary
- We can define the `asdict` analogy to `astuple`

``` python
import json


class RGB:
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

    def __str__(self):
        return f"({self.red}, {self.green}, {self.blue})"

    def _asdict(self):
        return dict(red=self.red, green=self.green, blue=self.blue)


red = RGB(red=255, green=0, blue=0)
data = json.dumps(red._asdict())
print(data)

# using _asdict to create a copy via keyword unpacking
red_copy = RGB(**red._asdict())
print(red_copy)

assert red is not red_copy
```

    {"red": 255, "green": 0, "blue": 0}
    (255, 0, 0)

- We can get the same behaviour directly with a dataclass via the
  `asdict` method

``` python
from dataclasses import dataclass, asdict


@dataclass
class DataclassRGB:
    red: int
    green: int
    blue: int


red = DataclassRGB(red=255, green=0, blue=0)
print(asdict(red))
```

    {'red': 255, 'green': 0, 'blue': 0}

### Checking Whether Objects are Equivalent

- By default python’s object equality check, check’s that two objects
  reference the same memory
  - Means that two distinct objects with the same attribute values do
    not compare equal

``` python
class RGB:
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

    def __str__(self):
        return f"({self.red}, {self.green}, {self.blue})"

    def _astuple(self):
        return (self.red, self.green, self.blue)


red = RGB(255, 0, 0)
red_2 = RGB(255, 0, 0)
print(red == red_2)

assert red == red
assert red is red
assert red != red_2
assert red is not red_2
```

    False

- To overwrite the behaviour we have to define an implementation of the
  `__eq__`
- For simple objects we typically want to just match the attributes

``` python
class RGB:
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

    def __str__(self):
        return f"({self.red}, {self.green}, {self.blue})"

    def _astuple(self):
        return (self.red, self.green, self.blue)

    def __eq__(self, other):
        return type(self) == type(other) and (self._astuple() == other._astuple())


red = RGB(255, 0, 0)
red_2 = RGB(255, 0, 0)
green = RGB(0, 255, 0)

assert red == red
assert red == red_2
assert red is not red_2
assert red != green
```

- For dataclasses a default `__eq__` method is generated automatically
  - The implementation is a tuple-based comparison

``` python
from dataclasses import dataclass, asdict


@dataclass
class DataclassRGB:
    red: int
    green: int
    blue: int


red = DataclassRGB(255, 0, 0)
green = DataclassRGB(0, 255, 0)
red_2 = DataclassRGB(255, 0, 0)

assert red == red
assert red == red_2
assert red is not red_2
assert red != green
```

### Enabling Objects to be Compared

- Useful to often be able to order objects
  - E.g. We might want to represent planets and their distance from
    Earth
  - If we try and sort these objects we get an exception because no sort
    is ordered

``` python
class Planet:
    def __init__(self, distance, size):
        self.distance = distance
        self.size = size

    def __repr__(self):
        return (
            f"{type(self).__module__}"
            f"{type(self).__name__}("
            f"distance={self.distance}, "
            f"size={self.size})"
        )

far = Planet(10, 5)
near = Planet(1, 2)
data = [far, near]
data.sort()
print(data)
```

    TypeError: '<' not supported between instances of 'Planet' and 'Planet'
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[25], line 17
         15 near = Planet(1, 2)
         16 data = [far, near]
    ---> 17 data.sort()
         18 print(data)

    TypeError: '<' not supported between instances of 'Planet' and 'Planet'

- There are alternatives for most cases (such as using `sort` and
  passing a `key` function)
- However, often it is useful for an object to have it’s own natural
  ordering (or we might just want to do a comparison)
- To do comparison we need to implement the `__lt__` (less than),
  `__le__` (less than or equal), `__gt__` (greater than) or `__ge__`
  (greater than or equal)
  - A natural technique is to pass this over to a comparison on the
    tuple representation

``` python
class Planet:
    def __init__(self, distance, size):
        self.distance = distance
        self.size = size

    def __repr__(self):
        return (
            f"{type(self).__module__}"
            f"{type(self).__name__}("
            f"distance={self.distance}, "
            f"size={self.size})"
        )

    def __eq__(self, other):
        return type(self) == type(other) and self._astuple() == other._astuple()

    def __lt__(self, other):
        if type(self) != type(other):
            raise NotImplemented
        return self._astuple() < other._astuple()

    def __le__(self, other):
        if type(self) != type(other):
            raise NotImplemented
        return self._astuple() <= other._astuple()

    def __gt__(self, other):
        if type(self) != type(other):
            raise NotImplemented
        return self._astuple() > other._astuple()

    def __ge__(self, other):
        if type(self) != type(other):
            raise NotImplemented
        return self._astuple() >= other._astuple()

    def _astuple(self):
        return (self.distance, self.size)


far = Planet(10, 5)
near = Planet(1, 2)
data = [far, near]
data.sort()
print(data)
```

    [__main__Planet(distance=1, size=2), __main__Planet(distance=10, size=5)]

- Python allows comparisons between arbitrary types
  - We return the `NotImplemented` *singleton* to indicate an object
    could not be compared
  - This is *not* the same as raising `NotImplementedError`
- Observe that we had to write *four* methods to do comparison
  - One way to remove the boilerplate is to use the `total_ordering`
    class decorator from `functools`
- With a `dataclass` we can generate an ordering with the `order` flag
  - This determines the order by interpreting the attributes as an
    ordered tuple of values

``` python
from dataclasses import dataclass


@dataclass(order=True)
class DataclassPlanet:
    distance: float
    size: float


far = DataclassPlanet(10, 2)
near = DataclassPlanet(1, 5)
assert far > near
assert near < far
```

## Things to Remember

- `dataclass` decorator from `dataclasses` built-in can be used to
  define versatile, lightweight classes in python
  - Eliminates most of the boilerplate associated with setting up
    classes in python
- `dataclasses` helps avoid verbosity associated with python’s
  object-oriented feature sets
- `dataclasses` provides additional functions like `astuple` and
  `asdict` for conversions
- `dataclasses` provides advanced attribute behaviours e.g. `field`
- It is important to understand how to implement OOP idioms yourself for
  when you have larger classes that need more customisation than
  `dataclass` can provide
