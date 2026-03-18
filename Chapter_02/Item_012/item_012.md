# Understand the Difference Between `repr` and `str` when Printing

Objects

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- `print` statement style debugging refers to debugging via format
  strings or `logging`
  - Tend’s to get you pretty far
  - Consider a proper debugger for more complicated issues
- Python object internals are typically public and accessible via
  attributes
- `print` returns a human readable string
  - Can be customised via formatting (see [Item
    11](../Item_011/item_011.qmd))
  - For example `print` called with a string displays the string without
    quotes

``` python
print("foo bar")
```

    foo bar

- There are many ways to modify happens when a variable get’s passed to
  `print`

- Here all the following are equivalent to the above

  1. Calling `str` on the variable, then `print` on the result
  2. Using the `%s` format specifier with the `%` operator
  3. The default f-string formatting i.e. `f"{"foo bar"}"`
  4. Calling the `format` built-in
  5. Calling the `__format__` dunder method
  6. Calling the `__str__` dunder method

``` python
foo = "foo bar"
print(str(foo))
print("%s" % foo)
print(f"{foo}")
print(format(foo))
print(foo.__format__())
print(foo.__str__())
```

    foo bar
    foo bar
    foo bar
    foo bar

    TypeError: str.__format__() takes exactly one argument (0 given)
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[2], line 6
          4 print(f"{foo}")
          5 print(format(foo))
    ----> 6 print(foo.__format__())
          7 print(foo.__str__())

    TypeError: str.__format__() takes exactly one argument (0 given)

- Human readable string doesn’t strictly mean the most expressive about
  what the actual variable *is*
- e.g. The integer `5` and the string `"5"` have the same output,
  despite being incompatible types

``` python
int_five = 5
str_five = "5"

print(int_five)
print(str_five)
print(f"Is {int_five} == {str_five}? {int_five == str_five}")
```

    5
    5
    Is 5 == 5? False

- While debugging typically want the type information to be clear
  - This is normally the `repr` string
- `repr` built-in returns the *printable representation* on an object
  - For many built-in types this is also a valid python expression
  - i.e we can `eval` it to get the object back

``` python
# repr of a byte string

a = "\x07"
print(repr(a))

b = eval(repr(a))
print(b)
assert a == b
```

    '\x07'
    

- When debugging explicitly call `repr` to ensure type information is
  conveyed
  - `%r` format specifier (`%` operator) or `!r` format specifier
    (`format` / F-string) is a shorthand for `repr`

``` python
int_five = 5
str_five = "5"
print(repr(int_five))
print(repr(str_five))

# using repr format specifiers

print("Is %r == %r?" % (int_five, str_five))
print(f"Is {int_value!r} == {str_value!r}?")
```

    5
    '5'
    Is 5 == '5'?

    NameError: name 'int_value' is not defined
    ---------------------------------------------------------------------------
    NameError                                 Traceback (most recent call last)
    Cell In[5], line 9
          6 # using repr format specifiers
          8 print("Is %r == %r?" % (int_five, str_five))
    ----> 9 print(f"Is {int_value!r} == {str_value!r}?")

    NameError: name 'int_value' is not defined

- When `str` is called on an argument
  1. First tries to call `__str__` on the argument
  2. If no `__str__` falls back to `__repr__`
  3. If neither exists, goes through method resolution
      - Calls the default object `repr`
      - The default is not very useful, just object type and memory
        address
        - Can’t pass to `eval`

``` python
# Resolving the default object repr

class OpaqueClass:
    def __init__(self, x, y):
        self.x = x
        self.y = y

obj = OpaqueClass(1, "foo")
print(obj)
```

    <__main__.OpaqueClass object at 0x7fa7b07b63c0>

- A lightweight `repr` implementation may be,

``` python
class BetterClass:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"BetterClass(x={self.x!r}, y={self.y!r})"


obj = BetterClass(1, "foo")
print(obj)
```

    BetterClass(x=1, y='foo')

- Observe that we delete to the `repr` of `x` and `y` to ensure they are
  also properly represented
- Above implicitly `print` is calling `str` which resolves to a call on
  `__repr__` due to the missing `__str__` method
  - We could add a `__str__` method
    - e.g. If we wanted output suitable for a UI element

``` python
class BetterClassWithStr:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"BetterClass(x={self.x!r}, y={self.y!r})"

    def __str__(self):
        return f"({self.x}, {self.y})"


obj = BetterClassWithStr(1, "foo")
print("Human readable:", obj)
print("Representation:", repr(obj))
```

    Human readable: (1, foo)
    Representation: BetterClass(x=1, y='foo')

- Note here we don’t use `!r` on the `x` and `y` attributes so they are
  formatted via `str` not `repr`

## Things to Remember

- Calling `print` returns the `str` representation of a variable
  - Implicitly human-readable and hides type information
- Calling `repr` on python built-ins produces the canonical
  representation of a value
  - `repr` strings are typically designed such that
    `eval(repr(obj)) == obj`
    - i.e. We can reconstruct an object via it’s representation
- `%s` in `%` operator format strings produces human readable strings
  via `str`
- `%r` in `%` operator format strings produces representative strings
  via `repr`
- F strings default to human-readable strings, but can instead use
  representative strings via the `!r` conversion suffix
- You can define the `__str__` and `__repr__` methods on your classes to
  control how they are printed when `str` and `repr` is called
  respectively
  - If there is no `__str__` method, `str` will use the `__repr__`
    method
  - The default `__repr__` on an object only provides the type and
    memory address of an object
