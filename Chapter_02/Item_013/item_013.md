# Item 13: Prefer Explicit String Concatenation over Implicit

Especially in Lists

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Python’s initial development inherited many C-like features
- Including numeric literal notation and format specifiers
  - Octal now requires the `0o` prefix not `0`
  - Use F-strings and `format` over old style format specifiers ([Item
    11](../Item_011/item_011.qmd))
- Python retains implicit string concatenation
  - Adjacent string literals are concatenated
  - Originally designed in C to help with splitting long strings over
    multiple lines

``` python
# The following are equivalent
foo = "hello" + "world"
bar = "hello" "world"

assert foo == bar
```

- One use case is merging different types of strings
  - Having each on their own line makes it easy to read
  - Removing operators reduces noise

``` python
# concatenation a raw string, f-string and single-quote string

x = 1
foo = (
    r"first \ part is here with escapes\n, "
    f"string interpolation {x} in here, "
    'this has "double quotes" inside'
)
print(foo)
```

    first \ part is here with escapes\n, string interpolation 1 in here, this has "double quotes" inside

- Combining everything on the one line can be opaque
  - Hard to see where one string ends and the next begins

``` python
y = 2
bar = r"fir\st" f"{y}" '"third"'
print(bar)
```

    fir\st2"third"

- Implicit concatenation is prone to breakage
  - E.g. if someone adds a comma, instead of concatenation we’ll get
    tuples (See [Item 6](../../Chapter_01/Item_006/item_006.qmd))
  - Or in reverse, eliminating a comma means rather than a tuple or an
    error you get concatenation

``` python
# accidental tuple instead of concatenation
z = 3
foobar = r"fir\st", f"{z}" '"third"'
print(foobar)

# accidental concatenation instead of a list
foo_list = [
    "first line\n",
    "second line\n"
    "third line\n",
]
print(foo_list)
```

    ('fir\\st', '3"third"')
    ['first line\n', 'second line\nthird line\n']

- This can be easy to miss
  - Autoformatters may structure the code or merge strings which can
    help you spot the error
- Best to be explicit when you are concatenating
  - Might not be the cleanest presentation but makes the intention clear
  - Recall the [Zen of Python](../../Chapter_01/Chapter_01.qmd) *Prefer
    Explicit*

``` python
foo_list_with_explicit_concatenation = [
    "first line\n",
    "second line\n" + "third line\n",
]
print(foo_list_with_explicit_concatenation)
```

    ['first line\n', 'second line\nthird line\n']

- Above the autoformatter has put the last two lines and the
  concatenation operator together
  - Slightly longer line, but makes it clear the concatenation is
    happening
- Implicit concatenation can also occur in other places, e.g. function
  calls
  - With something like `print` this might even be more readable if we
    are passing arguments

``` python
import sys

print("this is a long message "
      "that should be printed out",
      end="",
      file=sys.stderr)
```

    this is a long message that should be printed out

- For other calls with multiple positional arguments can lead to errors

``` python
import sys

class MyData:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return f"MyData({self.args!r}, {self.kwargs!r})"


first_value = "foo"
second_value = "bar"
x = 1
y = 2

value = MyData(
    123,
    first_value,
    f"my_format_string {x}"
    f"another value {y}",
    "and here is more text",
    second_value,
    stream=sys.stderr,
)

print("With implicit concatenation")
print(value)

print("With explicit concatenation")

value = MyData(
    123,
    first_value,
    f"my_format string {x}" + f"another value {y}",
    "and here is more text",
    second_value,
    stream=sys.stderr,
)

print(value)
```

    With implicit concatenation
    MyData((123, 'foo', 'my_format_string 1another value 2', 'and here is more text', 'bar'), {'stream': <ipykernel.iostream.OutStream object at 0x7f9aeb51dd50>})
    With explicit concatenation
    MyData((123, 'foo', 'my_format string 1another value 2', 'and here is more text', 'bar'), {'stream': <ipykernel.iostream.OutStream object at 0x7f9aeb51dd50>})

- Always prefer explicit concatenation when a function has multiple
  positional arguments
- If there’s one positional argument then implicit string concatenation
  is fine
  - Here there is no ambiguity if separate strings are separate
    arguments
- Keyword arguments can be passed either way
  - Sibling string literals can’t be confused, since there needs to be
    an explicit `key =`

## Things to Remember

- Two adjacent string literals will be merged as if the `+` operator is
  supplied
- Avoid implicit string concatenation in collections
  - It is ambiguous if this is intentional or a missing comma
  - Use the explicit `+` operator
- For function calls
  - You may use implicit concatenation if the function accepts *one* and
    only *one* positional argument
  - You may use implicit concatenation with keyword arguments
  - Otherwise use explicit concatenation
