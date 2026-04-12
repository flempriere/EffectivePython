# Item 32: Prefer Raising Exceptions to Returning `None`


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Python provides the value `None` to indicate the absence of a value
- A common idiom is to return this value from a function when an invalid
  state is reached
  - e.g. when attempting to divide by zero

``` python
def careful_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None

x, y = 1, 0
result = careful_divide(x, y)
if result is None:
    print("Invalid inputs")
```

    Invalid inputs

- Above has the issue that if the numerator is zero, but the denominator
  is not then it returns zero
- This means that if someone tries to check for `None` by using a
  falsely comparison then valid results which return $0$ are erroneously
  flagged as errors

``` python
def careful_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None

x, y = 0, 5
result = careful_divide(x, y)
if not result:
    print("Invalid inputs") # run's even though 0/5 is valid
```

    Invalid inputs

- Two approaches to fixing this issue

  1.  Split return into a 2-tuple
      - First part indicates if operation succeeded
      - Second part returns the computed result
      - Problem with this approach is the caller can easily ignore the
        first part
        - i.e. It does not enforce correctness
  2.  Never return `None` but rather use exceptions to indicate errors
      - Raise an exception
      - Caller must handle the exception else the program crashes
      - For example we could convert the `ZeroDivisionError` into a more
        generic `ValueError`

``` python
# First approach - error tuple

def careful_divide(a, b):
    try:
        return True, a / b
    except ZeroDivisionError:
        return False, None


# Caller can still write the same faulty code
# Correct usage:

x, y = 0, 5
success, result = careful_divide(x, y)
if not success:
    print("Invalid inputs")

# Incorrect usage:
_, result = careful_divide(x, y)
if not result:
    print("Invalid inputs")
```

    Invalid inputs

``` python
# Second approach - Raising an exception for the caller to handle

def careful_divide(x, y):
    try:
        return a / b
    except ZeroDivisionError:
        raise ValueError("invalid inputs")

x, y = 0, 5
try:
    result = careful_divide(x, y)
except ValueError:
    print("Invalid Inputs")
else:
    print(f"Result is {result:.1f}")
```

    NameError: name 'a' is not defined
    ---------------------------------------------------------------------------
    NameError                                 Traceback (most recent call last)
    Cell In[4], line 11
          9 x, y = 0, 5
         10 try:
    ---> 11     result = careful_divide(x, y)
         12 except ValueError:
         13     print("Invalid Inputs")

    Cell In[4], line 5, in careful_divide(x, y)
          3 def careful_divide(x, y):
          4     try:
    ----> 5         return a / b
          6     except ZeroDivisionError:
          7         raise ValueError("invalid inputs")

    NameError: name 'a' is not defined

- Using exceptions also helps with type checking
- We can write more specific return signatures if we don’t also have
  include `None`
  - Unfortunately python’s type system doesn’t let us indicate the
    exceptions a function raises
  - So we have to document them

``` python
# Complete example using exceptions and type signatures

def careful_divide(a: float, b: float) -> float:
    """
    Divides a by b

    Parameters
    ----------
    a : float
        numerator
    b : float
        denominator, should be non-zero

    Returns
    -------
    float
        `a / b`

    Raises
    ------
    ValueError
        Raised if `a` cannot be divided by `b`
    """

try:
    result = careful_divide(1, 0)
except ValueError:
    print("Invalid inputs")
else:
    print(f"Result is {result:.1f}")
```

    TypeError: unsupported format string passed to NoneType.__format__
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[5], line 30
         28     print("Invalid inputs")
         29 else:
    ---> 30     print(f"Result is {result:.1f}")

    TypeError: unsupported format string passed to NoneType.__format__

## Things to Remember

- Functions returning `None` to indicate errors are failure prone
  - Many valid values such as zero, `False` and `""` evaluate `False`
    which may be confused with a `None` value
- Raise exceptions to indicate special situations instead of returning
  - This forces the caller to handle them
  - Document the exception behaviour so the caller can handle it
    correctly
- Type annotations can be used to be clear about the range of valid
  returned values
