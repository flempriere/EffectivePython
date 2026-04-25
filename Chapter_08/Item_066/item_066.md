# Item 66: Prefer Class Decorators over Metaclasses for Composable Class

Extensions

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- As seen metaclasses are powerful but also have their limitations (See
  [Item 62](../Item_062/item_062.qmd) and [Item
  63](../Item_063/item_063.qmd))
- Consider the case we want to decorate all methods of a class with some
  form of trace function
  - Should print all arguments, return values and any exceptions
- Naturally this can be implemented via decorator (See [Item
  38](../../Chapter_05/Item_038/item_038.qmd))

``` python
import functools

def trace_func(func):
    if hasattr(func, "tracing"): # Only decorate once
        return func

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = repr(args)
        kwargs_repr = repr(kwargs)
        result = None
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            result = e
            raise
        finally:
            print(
                f"{func.__name__}"
                f"({args_repr}, {kwargs_repr}) -> "
                f"{result!r}"
            )
    wrapper.tracing = True
    return wrapper
```

- We could then use this to create a version of a dictionary that
  provides a trace (See [Item
  58](../../Chapter_07/Item_057/item_057.qmd))

``` python
import functools

def trace_func(func):
    if hasattr(func, "tracing"): # Only decorate once
        return func

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = repr(args)
        kwargs_repr = repr(kwargs)
        result = None
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            result = e
            raise
        finally:
            print(
                f"{func.__name__}"
                f"({args_repr}, {kwargs_repr}) -> "
                f"{result!r}"
            )
    wrapper.tracing = True
    return wrapper

class TraceDict(dict):
    @trace_func
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    @trace_func
    def __setitem__(self, *args, **kwargs):
        return super().__setitem__(*args, **kwargs)

    @trace_func
    def __getitem__(self, *args, **kwargs):
        return super().__getitem__(*args, **kwargs)

trace_dict = TraceDict([("hi", 1)])
trace_dict["there"] = 2
trace_dict["hi"]

try:
    trace_dict["does not exist"]
except KeyError:
    pass # Expected
```

    __init__(({}, [('hi', 1)]), {}) -> None
    __setitem__(({'hi': 1}, 'there', 2), {}) -> None
    __getitem__(({'hi': 1, 'there': 2}, 'hi'), {}) -> 1
    __getitem__(({'hi': 1, 'there': 2}, 'does not exist'), {}) -> KeyError('does not exist')

- This approach requires us to explicitly wrap the methods we’re
  interested in
  - Which is obviously tedious and not great
- Since we don’t control `dict` if that class changes we’ll end up with
  more undecorated methods
- Automatic decoration can be achieved via a metaclass
  - We go through the classes attributes
  - We match those that are functions and not explicitly excluded
  - Wrap those in the decorator
  - Set this new wrapped method back onto the instance
- We can then declare the `TraceDict` with this metaclass

``` python
import functools
import types

def trace_func(func):
    if hasattr(func, "tracing"): #Only decorate once
        return func

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = repr(args)
        kwargs_repr = repr(kwargs)
        result = None
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            result = e
            raise
        finally:
            print(
                f"{func.__name__}"
                f"({args_repr}, {kwargs_repr}) -> "
                f"{result!r}"
            )
    wrapper.tracing = True
    return wrapper

TRACE_TYPES = (
    types.MethodType,
    types.FunctionType,
    types.BuiltinFunctionType,
    types.BuiltinMethodType,
    types.MethodDescriptorType,
    types.ClassMethodDescriptorType,
    types.WrapperDescriptorType,
)

IGNORE_METHODS = (
    "__repr__",
    "__str__",
)

class TraceMeta(type):
    def __new__(meta, name, bases, class_dict):
        klass = super().__new__(meta, name, bases, class_dict)

        for key in dir(klass):
            if key in IGNORE_METHODS:
                continue

            value = getattr(klass, key)
            if not isinstance(value, TRACE_TYPES):
                continue

            wrapped = trace_func(value)
            setattr(klass, key, wrapped)
        return klass

class TraceDict(dict, metaclass=TraceMeta):
    pass

trace_dict = TraceDict([("hi", 1)])
trace_dict["there"] = 2
trace_dict["hi"]

try:
    trace_dict["does not exist"]
except KeyError:
    pass # Expected
```

    __new__((<class '__main__.TraceDict'>, [('hi', 1)]), {}) -> {}
    __init__(({}, [('hi', 1)]), {}) -> None
    __setitem__(({'hi': 1}, 'there', 2), {}) -> None
    __getitem__(({'hi': 1, 'there': 2}, 'hi'), {}) -> 1
    __getitem__(({'hi': 1, 'there': 2}, 'does not exist'), {}) -> KeyError('does not exist')

