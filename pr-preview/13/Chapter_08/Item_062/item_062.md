# Item 62: Validate Subclasses with `__init_subclasses__`


- [Notes](#notes)
  - [What does a Metaclass do?](#what-does-a-metaclass-do)
  - [Metaclasses and Multiple
    Inheritance](#metaclasses-and-multiple-inheritance)
- [Things to Remember](#things-to-remember)

## Notes

- A simple application of metaclasses is verifying a class is defined
  correctly
  - When building a class hierarchy can be useful to
    1.  Enforce style
    2.  Require method overrides
    3.  Maintain strict relationships between attributes
- Metaclasses provide a mechanism to run validation code at class
  definition
- Typically validation code runs in the `__init__` method
  - i.e. During object creation at runtime (See [Item
    58](../Item_058/item_058.qmd))
- Metaclasses means the error is caught earlier
  - Such as during module import

### What does a Metaclass do?

- Metaclasses are defined by inheriting from `type`
- Classes indicate a metaclass via the `metaclass` keyword in the
  inheritance argument list
- Metaclass’ `__new__` is called with any associated `class` statements
  when they occur

``` python
class Meta(type):
    def __new__(meta, name, bases, class_dict):
        # meta is equivalent of cls or self
        # name is the class name
        # base is any parent classes for the class
        print(f"* Running {meta}.__new__ for {name}")
        print("Bases:", bases)
        print(class_dict)
        return type.__new__(meta, name, bases, class_dict) # equivalent to super

class MyClass(metaclass=Meta):
    stuff = 123

    def foo():
        pass

class MySubClass(MyClass):
    other = 567

    def bar():
        pass
```

    * Running <class '__main__.Meta'>.__new__ for MyClass
    Bases: ()
    {'__module__': '__main__', '__qualname__': 'MyClass', '__firstlineno__': 11, 'stuff': 123, 'foo': <function MyClass.foo at 0x7f177facba00>, '__static_attributes__': (), '__classdictcell__': <cell at 0x7f177c474a90: dict object at 0x7f177c2d0140>}
    * Running <class '__main__.Meta'>.__new__ for MySubClass
    Bases: (<class '__main__.MyClass'>,)
    {'__module__': '__main__', '__qualname__': 'MySubClass', '__firstlineno__': 17, 'other': 567, 'bar': <function MySubClass.bar at 0x7f177facb8a0>, '__static_attributes__': (), '__classdictcell__': <cell at 0x7f177c474c40: dict object at 0x7f177c2d3f40>}

- Metaclass has access to,
  1.  Itself (`meta`)
  2.  The name of the class (`name`)
  3.  Parent classes - not including `object` (`bases`)
  4.  All class attributes
- Functionality can be added to `Meta.__new__` to validate all the
  parameters of a subclass
- For example, we might have base class representing polygons
  - Define an appropriate metaclass and validate that all polygon
    subclasses have the appropriate number of sides
  - Attempting to define an polygon with less than three sides causes
    the class statement to fail as soon as the program attempts to
    define the object

``` python
# defining the metaclass
class ValidatePolygon(type):
    def __new__(meta, name, bases, class_dict):
        # Only validate subclasses of the Polygon class
        if bases:
            if class_dict["sides"] < 3:
                raise ValueError("Polygons need 3+ sides")
        return type.__new__(meta, name, bases, class_dict)

class Polygon(metaclass=ValidatePolygon):
    sides = None # Must be specified by subclasses

    @classmethod
    def interior_angle(cls):
        return (cls.sides - 2) * 180

print("Defining valid Polygons")

class Triangle(Polygon):
    sides = 3

class Rectangle(Polygon):
    sides = 4

class Nonagon(Polygon):
    sides = 9

# validation all works and passes
assert Triangle.interior_angle() == 180
assert Rectangle.interior_angle() == 360
assert Nonagon.interior_angle() == 1260

print("Defining an invalid Polygon")

class Line(Polygon):
    sides = 2

assert Line.interior_angle() == 0
```

    Defining valid Polygons
    Defining an invalid Polygon

    ValueError: Polygons need 3+ sides
    ---------------------------------------------------------------------------
    ValueError                                Traceback (most recent call last)
    Cell In[2], line 35
         31 assert Nonagon.interior_angle() == 1260
         33 print("Defining an invalid Polygon")
    ---> 35 class Line(Polygon):
         36     sides = 2
         38 assert Line.interior_angle() == 0

    Cell In[2], line 7, in ValidatePolygon.__new__(meta, name, bases, class_dict)
          5 if bases:
          6     if class_dict["sides"] < 3:
    ----> 7         raise ValueError("Polygons need 3+ sides")
          8 return type.__new__(meta, name, bases, class_dict)

    ValueError: Polygons need 3+ sides

- A simplified approach (since Python 3.6) simplifies the process with
  the `__init_subclass__` class dunder method
  - Allows the same behaviour without the need for a metaclass

``` python
class BetterPolygon:
    sides = None

    def __init_subclass__(cls):
        super().__init_subclass__()
        if cls.sides < 3:
            raise ValueError("Polygons need 3+ sides")

    @classmethod
    def interior_angles(cls):
        return (cls.sides - 2) * 180

class Hexagon(BetterPolygon):
    sides = 6

assert Hexagon.interior_angles() == 720

print("Before class definition")

class Point(BetterPolygon):
    sides = 1

print("After class definition")
```

    Before class definition

    ValueError: Polygons need 3+ sides
    ---------------------------------------------------------------------------
    ValueError                                Traceback (most recent call last)
    Cell In[3], line 20
         16 assert Hexagon.interior_angles() == 720
         18 print("Before class definition")
    ---> 20 class Point(BetterPolygon):
         21     sides = 1
         23 print("After class definition")

    Cell In[3], line 7, in BetterPolygon.__init_subclass__(cls)
          5 super().__init_subclass__()
          6 if cls.sides < 3:
    ----> 7     raise ValueError("Polygons need 3+ sides")

    ValueError: Polygons need 3+ sides

- Code is shorter and we don’t have a metaclass
- The behaviour is cleaner and easier to follow since we can access
  class variables directly rather than having to use the class
  dictionary

### Metaclasses and Multiple Inheritance

- Metaclasses have the limitation that each class can only have *one*
  metaclass
- E.g. if we wanted to have a `FilledRegion` that represents a coloured
  region
  - Might want to validate the colour
  - This may then be associated to a polygon but it’s not strictly one
- We could represent the basic idea with a metaclass
  - This works fine for a pure subclass of `Filled`
- If we try to define a class `BluePolygon` that is both a `Filled`
  subclass and a `Polygon` subclass we get an error
  - *Not* because `ValidateFilled` caught that blue was an invalid
    colour, but because of a conflict in the metaclass hierarchy
- The concept is that you can’t inherit from multiple disjoint
  metaclasses

``` python
class ValidateFilled(type):
    def __new__(meta, name, bases, class_dict):
        # Only validate subclasses of the filled class
        if bases:
            if class_dict["colour"] not in ("red", "green"):
                raise ValueError("Fill colour not supported")
        return type.__new__(meta, name, bases, class_dict)

class Filled(metaclass=ValidateFilled):
    colour = None # Must be specified by subclasses

print("Defining a colour region")
class RedRegion(Filled):
    colour = "red"

print(f"After definition: RedRegion colour is {RedRegion.colour}")

print("Attempting to define a coloured polygon")
# Previous polygon
# defining the metaclass
class ValidatePolygon(type):
    def __new__(meta, name, bases, class_dict):
        # Only validate subclasses of the Polygon class
        if bases:
            if class_dict["sides"] < 3:
                raise ValueError("Polygons need 3+ sides")
        return type.__new__(meta, name, bases, class_dict)

class Polygon(metaclass=ValidatePolygon):
    sides = None # Must be specified by subclasses

    @classmethod
    def interior_angle(cls):
        return (cls.sides - 2) * 180

print("Before BluePentagon definition, should fail because blue is not a valid colour")
class BluePentagon(Filled, Polygon):
    colour = "blue"
    sides = 5

print("After definition")
```

    Defining a colour region
    After definition: RedRegion colour is red
    Attempting to define a coloured polygon
    Before BluePentagon definition, should fail because blue is not a valid colour

    TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[4], line 37
         34         return (cls.sides - 2) * 180
         36 print("Before BluePentagon definition, should fail because blue is not a valid colour")
    ---> 37 class BluePentagon(Filled, Polygon):
         38     colour = "blue"
         39     sides = 5

    TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases

- We can fix this by creating a *metaclass hierarchy*
  - Use this to layer validation

``` python
class ValidatePolygon(type):
    def __new__(meta, name, bases, class_dict):
        # Only validate subclasses of the Polygon class
        if not class_dict.get("is_root"):
            if class_dict["sides"] < 3:
                raise ValueError("Polygons need 3+ sides")
        return type.__new__(meta, name, bases, class_dict)

class Polygon(metaclass=ValidatePolygon):
    is_root = True
    sides = None # Must be specified by subclass

class ValidateFilledPolygon(ValidatePolygon):
    def __new__(meta, name, bases, class_dict):
        # only validate non-root classes
        if not class_dict.get("is_root"):
            if class_dict["colour"] not in ("red", "green"):
                raise ValueError("Fill colour not supported")
        return super().__new__(meta, name, bases, class_dict)

class FilledPolygon(Polygon, metaclass=ValidateFilledPolygon):
    is_root = True
    colour = None # Must be specified by subclass

print("Defining a valid coloured polygon")
class GreenPolygon(FilledPolygon):
    colour = "green"
    sides = 5

greenie = GreenPolygon()
assert isinstance(greenie, Polygon)

print("Attempting to define an invalid colour for coloured polygon")
try:
    class OrangePolygon(FilledPolygon):
        colour = "orange"
        sides = 5
    print("Orange polygon is coloured", OrangePolygon.colour)
except ValueError as e:
    print("Failed to define OrangePolygon. Got exception:", e)

print("Attempting to define an invalid number of sides for polygon")
try:
    class RedLine(FilledPolygon):
        colour = "red"
        sides = 2
    print("Red polyon has", RedLine.sides, "sides")
except ValueError as e:
    print("Failed to define RedLine. Got exception:", e)
```

    Defining a valid coloured polygon
    Attempting to define an invalid colour for coloured polygon
    Failed to define OrangePolygon. Got exception: Fill colour not supported
    Attempting to define an invalid number of sides for polygon
    Failed to define RedLine. Got exception: Polygons need 3+ sides

- We’ve now broken composability (See [Item
  54](../../Chapter_07/Item_054/item_054.qmd))
- We no longer have a way to have a generic `Filled` region and separate
  validation
  - Again the solution is to use `__init_subclass__`
  - We can then inherit from both `Filled` and `BetterPolygon`
  - Validation logic runs via the `super().__init_subclass__` call

``` python
class Filled:
    colour = None # Must be specified by subclasses

    def __init_subclass__(cls):
        super().__init_subclass__()
        if cls.colour not in ("red", "green", "blue"):
            raise ValueError("Fills need a valid colour")

class Polygon:
    sides = None

    def __init_subclass__(cls):
        super().__init_subclass__()
        if cls.sides < 3:
            raise ValueError("Polygons need 3+ sides")

    @classmethod
    def interior_angles(cls):
        return (cls.sides - 2) * 180

class RedTriangle(Filled, Polygon):
    colour = "red"
    sides = 3

ruddy = RedTriangle()
assert isinstance(ruddy, Filled)
assert isinstance(ruddy, Polygon)

try:
    print("Before specifying class with wrong number of sides")
    class BlueLine:
        colour = "blue"
        sides = 2
    print("After class definition")
except ValueError as e:
    print("Failed to define BlueLine. Got exception", e)

try:
    print("Before specifying class with wrong colour")
    class BrownSquare:
        colour = "brown"
        sides = 4
    print("After class definition")
except ValueError as e:
    print("Failed to define BrownSquare. Got exception", e)
```

    Before specifying class with wrong number of sides
    After class definition
    Before specifying class with wrong colour
    After class definition

- `__init_subclass__` also works when dealing with multiple and diamond
  inheritance structures (See [Item
  53](../../Chapter_07/Item_053/item_053.qmd))

``` python
# A basic diamond hierarchy

class Top:
    def __init_subclass__(cls):
        super().__init_subclass__()
        print(f"Top for {cls}")

class Left(Top):
    def __init_subclass__(cls):
        super().__init_subclass__()
        print(f"Left for {cls}")

class Right(Top):
    def __init_subclass__(cls):
        super().__init_subclass__()
        print(f"Right for {cls}")

class Bottom(Left, Right):
    def __init_subclass__(cls):
        super().__init_subclass__()
        print(f"Bottom for {cls}")
```

    Top for <class '__main__.Left'>
    Top for <class '__main__.Right'>
    Top for <class '__main__.Bottom'>
    Right for <class '__main__.Bottom'>
    Left for <class '__main__.Bottom'>

- `Top.__init_subclass__` is only called a single time per class

## Things to Remember

- Metaclasses run the `__new__` method after a class statement’s body
  has been processed
- Metaclasses can inspect or modify a class after definition
  - Often overkill
- Use `__init_subclass__` to ensure well-formed subclasses at definition
  time
- Use `super().__init_subclass__` to ensure the correct method order
  resolution in class hierarchies
