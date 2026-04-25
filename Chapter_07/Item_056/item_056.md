# Item 56: Prefer `dataclasses` for Creating Immutable Objects

- [Notes](#notes)
  - [Preventing Objects from being
    Modified](#preventing-objects-from-being-modified)
  - [Creating Copies of Objects with Replaced
    Attributes](#creating-copies-of-objects-with-replaced-attributes)
  - [Using Immutable Objects in Dictionaries and
    Sets](#using-immutable-objects-in-dictionaries-and-sets)
    - [What about `NamedTuple`](#what-about-namedtuple)
- [Things to Remember](#things-to-remember)

## Notes

- Often it is useful to prevent objects from being modified after
  creation
- This is called *immutability* and is very common in functional-style
  programming
  - Mean’s that functions and methods map inputs to outputs
  - Reduces side-effects -\> each function has deterministic output
- Functional-style code is very easy to test
  - Need only consider input and output as opposed to stateful behaviour
- Instead of mutating an object we instead return a *new* object with
  the *new* values
- Objects that cannot be changed are said to be *immutable*
- Dataclasses built-in module provides a mechanism for defining
  immutable types (See [Item 51](../Item_051/item_051.qmd) for more on
  Dataclasses)
  - Also let’s such value types be used as dictionary keys and set
    members by default

### Preventing Objects from being Modified

- All python function arguments are passed by reference
  - Any callee may change a caller’s data (See [Item
    30](../../Chapter_05/Item_030/item_030.qmd))
- For example, consider a simple two-dimensional point representation

``` python
class Point:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y


def distance(p, q):
    return ((p.x - q.x) ** 2 + (p.y - q.y) ** 2) ** 0.5


origin = Point("source", 0, 0)
point = Point("destination", 3, 4)
print(distance(origin, point))
```

    5.0

- Now what if we wanted to write a function that determined the distance
  only in the `x` coordinate
  - We might write a function `x_distance` that reuses `distance` by
    first setting the `y` components of both points to $0$
  - This would work in a language like C which copies arguments, but
    here because the arguments are references we permanently alter the
    value of the points and any future distance calculations break

``` python
class Point:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y


def distance(p, q):
    return ((p.x - q.x) ** 2 + (p.y - q.y) ** 2) ** 0.5


def x_distance(p, q):
    p.y = 0
    q.y = 0
    return distance(p, q)


origin = Point("source", 0, 0)
point = Point("destination", 3, 4)
assert distance(origin, point) == 5.0  # works

# calculating just the x-distance
assert x_distance(origin, point) == 3.0

# Now attempting to recalculate the distance breaks
assert distance(origin, point) == 5.0
```

    AssertionError:
    ---------------------------------------------------------------------------
    AssertionError                            Traceback (most recent call last)
    Cell In[2], line 26
         23 assert x_distance(origin, point) == 3.0
         25 # Now attempting to recalculate the distance breaks
    ---> 26 assert distance(origin, point) == 5.0

    AssertionError:

- To prevent modifications in a standard class we have to implement the
  `__setattr__` and `__delattr__` dunder methods
  - Want to raise an `AttributeError` exception if called
- To set the initial values we then have to bypass `__setattr__` and
  `__delattr__` i.e. by directly invoking the class `__dict__` attribute
- `distance` then works as expected
- `x_distance` implementation will break because it violates
  immutability
  - But this preserves future calls to `distance` and the state of the
    object

``` python
class ImmutablePoint:
    def __init__(self, name, x, y):
        self.__dict__.update(name=name, x=x, y=y)

    def __setattr__(self, key, value):
        raise AttributeError("Immutable object: set not allowed")

    def __delattr__(self, key):
        raise AttributeError("Immutable object: set not allowed")


def distance(p, q):
    return ((p.x - q.x) ** 2 + (p.y - q.y) ** 2) ** 0.5


def x_distance(p, q):
    p.y = 0
    q.y = 0
    return distance(p, q)


origin = ImmutablePoint("source", 0, 0)
point = ImmutablePoint("destination", 3, 4)

assert distance(origin, point) == 5

print(x_distance(origin, point))
```

    AttributeError: Immutable object: set not allowed
    ---------------------------------------------------------------------------
    AttributeError                            Traceback (most recent call last)
    Cell In[3], line 27
         23 point = ImmutablePoint("destination", 3, 4)
         25 assert distance(origin, point) == 5
    ---> 27 print(x_distance(origin, point))

    Cell In[3], line 17, in x_distance(p, q)
         16 def x_distance(p, q):
    ---> 17     p.y = 0
         18     q.y = 0
         19     return distance(p, q)

    Cell In[3], line 6, in ImmutablePoint.__setattr__(self, key, value)
          5 def __setattr__(self, key, value):
    ----> 6     raise AttributeError("Immutable object: set not allowed")

    AttributeError: Immutable object: set not allowed

- Dataclasses implement the same functionality simply by passing
  `frozen=True` to the dataclass decorator

``` python
from dataclasses import dataclass


@dataclass(frozen=True)
class DataClassImmutablePoint:
    name: str
    x: float
    y: float


def distance(p, q):
    return ((p.x - q.x) ** 2 + (p.y - q.y) ** 2) ** 0.5


def x_distance(p, q):
    p.y = 0
    q.y = 0
    return distance(p, q)


origin = DataClassImmutablePoint("origin", 0, 0)
point = DataClassImmutablePoint("destination", 3, 4)
assert distance(origin, point) == 5

print(x_distance(origin, point))
```

    FrozenInstanceError: cannot assign to field 'y'
    ---------------------------------------------------------------------------
    FrozenInstanceError                       Traceback (most recent call last)
    Cell In[4], line 25
         22 point = DataClassImmutablePoint("destination", 3, 4)
         23 assert distance(origin, point) == 5
    ---> 25 print(x_distance(origin, point))

    Cell In[4], line 16, in x_distance(p, q)
         15 def x_distance(p, q):
    ---> 16     p.y = 0
         17     q.y = 0
         18     return distance(p, q)

    File <string>:17, in __setattr__(self, name, value)

    FrozenInstanceError: cannot assign to field 'y'

- Since the dataclass behaviour is built-in it can also be caught by
  static type-checkers

``` python
from dataclasses import dataclass


@dataclass(frozen=True)
class DataClassImmutablePoint:
    name: str
    x: float
    y: float


origin = DataClassImmutablePoint("origin", 0, 0)
origin.x = -3
```

    FrozenInstanceError: cannot assign to field 'x'
    ---------------------------------------------------------------------------
    FrozenInstanceError                       Traceback (most recent call last)
    Cell In[5], line 12
          8     y: float
         11 origin = DataClassImmutablePoint("origin", 0, 0)
    ---> 12 origin.x = -3

    File <string>:17, in __setattr__(self, name, value)

    FrozenInstanceError: cannot assign to field 'x'

- Running `ty` on the above output leads to

``` {shell}
error[invalid-assignment]: Property `x` defined in `DataClassImmutablePoint` is read-only
  --> ty_check.py:12:1
   |
11 | origin = DataClassImmutablePoint("origin", 0, 0)
12 | origin.x = -3
   | ^^^^^^^^
   |
info: rule `invalid-assignment` is enabled by default

Found 1 diagnostic
```

- If we want to achieve similar functionality with normal classes we can
  use `Final` and `Never`
  - These are type annotations supplied by `typing`

``` python
from typing import Any, Final, Never


class StaticallyAnalysableImmutablePoint:
    name: Final[str]
    x: Final[float]
    y: Final[float]

    def __init__(self, name: str, x: int, y: int) -> None:
        self.name = name
        self.x = x
        self.y = y

    def __setattr__(self, key: str, value: Any) -> None:
        if key in self.__class__.__annotations__ and key not in dir(self):
            # allow first assignment
            super().__setattr__(key, value)
        else:
            raise AttributeError("Immutable object: set not allowed")

    def __delattr__(self, key: str) -> Never:
        raise AttributeError("Immutable object: set not allowed")


origin = StaticallyAnalysableImmutablePoint("source", 0, 0)
origin.x = -3
```

    AttributeError: Immutable object: set not allowed
    ---------------------------------------------------------------------------
    AttributeError                            Traceback (most recent call last)
    Cell In[6], line 26
         22         raise AttributeError("Immutable object: set not allowed")
         25 origin = StaticallyAnalysableImmutablePoint("source", 0, 0)
    ---> 26 origin.x = -3

    Cell In[6], line 19, in StaticallyAnalysableImmutablePoint.__setattr__(self, key, value)
         17     super().__setattr__(key, value)
         18 else:
    ---> 19     raise AttributeError("Immutable object: set not allowed")

    AttributeError: Immutable object: set not allowed

- The result of running the above through `ty` is then,

``` {shell}
error[invalid-assignment]: Cannot assign to final attribute `x` on type `StaticallyAnalysableImmutablePoint`
  --> ty_check.py:26:1
   |
25 | origin = StaticallyAnalysableImmutablePoint("source", 0, 0)
26 | origin.x = -3
   | ^^^^^^^^
   |
info: rule `invalid-assignment` is enabled by default

Found 1 diagnostic
```

### Creating Copies of Objects with Replaced Attributes

- For immutable objects natural question is then how to create copies of
  objects where we need to update one of the fields
  - Since we can’t mutate a field directly, this means we will have to
    create a new instance
- For example we might wish to translate our point objects

``` python
class ImmutablePoint:
    def __init__(self, name, x, y):
        self.__dict__.update(name=name, x=x, y=y)

    def __setattr__(self, key, value):
        raise AttributeError("Immutable object: set not allowed")

    def __delattr__(self, key):
        raise AttributeError("Immutable object: set not allowed")


def translate(point, delta_x, delta_y):
    point.x += delta_x
    point.y += delta_y


# the above fails because the object is immutable
point = ImmutablePoint("origin", 0, 0)
translate(point, 10, 20)
```

    AttributeError: Immutable object: set not allowed
    ---------------------------------------------------------------------------
    AttributeError                            Traceback (most recent call last)
    Cell In[7], line 19
         17 # the above fails because the object is immutable
         18 point = ImmutablePoint("origin", 0, 0)
    ---> 19 translate(point, 10, 20)

    Cell In[7], line 13, in translate(point, delta_x, delta_y)
         12 def translate(point, delta_x, delta_y):
    ---> 13     point.x += delta_x
         14     point.y += delta_y

    Cell In[7], line 6, in ImmutablePoint.__setattr__(self, key, value)
          5 def __setattr__(self, key, value):
    ----> 6     raise AttributeError("Immutable object: set not allowed")

    AttributeError: Immutable object: set not allowed

- Obvious solution is to do the copy explicitly

``` python
class ImmutablePoint:
    def __init__(self, name, x, y):
        self.__dict__.update(name=name, x=x, y=y)

    def __setattr__(self, key, value):
        raise AttributeError("Immutable object: set not allowed")

    def __delattr__(self, key):
        raise AttributeError("Immutable object: set not allowed")


# version of translate that returns a copy
def translate(point, delta_x, delta_y):
    return ImmutablePoint(name=point.name, x=point.x + delta_x, y=point.y + delta_y)


point = ImmutablePoint("origin", 0, 0)
new_point = translate(point, 10, 20)  # assign to new instance
print(f"New point is at ({new_point.x}, {new_point.y}) as is called {new_point.name}")
```

    New point is at (10, 20) as is called origin

- Error prone
  - Have to copy across all attributes, even those we do not change
  - e.g. `name`
- It’s easy for the copy code to desynchronise from the rest of the code
- We can define a generic `_replace` method that allows for attributes
  to be overwritten
  - Returns a copy

``` python
class ImmutablePoint:
    def __init__(self, name, x, y):
        self.__dict__.update(name=name, x=x, y=y)

    def __setattr__(self, key, value):
        raise AttributeError("Immutable object: set not allowed")

    def __delattr__(self, key):
        raise AttributeError("Immutable object: set not allowed")

    # _replace returns a copy with overridable parameters
    def _replace(self, **overrides):
        fields = dict(
            name=self.name,
            x=self.x,
            y=self.y,
        )
        fields.update(overrides)
        cls = type(self)
        return cls(**fields)


# version of translate that returns a copy via _replace
def translate(point, delta_x, delta_y):
    return point._replace(x=point.x + delta_x, y=point.y + delta_y)


point = ImmutablePoint("origin", 0, 0)
new_point = translate(point, 10, 20)  # assign to new instance
print(f"New point is at ({new_point.x}, {new_point.y}) and is called {new_point.name}")
```

    New point is at (10, 20) and is called origin

- Work’s better because the copy code is one place now
  - Can be reused by other methods
- We still have the maintenance overhead of keeping `_replace` synched
  to any changes to the class
- Every class that wants to use `translate` also has to implement the
  `_replace` interface
- dataclasses provides the `replace` function
  - Works as above but invokes no maintenance overhead on our end

``` python
import dataclasses


@dataclasses.dataclass(frozen=True)
class DataClassImmutablePoint:
    name: str
    x: float
    y: float


# translate that works on dataclasses via the `dataclasses.replace` function
def translate(point, delta_x, delta_y):
    return dataclasses.replace(point, x=point.x + delta_x, y=point.y + delta_y)


origin = DataClassImmutablePoint("origin", 0, 0)
new_point = translate(origin, 10, 20)
print(f"New point is: {new_point}")
```

    New point is: DataClassImmutablePoint(name='origin', x=10, y=20)

### Using Immutable Objects in Dictionaries and Sets

- Every time we use the same key to access a dictionary we expect the
  access to respect previous accesses
  - i.e. if we use `key` to set then recall a value we should get that
    same value back
  - Overwriting a `key` should return the new value

``` python
my_dict = {}
my_dict["a"] = 123
print(my_dict["a"])
my_dict["a"] = 456
print(my_dict["a"])

# key accesses respect prior operations
```

    123
    456

- Adding a value to a set should also be idempotent (i.e. we can only
  add it once)

``` python
my_set = set()
my_set.add("b")
my_set.add("b")
print(my_set)
```

    {'b'}

- It is a requirement that these data structures provide *stable*
  mappings
- Default user-defined objects can’t be used as dictionary keys or set
  values
- For example, we might want to use our `Point` classes to simulate
  electricity
  - Points correspond to charges
  - Natural implementation is to use `Point` objects as key’s to a
    dictionary mapping points to charges
- The code below seems to work when we define the dictionary and then
  try to recall a `key` from the dictionary (`point_1`)
  - However, if we create an equivalent `Point` then the access fails

``` python
class Point:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y


point_1 = Point("A", 5, 10)
point_2 = Point("B", -7, 4)
charges = {
    point_1: 1.5,
    point_2: 3.5,
}

print(charges[point_1])

point_3 = Point("A", 5, 10)
print(charges[point_3])  # fails
```

    1.5

    KeyError: <__main__.Point object at 0x7f9d58ab5f90>
    ---------------------------------------------------------------------------
    KeyError                                  Traceback (most recent call last)
    Cell In[13], line 18
         15 print(charges[point_1])
         17 point_3 = Point("A", 5, 10)
    ---> 18 print(charges[point_3])  # fails

    KeyError: <__main__.Point object at 0x7f9d58ab5f90>

- This occurs because we haven’t defined an `__eq__` method
  - Since `point_1` and `point_3` refer to different memory they are not
    considered the same
- We can implement the `__eq__` and try again

``` python
class Point:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y

    def __eq__(self, other):
        return (
            type(self) == type(other),
            self.name == other.name,
            self.x == other.x,
            self.y == other.y,
        )


point_1 = Point("A", 5, 10)
point_2 = Point("B", -7, 4)
charges = {
    point_1: 1.5,
    point_2: 3.5,
}

print(charges[point_1])

point_3 = Point("A", 5, 10)

assert point_1 == point_3

print(charges[point_3])  # fails
```

    TypeError: cannot use 'Point' as a dict key (unhashable type: 'Point')
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[14], line 18
         16 point_1 = Point("A", 5, 10)
         17 point_2 = Point("B", -7, 4)
    ---> 18 charges = {
         19     point_1: 1.5,
         20     point_2: 3.5,
         21 }
         23 print(charges[point_1])
         25 point_3 = Point("A", 5, 10)

    TypeError: cannot use 'Point' as a dict key (unhashable type: 'Point')

- Now this still fails but here we can’t even use `Point` as a
  dictionary key because it is *unhashable*
- This means that we have to implement the `__hash__` dunder method
- Dictionary types rely on the value of the `__hash__` function (an
  integer) to construct the lookup table
  - To ensure the same object consistently keys the same value in the
    lookup table this hash
    1. Must not change for the same object over it’s lifetime
    2. Must be same for equivalent objects
- We can implement `__hash__` on our points by using the `hash`
  implementation on the object’s tuple representation
  - Now works as expected

``` python
class Point:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y

    def __eq__(self, other):
        return (
            type(self) == type(other),
            self.name == other.name,
            self.x == other.x,
            self.y == other.y,
        )

    def __hash__(self):
        return hash((self.name, self.x, self.y))


point_1 = Point("A", 5, 10)
point_2 = Point("B", -7, 4)
charges = {
    point_1: 1.5,
    point_2: 3.5,
}

print(charges[point_1])

point_3 = Point("A", 5, 10)

assert point_1 == point_3

print(charges[point_3])  # succeeds
```

    1.5
    1.5

- Using `frozen` to construct an immutable `dataclass` will
  automatically make the object hashable
- Can thus be used as a dictionary key or set value out of the box

``` python
from dataclasses import dataclass


@dataclass(frozen=True)
class DataClassImmutablePoint:
    name: str
    x: float
    y: float


point_1 = DataClassImmutablePoint("A", 5, 10)
point_2 = DataClassImmutablePoint("B", -7, 4)
charges = {
    point_1: 1.5,
    point_2: 3.5,
}

print(charges[point_1])

point_3 = DataClassImmutablePoint("A", 5, 10)

assert point_1 == point_3

print(charges[point_3])  # succeeds

# Using as a set value
my_set = {
    point_1,
    point_2,
    point_3,
}  # point_3 is equivalent to point_1 and should be discarded
assert my_set == {point_1, point_2}
```

    1.5
    1.5

#### What about `NamedTuple`

- Prior to `dataclasses`, `namedtuple` was an alternative for creating
  immutable objects

- `namedtuple` is a function provided by the `collections` built-in
  module

- Provides similar benefits to a frozen dataclass namely,

  1. Construction of objects with positional or keyword arguments
  2. Default values for unspecified attributes
  3. Automatic definition of object-oriented special methods
      - e.g. `__init__`, `__repr__`, `__eq__`, `__hash__`, `__lt__`
  4. Built-in helper methods
      - e.g. `replace` and `_dict` for modifying the representation
  5. Runtime introspection
      - `_fields` and `_field_` class attributes for introspection
  6. Support for static type checking via the `NamedTuple` class from
      `typing` built-in module
  7. Low memory usage by avoiding using `__dict__` instance
      dictionaries
      - Similar to dataclasses using `slots=True` (not discussed)

- Named tuples also allow positional indexing into their attributes

  - Useful for wrapping sequential data structures, e.g. CSV lines,
    Database rows
  - Dataclass requires the use of the `_astuple` method

- Sequential nature of named tuples might result in misuse

  - e.g. numerical indexing and iteration
  - Can be a subtle source of bugs

- Since it’s not structured like a standard class can make migration to
  a full-class implementation more difficult

  - Especially if it’s a heavily used API

- If the data is not sequential, prefer a dataclass or a regular class

## Things to Remember

- Functional style code on immutable objects is typically more robust
  than imperative-style or OOP style that relies heavily on modifying
  state
  - In general one should avoid side effects
- Using the `frozen` flag with a dataclass is the easiest way to create
  an immutable class
- The `replace` helper function from `dataclasses` simplifies creating
  copies of immutable objects with changed attribute values
  - Facilitates writing functional style code
- Immutable dataclasses are comparable for equivalence by value and have
  stable hashes
  - Can be used as dictionary keys or set values