- However, we’ll run back into the problem that we can’t use this
  approach with any class that already has a metaclass

``` python
class OtherMeta(type):
    pass

class SimpleDict(dict, metaclass=OtherMeta):
    pass

class ChildTraceDict(SimpleDict, metaclass=TraceMeta):
    pass
```

    TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[4], line 7
          4 class SimpleDict(dict, metaclass=OtherMeta):
          5     pass
    ----> 7 class ChildTraceDict(SimpleDict, metaclass=TraceMeta):
          8     pass

    TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases

- We could of course use metaclass inheritance, but we know this
  approach is brittle
  - i.e. the fix above we make `OtherMeta` inherit from `TraceMeta`

``` python
class OtherMeta(TraceMeta):
    pass

class SimpleDict(dict, metaclass=OtherMeta):
    pass

class ChildTraceDict(SimpleDict, metaclass=TraceMeta):
    pass
```

    __init_subclass__((), {}) -> None

- Obviously this solution doesn’t work in all cases
  1. We might not control the metaclass of the other class (especially
      if we want to apply a trace to a library class)
  2. Doesn’t let us compose multiple utility metaclasses
- Better approach is to use a *class decorator*
  - Work like a function decorator, but wrap a class
  - Applied with the `@decorator` syntax before a class declaration
- Function will modify or re-create the class
  - New version is then returned

``` python
def my_class_decorator(klass):
    klass.extra_param = "hello"
    return klass

@my_class_decorator
class MyClass:
    pass

print(MyClass)
print(MyClass.extra_param)
```

    <class '__main__.MyClass'>
    hello

- We can use class decorators to implement the automatic method
  decoration
  - Instead of a metaclass we just write a standalone function

``` python
import functools
import types

def trace_func(func):
    if hasattr(func, "tracing"): #Only decorate once
        return func

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = repr(args)
        kwargs_repr = repr(kwargs)
        result = None
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            result = e
            raise
        finally:
            print(
                f"{func.__name__}"
                f"({args_repr}, {kwargs_repr}) -> "
                f"{result!r}"
            )
    wrapper.tracing = True
    return wrapper

TRACE_TYPES = (
    types.MethodType,
    types.FunctionType,
    types.BuiltinFunctionType,
    types.BuiltinMethodType,
    types.MethodDescriptorType,
    types.ClassMethodDescriptorType,
    types.WrapperDescriptorType,
)

IGNORE_METHODS = (
    "__repr__",
    "__str__",
)

def trace(klass):
    for key in dir(klass):
        if key in IGNORE_METHODS:
            continue
        value = getattr(klass, key)
        if not isinstance(value, TRACE_TYPES):
            continue
        wrapped = trace_func(value)
        setattr(klass, key, wrapped)
    return klass

@trace
class TraceDict(dict):
    pass

trace_dict = TraceDict([("hi", 1)])
trace_dict["there"] = 2
trace_dict["hi"]

try:
    trace_dict["does not exist"]
except KeyError:
    pass # Expected
```

    __new__((<class '__main__.TraceDict'>, [('hi', 1)]), {}) -> {}
    __init__(({}, [('hi', 1)]), {}) -> None
    __setitem__(({'hi': 1}, 'there', 2), {}) -> None
    __getitem__(({'hi': 1, 'there': 2}, 'hi'), {}) -> 1
    __getitem__(({'hi': 1, 'there': 2}, 'does not exist'), {}) -> KeyError('does not exist')

- Class decorators also work when the class has a metaclass

``` python
class OtherMeta(type):
    pass

@trace
class MetaDict(dict, metaclass=OtherMeta):
    pass

trace_dict = MetaDict([("hi", 1)])
trace_dict["there"] = 2
trace_dict["hi"]

try:
    trace_dict["does not exist"]
except KeyError:
    pass # Expected
```

    __new__((<class '__main__.MetaDict'>, [('hi', 1)]), {}) -> {}
    __init__(({}, [('hi', 1)]), {}) -> None
    __setitem__(({'hi': 1}, 'there', 2), {}) -> None
    __getitem__(({'hi': 1, 'there': 2}, 'hi'), {}) -> 1
    __getitem__(({'hi': 1, 'there': 2}, 'does not exist'), {}) -> KeyError('does not exist')

- Class decorators are typically the best way to make composable
  extensions to classes

## Things to Remember

- A class decorator is a simple function that receives a class as a
  parameter and returns either a new class or a modification of the
  original class
- Class decorators let you modify every method or attribute of a class
  with minimal boilerplate
- Metaclasses can’t be composed
- Class Decorators can be used to extend classes without conflict
