# Item 65: Consider Class Body Definition Order to Between Relationships
Attributes


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Classes are often defined to represent external data
  - e.g. CSV data for freight deliveries
- CSV data can be read via the csv built-in library

``` python
import csv

with open("packages.csv") as f:
    for row in csv.reader(f):
        print(row)
```

    ['Sydney', ' Truck', ' 25']
    ['Melbourne', ' Boat', ' 6']
    ['Brisbane', ' Plane', ' 12']
    ['Perth', ' Road Train', ' 90']
    ['Adelaide', ' Truck', ' 17']

- We can wrap this in a nice class interface (See [Item
  52](../../Chapter_07/Item_052/item_052.qmd))

``` python
class Delivery:
    def __init__(self, destination, method, weight):
        self.destination = destination
        self.method = method
        self.weight = weight

    @classmethod
    def from_row(cls, row):
        return cls(row[0], row[1], row[2])

row = ["Sydney", "truck", "25"]
obj = Delivery.from_row(row)
print(obj.__dict__)
```

    {'destination': 'Sydney', 'method': 'truck', 'weight': '25'}

- Editing the CSV requires reformatting the class
  - e.g. if the columns are reordered, or new ones added
  - Have to change the `__init__` and the `from_row` functions
- What if we want to handle multiple CSV types
  - Have to consider
    1.  Different number of columns
    2.  Differently labelled columns
    3.  Different cell types
- Would like to reduce the repeated boilerplate of defining a new class
- Might consider an approach using a class attribute to map csv columns
  (in order) to attribute names (See [Item
  64](../Item_064/item_064.qmd))
  - Here the `RowMapper` class

``` python
class RowMapper:
    fields = () # Must be in CSV column order

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key not in type(self).fields:
                raise TypeError(f"Invalid field: {key}")
            setattr(self, key, value)

    @classmethod
    def from_row(cls, row):
        if len(row) != len(cls.fields):
            raise ValueError("Wrong number of fields")
        kwargs = dict(pair for pair in zip(cls.fields, row))
        return cls(**kwargs)

class DeliveryMapper(RowMapper):
    fields = ("destination", "method", "weight")

row = ["Sydney", "truck", "25"]
obj = DeliveryMapper.from_row(row)
assert obj.destination == "Sydney"
assert obj.method == "truck"
assert obj.weight == "25"
```

- Approach works but is not pythonic
  - Attributes are specified by strings not variable names
  - Hard to read
  - Unable to use static analysis tools
- `fields` is an additional layer of nesting
  - List of attributes as an attribute
- Would prefer to be able to write the fields in the class body as
  variable names, like

``` python
class MovingMapper:
    source = ...
    destination = ...
    square_feet = ...
```

- One approach would be to use a dataclass (See [Item
  51](../../Chapter_07/Item_051/item_051.qmd))
- Alternative is to combine three features
  1.  `__init_subclass__`
      - Let’s us run code at class definition (See [Item
        62](../Item_062/item_062.qmd))
  2.  Runtime introspection of attributes via the instance `__dict__`
      (See [Item 54](../../Chapter_07/Item_054/item_054.qmd))
  3.  Python dictionaries preserving insertion order of key-value pairs
      (See [Item 25](../../Chapter_04/Item_025/item_025.qmd))

``` python
class RowMapper:
    def __init_subclass__(cls):
        fields = []
        for key, value in cls.__dict__.items():
            if value is Ellipsis:
                fields.append(key)
        cls.fields = tuple(fields)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key not in type(self).fields:
                raise TypeError(f"Invalid field: {key}")
            setattr(self, key, value)

    @classmethod
    def from_row(cls, row):
        if len(row) != len(cls.fields):
            raise ValueError("Wrong number of fields")
        kwargs = dict(pair for pair in zip(cls.fields, row))
        return cls(**kwargs)

class DeliveryDriver(RowMapper):
    destination = ...
    method = ...
    weight = ...

row = ["Sydney", "truck", "25"]
obj = DeliveryDriver.from_row(row)
assert obj.destination == "Sydney"
assert obj.method == "truck"
assert obj.weight == "25"
```

- If order of columns change, then the attributes need to be reordered
  in the class definition
