# Item 11: Prefer Interpolated F-strings over C-Style Format Strings and
`str.format`


- [Notes](#notes)
  - [C Style Formatting](#c-style-formatting)
    - [Type Conversion Errors](#type-conversion-errors)
    - [Readability](#readability)
    - [Repeated Values have to be Repeated in the
      Tuple](#repeated-values-have-to-be-repeated-in-the-tuple)
  - [The `format` Built-in function and
    `str.format`](#the-format-built-in-function-and-strformat)
  - [Interpolated Format Strings](#interpolated-format-strings)
- [Things to Remember](#things-to-remember)

## Notes

- Strings are the standard data format for presenting data to people
  - Rendering user interface messages
  - Writing data to files and sockets
  - Specifying exceptions
  - Used in logging and debugging
- *Formatting* strings is thus a common scenario
- Formatting is combining text and values into a single human readable
  message
- Python has *four* string formatting techniques
  - Most of them have flaws

### C Style Formatting

- Uses the `%` operator
  - Or formatting operator
- Predefined text template is specified to the left
  - Needs to be a *format string*
- Values to be inserted are specified to the right
  - As either a single value or tuple
- For example to convert hex and binary to integer strings:

``` python
binary = 0b10111011
hexadecimal = 0xC5F
print("Binary is %d, hex is %d" % (binary, hexadecimal))
```

    Binary is 187, hex is 3167

- Format string requires *format specifiers* as placeholders for
  injected values
  - Inherits C’s [printf](https://en.cppreference.com/w/c/io/fprintf)
    formatting
- Four main problems with C style format strings

#### Type Conversion Errors

- Changing the type or order of data values on the right side can cause
  type conversion errors
- Below illustrates printing the value of a float and the corresponding
  key

``` python
key = "my_var"
value = 1.234

formatted = "%-10s = %.2f" % (key, value)
print(formatted)
```

    my_var     = 1.23

- Swapping the order causes a runtime error
  - Observe that the error is thrown on `key`
  - i.e. `value` the float is coerced to a string

``` python
key = "my_var"
value = 1.234

formatted = "%-10s = %.2f" % (value, key)
print(formatted)
```

    TypeError: must be real number, not str
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[3], line 4
          1 key = "my_var"
          2 value = 1.234
    ----> 4 formatted = "%-10s = %.2f" % (value, key)
          5 print(formatted)

    TypeError: must be real number, not str

- We also get an error if we swap the format specifiers (leaving the
  values in their original order)

``` python
key = "my_var"
value = 1.234

formatted = "%.2f = %-10s" % (key, value)
print(formatted)
```

    TypeError: must be real number, not str
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    Cell In[4], line 4
          1 key = "my_var"
          2 value = 1.234
    ----> 4 formatted = "%.2f = %-10s" % (key, value)
          5 print(formatted)

    TypeError: must be real number, not str

- In other words changing one side of the format operator requires us to
  ensure the other side remains synchronised

#### Readability

- C-style strings become hard to read when values need to be modified
  before injection
- E.g. here we enumerate the contents of a pantry

``` python
pantry = [
    ("avocados", 1.25),
    ("bananas", 2.5),
    ("cherries", 15),
]

for i,  (item, count) in enumerate(pantry):
    print("#%d: %-10s = %.2f" % (i, item, count))
```

    #0: avocados   = 1.25
    #1: bananas    = 2.50
    #2: cherries   = 15.00

- Now suppose we want to tidy up the output so that the numbers print
  from $1$, item’s are printed in title format and the numbers are
  rounded

``` python
pantry = [
    ("avocados", 1.25),
    ("bananas", 2.5),
    ("cherries", 15),
]

for i, (item, count) in enumerate(pantry):
    print("#%d: %-10s = %d" % (i + 1, item.title(), round(count)))
```

    #1: Avocados   = 1
    #2: Bananas    = 2
    #3: Cherries   = 15

- The string is now very terse
  - The left side is almost purely formatting specifiers
  - The right side is a tuple of expressions

#### Repeated Values have to be Repeated in the Tuple

- Let’s say you want to use the same value multiple times
- Then have to repeat it in the tuple multiple times
  - And in the correct order

``` python
template = "%s loves food. See %s cook."
name = "Max"
formatted = template % (name, name)
print(formatted)
```

    Max loves food. See Max cook.

- Annoying when we have to combine it with editing the value for
  formatting
- e.g. We might add `title` as a method call on one use of `name` but
  not the second

``` python
template = "%s loves food. See %s cook."
name = "brad"
formatted = template % (name, name)
print(formatted)
```

    brad loves food. See brad cook.

- `%` does resolve this by allowing dictionary key-value substitution
  - Specified as `%(key)specifier`
  - This means that the dictionary doesn’t have to be ordered

``` python
key = "my_var"
value = 1.234

first_method = "%-10s = %.2f" % (key, value)

second_method = "%(key)-10s = %(value).2f" % {
    "key": key,
    "value": value,
}

reordered_second_method = "%(key)-10s = %(value).2f" % {
    "value": value,
    "key": key,
}

assert first_method == second_method == reordered_second_method
```

- This also means we only need to supply a specifier a value once if we
  repeat it

``` python
template = "%(name)s loves food. See %(name)s cook."
name = "brad"
formatted = template % {"name": name.title()}
print(formatted)
```

    Brad loves food. See Brad cook.

- Dictionaries also introduce tradeoffs
  - They are longer and noiser and make reading templating code even
    harder
  - Add in lots of repetition of the key, which must be kept consistent
    - Write the key in the format string, write the key in the
      dictionary, write the variable in the dictionary (see below)

``` python
# dictionaries significantly increase code verbosity
soup = "lentil"
formatted = "Today's soup is %(soup)s." % {
    "soup": soup,
}  # soup repeated three times to print it once
print(formatted)
```

    Today's soup is lentil.

- When we start having multiple values we want to inject this can get
  very verbose

``` python
menu = {
    "soup": "lentil",
    "oyster": "kumamato",
    "special": "schnitzel",
}

template = "Today's soup is %(soup)s, buy one get two %(oyster)s oysters, and our special entree is %(special)s"

formatted = template % menu
print(formatted)
```

    Today's soup is lentil, buy one get two kumamato oysters, and our special entree is schnitzel

### The `format` Built-in function and `str.format`

- *Advanced string formatting* was introduced in python 3
- For individual values this is via the `format` built-in
  - `^` centres text
  - `,` injects thousands separators

``` python
# formatting a float
number = 1234.5678
formatted = format(number, ",.2f")
print(formatted)

# formatting a string
string = "my string"
formatted = format(string, "^20s")
print("*", formatted, "*")
```

    1,234.57
    *      my string       *

- To format multiple values together we can use the `str.format` method
- Placeholders are specified with `{}` rather than `%`
- By default placeholders are replaced by the corresponding positional
  argument passed to `format`

``` python
key = "my_value"
value = 1.234

formatted = "{} = {}".format(key, value)
print(formatted)
```

    my_value = 1.234

- Within a placeholder `:` to precede format specifiers
  - Similar to the printf specifier language
  - Extends it to the formatting mini-language
  - See the [Python
    Documentation](https://docs.python.org/3/library/string.html#format-specification-mini-language)
    for details

``` python
key = "my_value"
value = 1.234

formatted = "{:<10} = {:.2f}".format(key, value)
```

- How to think about this?
  - Think of it as passing each format specifier and the value to the
    `format` built-in function
  - The result of that call is then injected into the placeholder in the
    string
- Formatting behaviour per class can be specified with the `__format__`
  dunder method
- To print a literal brace in a format string you need to escape it by
  repeating the brace e.g. `{{`
  - Otherwise may be mistakenly interpreted as a placeholder

``` python
print("%.2f%%" % 12.5) # C-style formatting, have to escape the literal %
print("{} replaces {{}}".format(1.23))
```

    12.50%
    1.23 replaces {}

- You can also specify the positional argument within braces
  - Means you can reorder the format string without having to reorder
    the arguments to `format`

``` python
formatted = "{1} = {0}".format(key, value)
print(formatted)
```

    1.234 = my_value

- You can reference the same positional index multiple times to repeat a
  value

``` python
formatted = "{0} loves food. See {0} cook".format("Alice")
print(formatted)
```

    Alice loves food. See Alice cook

- `format` is still verbose when the value needs to be edited

``` python
pantry = [
    ("avocados", 1.25),
    ("bananas", 2.5),
    ("cherries", 15),
]

for i, (item, count) in enumerate(pantry):
    old_style = ("#%d: %-10s = %d" % (i + 1, item.title(), round(count)))

    new_style = "#{}: {:<10s} = {}".format(i + 1, item.title(), round(count))

    assert old_style == new_style
```

- There are complex specifier combinations
  - e.g. using dictionary keys and list indices
  - Coercing to unicode and `repr` strings

``` python
menu = {
    "soup": "lentil",
    "oyster": "kumamato",
    "special": "schnitzel",
}

formatted = "First letter is {menu[oyster][0]!r}".format(menu=menu)
print(formatted)
```

    First letter is 'k'

- These don’t reduce the key redundancy issue
- For example compare the verbosity of all the following methods

``` python
menu = {
    "soup": "lentil",
    "oyster": "kumamato",
    "special": "schnitzel",
}

old_template = "Today's soup is %(soup)s, buy one get two %(oyster)s oysters, and our special entree is %(special)s"
old_formatted = old_template % menu

new_template = "Today's soup is {soup}, buy one get two {oyster} oysters, and our special entree is {special}"
new_formatted = new_template.format(**menu)

assert old_formatted == new_formatted
```

- The new format style is definitely cleaner, but it’s not necessarily
  less verbose
- Format does offer some advanced features (for example dictionary keys
  and list indices)
  - Does not capture the full set of python’s expression functionality
  - Undermines the usefulness of `str.format`
- `format` and it’s resultant mini-language are more useful to know from
  the perspective of how they informed *f-strings*

### Interpolated Format Strings

- Python added format strings *f-strings* in 3.6
- A format string must be prefixed by `f`
  - Similar to how a byte string is prefixed by `b`
  - Raw (unescaped) string is prefixed by `r`
- Let you reference any name in the current scope as part of the format
  string

``` python
key = "my_var"
value = 1.234

formatted = f"{key} = {value}"
print(formatted)
```

    my_var = 1.234

- Can use the format mini-language
  - As with format just put a `:` after the variable name e.g. `{0:.2f}`
    becomes `{value:.2f}`

``` python
formatted = f"{key!r:<10} = {value:.2f}"
print(formatted)
```

    'my_var'   = 1.23

- F strings are shorter than C-style strings and using the `format`
  method
- See below

``` python
f_string = f"{key:<10} = {value:.2f}"

c_tuple = "%-10s = %.2f" % (key, value)

c_dict = "%(key)-10s = %(value).2f" % {"key": key, "value": value}

str_args = "{:<10} = {:.2f}".format(key, value)

str_kw = "{key:<10} = {value:.2f}".format(key=key, value=value)

assert c_tuple == c_dict == f_string
assert f_string == str_args == str_kw
```

- F-strings can also take a full python expression
  - This solves the problem of verbosity by allowing in-place
    modification of values

``` python
# old style format method vs f-string
pantry = [
    ("avocados", 1.25),
    ("bananas", 2.5),
    ("cherries", 15),
]

for i, (item, count) in enumerate(pantry):
    format_method_style = "#{}: {:<10s} = {}".format(i + 1, item.title(), round(count))

    f_string_style = f"#{i + 1}: {item.title():<10s} = {round(count)}"

    assert format_method_style == f_string_style
```

- You can split an f-string via adjacent string concatenation

``` python
pantry = [
    ("avocados", 1.25),
    ("bananas", 2.5),
    ("cherries", 15),
]

for i, (item, count) in enumerate(pantry):
    print(f"#{i + 1}: "
          f"{item.title():<10s}"
          f"{round(count)}")
```

    #1: Avocados  1
    #2: Bananas   2
    #3: Cherries  15

- You can use python expressions to parameterise the format specifiers
  themselves

``` python
places = 3
number = 1.23456

print(f"My number is {number:.{places}f}")
```

    My number is 1.235

- The one downside to F-strings is that the templating and injection of
  values happens in one step
- In the previous messages we could define our template, then separately
  inject the values
- This is useful when we want to perform some validation of the injected
  data first
  - For example, if we accept SQL queries, we might want to validate
    that the SQL query is safe *before* the query string is processed
- This led to the introduction of template strings in Python 3.14
  - In most cases f-strings should still suffice
  - For an understanding of how template or t-strings differ and their
    use cases refer to the [PEP](https://peps.python.org/pep-0750/)

## Things to Remember

- C-style format strings use the `%` operator to format
  - They tend to be verbose and brittle
- The `format` built-in function, and the associated `str.format` method
  introduces useful concepts for formatting
  - The `format` mini-language provides the foundation for F-strings
  - Overall, it’s verbosity matches the C-style technique and should be
    avoided
- F-strings are a new syntax for formatting values into strings
  - They solve pretty much all issues with C-style format strings
- F-strings are succinct and powerful
  - They allow arbitrary python expressions to be directly embedded
    within format specifiers
- F-strings have the downside that specifying the template and injecting
  values are no longer distinct steps
  - T-strings introduced in Python 3.14 are generalised F-strings that
    allow for inspecting the interpolated values
  - They replace F-strings in some use cases were input might need to be
    validated or sanitised
  - In general F-strings should fulfill most use cases
