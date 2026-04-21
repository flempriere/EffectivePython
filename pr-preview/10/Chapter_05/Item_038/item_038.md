# Item 38: Define Function Decorators with `functools.wrap`


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Decorators are a special syntax for wrapping a function in additional
  code
- Decorators can run code before and after the call to the wrapped
  function
- Can thus
  - Access and modify input arguments
  - Access and modify return values
  - Access and modify raised exceptions
- Useful for
  - Enforcing semantics
  - Debugging
  - Registering functions
  - More…
- E.g. let’s say we want a simple debugging utility to print the
  arguments and return values of a function call
  - We define it using `*args` and `**kwargs`

``` python
def trace(func):
    def wrapper(*args, **kwargs):
        args_repr = repr(args)
        kwargs_repr = repr(kwargs)
        result = func(*args, **kwargs)
        print(f"{func.__name__}({args_repr}, {kwargs_repr}) -> {result!r}")
        return result
    return wrapper
```

- Can then apply the decorator, using the `@` symbol

``` python
def trace(func):
    def wrapper(*args, **kwargs):
        args_repr = repr(args)
        kwargs_repr = repr(kwargs)
        result = func(*args, **kwargs)
        print(f"{func.__name__}({args_repr}, {kwargs_repr}) -> {result!r}")
        return result
    return wrapper

@trace
def fibonacci(n):
    """
    Calculate the n-th Fibonacci number (Assumng F_0 = 0, F_1 = 1)

    Parameters
    ----------
    n : int
        positive integer giving the index of the desired fibonacci number

    Returns
    -------
    int
        The `n`-th fibonacci number
    """

    if n in (0, 1):
        return n
    return fibonacci(n - 2) + fibonacci(n - 1)

fibonacci(4)
```

    fibonacci((0,), {}) -> 0
    fibonacci((1,), {}) -> 1
    fibonacci((2,), {}) -> 1
    fibonacci((1,), {}) -> 1
    fibonacci((0,), {}) -> 0
    fibonacci((1,), {}) -> 1
    fibonacci((2,), {}) -> 1
    fibonacci((3,), {}) -> 2
    fibonacci((4,), {}) -> 3

    3

- Calling the `@` is equivalent to the following

``` python
fibonacci = trace(fibonacci)
```

- i.e. we effectively realias `fibonacci` as with the call wrapped by
  `trace`
- Decorate function runs the wrapper code before and after `fibonacci`
  runs
- Works well
  - But minor side-effect
  - Value returned by the decorator doesn’t recognise it’s name as
    `fibonacci`
  - Instead it is the wrapper function defined in `trace`
  - This causes issues with introspection tools like debuggers
  - e.g. `help` can no longer look up the correct docstring

``` python
def trace(func):
    def wrapper(*args, **kwargs):
        args_repr = repr(args)
        kwargs_repr = repr(kwargs)
        result = func(*args, **kwargs)
        print(f"{func.__name__}({args_repr}, {kwargs_repr}) -> {result!r}")
        return result
    return wrapper

@trace
def fibonacci(n):
    """
    Calculate the n-th Fibonacci number (Assumng F_0 = 0, F_1 = 1)

    Parameters
    ----------
    n : int
        positive integer giving the index of the desired fibonacci number

    Returns
    -------
    int
        The `n`-th fibonacci number
    """

    if n in (0, 1):
        return n
    return fibonacci(n - 2) + fibonacci(n - 1)

print(fibonacci)
help(fibonacci)
```

    <function trace.<locals>.wrapper at 0x7f607810f950>
    Help on function wrapper in module __main__:

    wrapper(*args, **kwargs)

- Object serializers also break since they can no longer locate the
  original function

``` python
import pickle

def trace(func):
    def wrapper(*args, **kwargs):
        args_repr = repr(args)
        kwargs_repr = repr(kwargs)
        result = func(*args, **kwargs)
        print(f"{func.__name__}({args_repr}, {kwargs_repr}) -> {result!r}")
        return result
    return wrapper

@trace
def fibonacci(n):
    """
    Calculate the n-th Fibonacci number (Assumng F_0 = 0, F_1 = 1)

    Parameters
    ----------
    n : int
        positive integer giving the index of the desired fibonacci number

    Returns
    -------
    int
        The `n`-th fibonacci number
    """

    if n in (0, 1):
        return n
    return fibonacci(n - 2) + fibonacci(n - 1)

pickle.dumps(fibonacci)
```

    PicklingError: Can't pickle local object <function trace.<locals>.wrapper at 0x7f6078124a90>
    ---------------------------------------------------------------------------
    PicklingError                             Traceback (most recent call last)
    Cell In[4], line 32
         29         return n
         30     return fibonacci(n - 2) + fibonacci(n - 1)
    ---> 32 pickle.dumps(fibonacci)

    PicklingError: Can't pickle local object <function trace.<locals>.wrapper at 0x7f6078124a90>

- `functools` provides the `wraps` helper function
- Acts as a decorator for writing decorators
- Copies all inner metadata from a wrapped function to the other
  wrapping function
- For example we can rewrite our `trace` function

``` python
from functools import wraps
import pickle

def trace(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = repr(args)
        kwargs_repr = repr(kwargs)
        result = func(*args, **kwargs)
        print(f"{func.__name__}({args_repr}, {kwargs_repr}) -> {result!r}")
        return result
    return wrapper

@trace
def fibonacci(n):
    """
    Calculate the n-th Fibonacci number (Assumng F_0 = 0, F_1 = 1)

    Parameters
    ----------
    n : int
        positive integer giving the index of the desired fibonacci number

    Returns
    -------
    int
        The `n`-th fibonacci number
    """

    if n in (0, 1):
        return n
    return fibonacci(n - 2) + fibonacci(n - 1)

help(fibonacci)
print(pickle.dumps(fibonacci))
```

    Help on function fibonacci in module __main__:

    fibonacci(n)
        Calculate the n-th Fibonacci number (Assumng F_0 = 0, F_1 = 1)

        Parameters
        ----------
        n : int
            positive integer giving the index of the desired fibonacci number

        Returns
        -------
        int
            The `n`-th fibonacci number

    b'\x80\x05\x95\x1a\x00\x00\x00\x00\x00\x00\x00\x8c\x08__main__\x94\x8c\tfibonacci\x94\x93\x94.'

- In general `wraps` ensures that Python functions standard attributes
  are preserved
  - Ensures correct behaviour

## Things to Remember

- Python supports the decorator syntax
  - Allows a function to modify another function at runtime
- Using decorators can cause strange bugs in introspection tools like
  debuggers, serializers and help
- Use the `wraps` decorator from the `functools` built-in when defining
  your own decorators to ensure they’re implemented correctly
