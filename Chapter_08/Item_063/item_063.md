# Item 63: Register Class Existence with `__init_subclass__`


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Metaclasses (See [Item 62](../Item_062/item_062.qmd)) can be used to
  automatically register types
- Useful for reverse lookups
  - Mapping an identifier back to a class
- For example, implementing JSON serialisation
  - Need a way to map an object to a JSON string
- Might do this generically via a base class
  - Records constructor parameters
  - Creates a JSON dictionary (See [Item
    54](../../Chapter_07/Item_054/item_054.qmd) for a mix-in approach)

``` python
import json

class Serialisable:
    def __init__(self, *args):
        self.args = args

    def serialise(self):
        return json.dumps({"args": self.args})
```

- Can then inherit to create serializable classes

``` python
import json

class Serializable:
    def __init__(self, *args):
        self.args = args

    def serialize(self):
        return json.dumps({"args": self.args})

class Point2D(Serializable):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point2D({self.x}, {self.y})"

point = Point2D(5, 3)
print("Object:      ", point)
print("Serialized:  ", point.serialize())
```

    Object:       Point2D(5, 3)
    Serialized:   {"args": [5, 3]}

- We have to pair this with a deserializer
  - Define a class that can deserialize a given parent class

``` python
import json

class Serializable:
    def __init__(self, *args):
        self.args = args

    def serialize(self):
        return json.dumps({"args": self.args})

class Deserializable(Serializable):

    @classmethod
    def deserialize(cls, json_data):
        params = json.loads(json_data)
        return cls(*params["args"])

class Point2D(Deserializable):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point2D({self.x}, {self.y})"

before = Point2D(5, 3)
print("Before:      ", before)
data = before.serialize()
print("Serialized:  ", data)
after = Point2D.deserialize(data)
print("After:   ", after)
```

    Before:       Point2D(5, 3)
    Serialized:   {"args": [5, 3]}
    After:    Point2D(5, 3)

- Approach above requires us to know ahead of time the type of the
  deserialized data

  - i.e. need to know we have a `Point2D`

- Would like to have a series of serializable classes and one function
  for serialization and deserialization (See [Item
  50](../../Chapter_07/Item_050/item_050.qmd))

- Could include the class name in the JSON

- Use this to key a registry of constructors to deserialize the data

  - This approach requires us to register classes for deserialization
  - If we forget, then attempting to deserialize the class will break

``` python
import json

class Serializable:
    def __init__(self, *args):
        self.args = args

    def serialize(self):
        return json.dumps(
            {
                "class": self.__class__.__name__,
                "args": self.args
            }
        )

    def __repr__(self):
        name = self.__class__.__name__
        args_str = ", ".join(str(x) for x in self.args)
        return f"{name}(args_str)"

REGISTRY = {}

def register_class(target_class):
    REGISTRY[target_class.__name__] = target_class

def deserialize(data):
    params = json.loads(data)
    name = params["class"]
    target_class = REGISTRY[name]
    return target_class(*params["args"])

class Point2D(Serializable):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point2D({self.x}, {self.y})"

# have to register a class for deserialization
register_class(Point2D)

before = Point2D(5, 3)
print("Before:      ", before)
data = before.serialize()
print("Serialized:  ", data)
after = deserialize(data)
print("After:   ", after)

# forgetting to register a class
class Point3D(Serializable):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"Point3D({self.x}, {self.y}, {self.z})"

before = Point3D(5, -9, 4)
print("Before:      ", before)
data = before.serialize()
print("Serialized:  ", data)
after = deserialize(data)
print("After:   ", after)
```

    Before:       Point2D(5, 3)
    Serialized:   {"class": "Point2D", "args": [5, 3]}
    After:    Point2D(5, 3)
    Before:       Point3D(5, -9, 4)
    Serialized:   {"class": "Point3D", "args": [5, -9, 4]}

    KeyError: 'Point3D'
    ---------------------------------------------------------------------------
    KeyError                                  Traceback (most recent call last)
    Cell In[4], line 65
         63 data = before.serialize()
         64 print("Serialized:  ", data)
    ---> 65 after = deserialize(data)
         66 print("After:   ", after)

    Cell In[4], line 28, in deserialize(data)
         26 params = json.loads(data)
         27 name = params["class"]
    ---> 28 target_class = REGISTRY[name]
         29 return target_class(*params["args"])

    KeyError: 'Point3D'