- Instead of Ellipsis, one could use descriptors
  - Let’s us perform attribute validation and data conversion (See [Item
    60](../Item_060/item_060.qmd))
  - For example, we might want to convert weight to a floating point
- We’ll define a generic field that performs a conversion on a value
  when `__set__` is called
  - Then provide two concrete implementations
    1.  `StringField` for handling strings
    2.  `FloatField` for floating point numbers

``` python
class Field:
    def __init__(self):
        self.internal_name = None

    def __set_name__(self, owner, column_name):
        self.internal_name = "_" + column_name

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return getattr(instance, self.internal_name, "")

    def __set__(self, instance, value):
        converted_value = self.convert(value)
        setattr(instance, self.internal_name, converted_value)

    def convert(self, value):
        raise NotImplementedError

class StringField(Field):
    def convert(self, value):
        if not isinstance(value, str):
            raise ValueError("value is not a str")
        return value

class FloatField(Field):
    def convert(self, value):
        return float(value)


class RowMapper:
    def __init_subclass__(cls):
        fields = []
        for key, value in cls.__dict__.items():
            if isinstance(value, Field): #changed
                fields.append(key)
        cls.fields = tuple(fields)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key not in type(self).fields:
                raise TypeError(f"Invalid field: {key}")
            setattr(self, key, value)

    @classmethod
    def from_row(cls, row):
        if len(row) != len(cls.fields):
            raise ValueError(f"Wrong number of fields")
        kwargs = dict(pair for pair in zip(cls.fields, row))
        return cls(**kwargs)

class DeliveryDriver(RowMapper):
    destination = StringField()
    method = StringField()
    weight = FloatField()

row = ["Sydney", "truck", "25"]
obj = DeliveryDriver.from_row(row)
assert obj.destination == "Sydney"
assert obj.method == "truck"
assert obj.weight == 25.0 # number not string
```

- Can also use class attribute inspection to identify methods
- For example, now consider we want to describe a sequential workflow
  - Methods are executed in their order of definition

``` python
class HypotheticalWorkflow:
    def start_engine(self):
        ...
    def release_brake(self):
        ...
    def run(self):
        start_engine()
        release_brake()
```

- Want to implement this such that `run` implicitly knows the order
  rather than having to code it in
- An approach is to use a decorator (See [Item
  38](../../Chapter_05/Item_038/item_038.qmd))
  - Use it to indicate with methods should be executed by `run`

``` python
def step(func):
    func._is_step = True
    return func
```

- Want a base class that introspects for callables (See [Item
  48](../../Chapter_07/Item_048/item_048.qmd))
  - Then incorporate those with the `_is_step` attribute into the
    workflow
  - `run` then simply has to iterate through the created dictionary and
    call the functions

``` python
def step(func):
    func._is_step = True
    return func

class Workflow:
    def __init_subclass__(cls):
        steps = []
        for key, value in cls.__dict__.items():
            if callable(value) and hasattr(value, "_is_step"):
                steps.append(key)
        cls.steps = tuple(steps)

    def run(self):
        for step_name in type(self).steps:
            func = getattr(self, step_name)
            func()
```

- Putting this all together
  - We create a simple workflow
  - We define three methods `start_engine`, `my_helper_function`,
    `release_brake`
    - We only wrap the first and last methods, the middle should then
      not be incorporated into the workflow

``` python
def step(func):
    func._is_step = True
    return func

class Workflow:
    def __init_subclass__(cls):
        steps = []
        for key, value in cls.__dict__.items():
            if callable(value) and hasattr(value, "_is_step"):
                steps.append(key)
        cls.steps = tuple(steps)

    def run(self):
        for step_name in type(self).steps:
            func = getattr(self, step_name)
            func()

class StartCar(Workflow):
    @step
    def start_engine(self):
        print("Engine is on!")

    def my_helper_function(self):
        print("Should not be called")

    @step
    def release_brake(self):
        print("Brake is off!")

workflow = StartCar()
workflow.run()
```

    Engine is on!
    Brake is off!

## Things to Remember

- Can examine the attributes and methods defined in a class body at
  runtime via the class instance’s `__dict__` dictionary
- Definition order of class bodies is preserved for the `__dict__`
  - Lets us write code that considers relative positions of attributes
  - Useful for mapping relational data to object fields
- Descriptors and method decorators can be used to provide additional
  definition order execution
