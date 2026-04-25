# Item 61: Use `__getattr__`, `__getattribute__`, and `__setattr__` for

Lazy Attributes

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- `object` base class provides hooks for writing generic glue code
- For example, consider representing database records as objects
  - Assume an externally defined schema
  - Most languages require explicit mapping from the schema to objects
    and classes
  - Python let’s us perform this mapping generically at runtime
- Can’t do this with instance attributes, `@property` methods and
  descriptors
  - They need to defined at write time
- Instead use the `__getattr__` dunder method
  - If defined, called each time an attribute is not found on an object
    instance
- Here we define a class that lazy-loads attributes on their first
  access
  - Calling `__getattr__`; here by attempting to access `foo` mutates
    the instance `__dict__`

``` python
class LazyRecord:
    def __init__(self):
        self.exists = 5

    def __getattr__(self, name):
        value = f"Value for {name}"
        setattr(self, name, value)
        return value

data = LazyRecord()
print("Before:", data.__dict__)
print("foo:   ", data.foo)
print("After: ", data.__dict__)
```

    Before: {'exists': 5}
    foo:    Value for foo
    After:  {'exists': 5, 'foo': 'Value for foo'}

- Can add some debug `print` statements to highlight what’s going on

``` python
class LazyRecord:
    def __init__(self):
        self.exists = 5

    def __getattr__(self, name):
        value = f"Value for {name}"
        setattr(self, name, value)
        return value

class LoggingLazyRecord(LazyRecord):
    def __getattr__(self, name):
        print(f"Called __getattr__({name!r}), populating instance dictionary")
        result = super().__getattr__(name)
        print(f"Returning {result!r}")
        return result

data = LoggingLazyRecord()
print("exists:      ", data.exists)
print("First foo:   ", data.foo)
print("Second foo:  ", data.foo)
```

    exists:       5
    Called __getattr__('foo'), populating instance dictionary
    Returning 'Value for foo'
    First foo:    Value for foo
    Second foo:   Value for foo

- `exists` is present in instance dictionary so no call to `__getattr__`
- First call to `foo` can’t find it in the instance dictionary so
  `__getattr__` is called
- Second call to `foo` find’s it in the instance dictionary, so no
  further all to `__getattr__`
- `__getattr__` works great for lazy-loading schemaless data
  - Runs once to set up and load a property
  - Subsequent accesses go access the standard class instance
- Now consider supporting transactions
  - When a dynamic variable is accessed want to check if the record is
    valid and the transaction open
- `__getattr__` isn’t called each time because it goes via the
  dictionary for existing attributes
- Instead we have `__getattribute__`
  - Called *every* time an attribute is accessed
  - Including when it exists
- We could use this to check a global state on each access, e.g. a
  transaction

> [!CAUTION]
>
> Using `__getattribute__` to do complex operations on each attribute
> access can incur a significant performance overhead. As always
> consider and weigh up your options

- Here our basic validating implementation simply logs every attribute
  access

``` python
class ValidatingRecord:
    def __init__(self):
        self.exists = 5

    def __getattribute__(self, name):
        print(f"* Called __getattribute__({name!r})")
        try:
            value = super().__getattribute__(name)
            print(f"* Found {name!r}, returning {value!r}")
            return value
        except AttributeError:
            value = f"Value for {name}"
            print(f"* Setting {name!r} to {value!r}")
            setattr(self, name, value)
            return value

data = ValidatingRecord()
print("exists:      ", data.exists)
print("First foo:   ", data.foo)
print("Second foo:  ", data.foo)
```

    * Called __getattribute__('exists')
    * Found 'exists', returning 5
    exists:       5
    * Called __getattribute__('foo')
    * Setting 'foo' to 'Value for foo'
    First foo:    Value for foo
    * Called __getattribute__('foo')
    * Found 'foo', returning 'Value for foo'
    Second foo:   Value for foo

- Where the attribute shouldn’t exist we can raise an `AttributeError`
  - Causes standard python missing property behaviour for both
    `__getattr__` and `__getattribute__`

``` python
class MissingPropertyRecord:
    def __getattr__(self, name):
        if name == "bad_name":
            raise AttributeError(f"{name} is not allowed")

data = MissingPropertyRecord()
data.bad_name
```

    AttributeError: bad_name is not allowed
    ---------------------------------------------------------------------------
    AttributeError                            Traceback (most recent call last)
    Cell In[4], line 7
          4             raise AttributeError(f"{name} is not allowed")
          6 data = MissingPropertyRecord()
    ----> 7 data.bad_name

    Cell In[4], line 4, in MissingPropertyRecord.__getattr__(self, name)
          2 def __getattr__(self, name):
          3     if name == "bad_name":
    ----> 4         raise AttributeError(f"{name} is not allowed")

    AttributeError: bad_name is not allowed

- Python generic code often relies on using `hasattr` to verify the
  existence of an attribute then `getattr` to access it
  - Both are built-in functions
  - Both look in the instance dictionary then call `__getattr__`