- The reliance on registering classes is hard to follow and difficult to
  debug if the pattern isn’t familiar
  - The code to register is distinct from the class implementation
  - Not immediately obvious what the error is to someone creating a new
    class
- We might try a similar approach with *class decorators* (See [Item
  66](../Item_066/item_066.qmd))
  - Again vulnerable to someone forgetting to put them there
- Would be good to *automatically* register a class for deserialization
  when we define it *automatically*
  - Can be achieved via a metaclass
- For example, below defines a new metaclass to automatically register a
  class for deserialization

``` python
import json

REGISTRY = {}

def register_class(target_class):
    REGISTRY[target_class.__name__] = target_class

def deserialize(data):
    params = json.loads(data)
    name = params["class"]
    target_class = REGISTRY[name]
    return target_class(*params["args"])

class Meta(type):
    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        register_class(cls)
        return cls

class Serializable(metaclass=Meta):
    def __init__(self, *args):
        self.args = args

    def serialize(self):
        return json.dumps(
            {
                "class": self.__class__.__name__,
                "args": self.args
            }
        )

    def __repr__(self):
        name = self.__class__.__name__
        args_str = ", ".join(str(x) for x in self.args)
        return f"{name}(args_str)"

# No longer have to register classes
class Point2D(Serializable):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point2D({self.x}, {self.y})"

before = Point2D(5, 3)
print("Before:      ", before)
data = before.serialize()
print("Serialized:  ", data)
after = deserialize(data)
print("After:   ", after)

class Point3D(Serializable):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"Point3D({self.x}, {self.y}, {self.z})"

before = Point3D(5, -9, 4)
print("Before:      ", before)
data = before.serialize()
print("Serialized:  ", data)
after = deserialize(data)
print("After:   ", after)
```

    Before:       Point2D(5, 3)
    Serialized:   {"class": "Point2D", "args": [5, 3]}
    After:    Point2D(5, 3)
    Before:       Point3D(5, -9, 4)
    Serialized:   {"class": "Point3D", "args": [5, -9, 4]}
    After:    Point3D(5, -9, 4)

- We’ve already seen that there are issues with using metaclasses
- We’ll instead use `__init_subclass__` class dunder method
  - Again, available from Python 3.6 onwards
  - Reduces the boilerplate associated with metaclasses

``` python
import json

REGISTRY = {}

def register_class(target_class):
    REGISTRY[target_class.__name__] = target_class

def deserialize(data):
    params = json.loads(data)
    name = params["class"]
    target_class = REGISTRY[name]
    return target_class(*params["args"])

class Serializable:
    def __init__(self, *args):
        self.args = args

    def __init_subclass__(cls):
        super().__init_subclass__()
        register_class(cls)

    def serialize(self):
        return json.dumps(
            {
                "class": self.__class__.__name__,
                "args": self.args
            }
        )

    def __repr__(self):
        name = self.__class__.__name__
        args_str = ", ".join(str(x) for x in self.args)
        return f"{name}(args_str)"

# No longer have to register classes
class Point2D(Serializable):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point2D({self.x}, {self.y})"

before = Point2D(5, 3)
print("Before:      ", before)
data = before.serialize()
print("Serialized:  ", data)
after = deserialize(data)
print("After:   ", after)

class Point3D(Serializable):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"Point3D({self.x}, {self.y}, {self.z})"

before = Point3D(5, -9, 4)
print("Before:      ", before)
data = before.serialize()
print("Serialized:  ", data)
after = deserialize(data)
print("After:   ", after)
```

    Before:       Point2D(5, 3)
    Serialized:   {"class": "Point2D", "args": [5, 3]}
    After:    Point2D(5, 3)
    Before:       Point3D(5, -9, 4)
    Serialized:   {"class": "Point3D", "args": [5, -9, 4]}
    After:    Point3D(5, -9, 4)

- `__init_subclass__` or a metaclass ensures that class registration is
  enforced
  - Requires the correct inheritance tree
- Natural fit for serialization, database object-relational mappings,
  plugins and callback hooks

## Things to Remember

- Class registration is a helpful pattern for building modular python
  programs
- Metaclasses let you intercept and run registration code whenever a
  base class is subclassed
- Using metaclasses for registration avoids errors associating with
  improper use
- Prefer `__init_subclass__` over metaclass machinery
  - Cleaner and easier to understand
  - Works better with multiple inheritance
