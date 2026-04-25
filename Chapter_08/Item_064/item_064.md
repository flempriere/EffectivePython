# Item 64: Annotate Class Attributes with `__set_name__`

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Metaclasses (See [Item 62](../Item_062/item_062.qmd)) let you modify
  and annotate properties after class definition
  - Still prior to first use
- Common pattern when combined with descriptors (See [Item
  60](../Item_060/item_060.qmd))
  - Enables the addition of introspection tools
- For example, might want to define a class representing database rows
  - Want a property for each column in the database
  - Start by defining a descriptor

``` python
class Field:
    def __init__(self, column_name):
        self.column_name = column_name
        self.internal_name = "_" + self.column_name

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return getattr(instance, self.internal_name, "")

    def __set__(self, instance, value):
        setattr(instance, self.internal_name, value)
```

- `column_name` lets us write all the columns as protected instance
  variables
- Can then use `__set__` and `__get__` to defer to `setattr` and
  `getattr` to load and access state (See [Item
  64](../Item_061/item_061.qmd))
- Can then define a class
  - The class has to supply the row names

``` python
class Field:
    def __init__(self, column_name):
        self.column_name = column_name
        self.internal_name = "_" + self.column_name

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return getattr(instance, self.internal_name, "")

    def __set__(self, instance, value):
        setattr(instance, self.internal_name, value)

class Customer:
    first_name = Field("first_name")
    last_name = Field("last_name")
    prefix = Field("prefix")
    suffix = Field("suffix")

customer = Customer()
print(f"Before: {customer.first_name!r} {customer.__dict__}")
customer.first_name = "Euclid"
print(f"After: {customer.first_name!r} {customer.__dict__}")
```

    Before: '' {}
    After: 'Euclid' {'_first_name': 'Euclid'}

- As shown above the usage is simple
  - `Field` attributes modify the `__dict__` as required
- However we have some redundancy
  - We declare the field name twice
    1. On the left as a class variable
    2. In the `Field` constructor
- Would be nice to write it *once*, **but** the order of evaluation is
  the opposite of how it reads
  1. `Field` constructor is called as `Field("first_name")`
  2. Value is returned and assigned to `Customer.first_name`
- A `Field` instance can’t know upfront what attribute it’s being
  assigned to
- We can use a metaclass to eliminate this redundancy
  - e.g. To assign `Field.column_name` and `Field.internal_name` on the
    descriptor to the class
- Our base class is then a naked class to set the metaclass
  (`DatabaseRow`)
- The `Field` descriptor no longer requires arguments for it’s
  constructor
  - Attributes are then set by `Meta.__new__`
- `Customer` now no longer needs to define the `Field` names

``` python
class Meta(type):
    def __new__(meta, name, bases, class_dict):
        for key, value in class_dict.items():
            if isinstance(value, Field):
                value.column_name = key
                value.internal_name = "_" + key
        cls = type.__new__(meta, name, bases, class_dict)
        return cls

class DatabaseRow(metaclass=Meta):
    pass

class Field:
    def __init__(self):
        # these are set by the metaclass
        self.column_name = None
        self.internal_name = None

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return getattr(instance, self.internal_name, "")

    def __set__(self, instance, value):
        setattr(instance, self.internal_name, value)

class Customer(DatabaseRow):
    first_name = Field()
    last_name = Field()
    prefix = Field()
    suffix = Field()

customer = Customer()
print(f"Before: {customer.first_name!r} {customer.__dict__}")
customer.first_name = "Euclid"
print(f"After: {customer.first_name!r} {customer.__dict__}")
```

    Before: '' {}
    After: 'Euclid' {'_first_name': 'Euclid'}

- This approach couples the `Field` implementation to `DatabaseRow` (or
  actually the metaclass)
- `Field` breaks if the metaclass doesn’t exist to properly set it’s
  values

``` python
# attempting to use field with the metaclass derivation

class Field:
    def __init__(self):
        # these are set by the metaclass
        self.column_name = None
        self.internal_name = None

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return getattr(instance, self.internal_name, "")

    def __set__(self, instance, value):
        setattr(instance, self.internal_name, value)

class Customer:
    first_name = Field()
    last_name = Field()
    prefix = Field()
    suffix = Field()

customer = Customer()
print(f"Before: {customer.first_name!r} {customer.__dict__}")
customer.first_name = "Euclid"
print(f"After: {customer.first_name!r} {customer.__dict__}")
```

    TypeError: attribute name must be string, not 'NoneType'
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[4], line 24
         21     suffix = Field()
         23 customer = Customer()
    ---> 24 print(f"Before: {customer.first_name!r} {customer.__dict__}")
         25 customer.first_name = "Euclid"
         26 print(f"After: {customer.first_name!r} {customer.__dict__}")

    Cell In[4], line 12, in Field.__get__(self, instance, instance_type)
         10 if instance is None:
         11     return self
    ---> 12 return getattr(instance, self.internal_name, "")

    TypeError: attribute name must be string, not 'NoneType'

- Instead if we have Python 3.6 or newer we can use the `__set_name__`
  dunder method on Descriptors
  - Called on every descriptor instance when the containing class is
    defined
  - Receives the owning class and the attribute name being assigned to
- This let’s us avoid the need for a metaclass entirely

``` python
# attempting to use field with the metaclass derivation

class Field:
    def __init__(self):
        # these are set by the metaclass
        self.column_name = None
        self.internal_name = None

    def __set_name__(self, owner, column_name):
        self.column_name = column_name
        self.internal_name = "_" + column_name

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return getattr(instance, self.internal_name, "")

    def __set__(self, instance, value):
        setattr(instance, self.internal_name, value)

# No need to inherit
class Customer:
    first_name = Field()
    last_name = Field()
    prefix = Field()
    suffix = Field()

customer = Customer()
print(f"Before: {customer.first_name!r} {customer.__dict__}")
customer.first_name = "Euclid"
print(f"After: {customer.first_name!r} {customer.__dict__}")
```

    Before: '' {}
    After: 'Euclid' {'_first_name': 'Euclid'}

## Things to Remember

- Using a metaclass lets you modify class attributes before the class is
  fully defined
- Descriptors and metaclasses can be paired to provide declarative
  behaviour and runtime introspection
- Define `__set_name__` on descriptor classes
  - Let’s them take into account their containing classes and property
    names