``` python
class LazyRecord:
    def __init__(self):
        self.exists = 5

    def __getattr__(self, name):
        value = f"Value for {name}"
        setattr(self, name, value)
        return value

class LoggingLazyRecord(LazyRecord):
    def __getattr__(self, name):
        print(f"Called __getattr__({name!r}), populating instance dictionary")
        result = super().__getattr__(name)
        print(f"Returning {result!r}")
        return result

data = LoggingLazyRecord()
print("Before:          ", data.__dict__)
print("Has first foo:   ", hasattr(data, "foo"))
print("After:           ", data.__dict__)
print("Has second foo:  ", hasattr(data, "foo"))
```

    Before:           {'exists': 5}
    Called __getattr__('foo'), populating instance dictionary
    Returning 'Value for foo'
    Has first foo:    True
    After:            {'exists': 5, 'foo': 'Value for foo'}
    Has second foo:   True

- `hasattr` calls `__getattr__` the first time we attempt to access
  `foo`
- If the class instead implements `__getattribute__` this is called
  *every* time we use `hasattr` or `getattr`

``` python
class ValidatingRecord:
    def __init__(self):
        self.exists = 5

    def __getattribute__(self, name):
        print(f"* Called __getattribute__({name!r})")
        try:
            value = super().__getattribute__(name)
            print(f"* Found {name!r}, returning {value!r}")
            return value
        except AttributeError:
            value = f"Value for {name}"
            print(f"* Setting {name!r} to {value!r}")
            setattr(self, name, value)
            return value

data = ValidatingRecord()
print("Has first foo:   ", hasattr(data, "foo"))
print("Second foo:      ", hasattr(data, "foo"))
```

    * Called __getattribute__('foo')
    * Setting 'foo' to 'Value for foo'
    Has first foo:    True
    * Called __getattribute__('foo')
    * Found 'foo', returning 'Value for foo'
    Second foo:       True

- Now let’s say we want to implement lazy push-back to a database on
  attribute assignment
- We use the assignment analogue for `__getattr__`, `__setattr__`
  - Intercept’s arbitrary attribute assignments
- `__setattr__` is called every time an attribute is assigned
  - Hence no `__setattribute__` analogue
  - Also called by the `setattr` function
- We’ll define a basic `SavingRecord` and a `LoggingSavingRecord`
  variant

``` python
class SavingRecord:

    def __setattr__(self, name, value):
        # save some data for the record
        super().__setattr__(name, value)


class LoggingSavingRecord(SavingRecord):
    def __setattr__(self, name, value):
        print(f"* Called __setattr__({name!r}, {value!r})")
        super().__setattr__(name, value)

data = LoggingSavingRecord()
print("Before:  ", data.__dict__)
data.foo = 5
print("After:   ", data.__dict__)
data.foo = 7
print("Finally: ", data.__dict__)
```

    Before:   {}
    * Called __setattr__('foo', 5)
    After:    {'foo': 5}
    * Called __setattr__('foo', 7)
    Finally:  {'foo': 7}

- The downside to `__setattr__` and `__getattribute__` is that they are
  *always* called
  - In contrast to the downside of `__getattr__` which can only be
    called *once*
- Often we want somewhere in between
  - For example, might want attribute accesses to look up keys in an
    internal dictionary

``` python
class BrokenDictionaryRecord:
    def __init__(self, data):
        self._data = data
    def __getattribute__(self, name):
        return self._data[name]

data = BrokenDictionaryRecord({"foo": 3})
data.foo
```

    RecursionError: maximum recursion depth exceeded
    ---------------------------------------------------------------------------
    RecursionError                            Traceback (most recent call last)
    Cell In[8], line 8
          5         return self._data[name]
          7 data = BrokenDictionaryRecord({"foo": 3})
    ----> 8 data.foo

    Cell In[8], line 5, in BrokenDictionaryRecord.__getattribute__(self, name)
          4 def __getattribute__(self, name):
    ----> 5     return self._data[name]

    Cell In[8], line 5, in BrokenDictionaryRecord.__getattribute__(self, name)
          4 def __getattribute__(self, name):
    ----> 5     return self._data[name]

        [... skipping similar frames: BrokenDictionaryRecord.__getattribute__ at line 5 (2975 times)]

    Cell In[8], line 5, in BrokenDictionaryRecord.__getattribute__(self, name)
          4 def __getattribute__(self, name):
    ----> 5     return self._data[name]

    RecursionError: maximum recursion depth exceeded

- This causes an infinite recursion because each time `__getattribute__`
  accesses `self._data` it triggers a fresh call of `__getattribute__`
  - Solution is to defer to the `super().__getattribute__` invocation
    for the dictionary access
  - This avoids the recursion

``` python
class DictionaryRecord:
    def __init__(self, data):
        self._data = data

    def __getattribute__(self, name):
        print(f"* Called __getattribute__({name!r})")
        data_dict = super().__getattribute__("_data") # fetch self._data by super __getattribute__ to avoid recursion
        return data_dict[name]

data = DictionaryRecord({"foo": 3})
print("foo: ", data.foo)
```

    * Called __getattribute__('foo')
    foo:  3

- `__setattr__` methods modifying attributes should also use
  `super().__setattr__`

## Things to Remember

- Use `__getattr__` and `__setattr__` to lazily load and save attributes
  for objects
- `__getattr__` only gets called when accessing an attribute that
  doesn’t exist
- `__getattribute__` is called every time an attribute is accessed
- Avoid infinite recursion in `__getattribute__` and `__setattr__`
  implementations by calling `super().__getattribute__` and
  `super().__setattr__()` to access and set attributes
