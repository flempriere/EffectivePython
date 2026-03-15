# Item 4: Write Helper Functions instead of Complex Expressions


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Python’s high level syntax lets you write very compact expressions
- e.g. To decode a website query string,

``` python
from urllib.parse import parse_qs

my_values = parse_qs("red=5&blue=0&green=", keep_blank_values=True)
print(repr(my_values))
```

    {'red': ['5'], 'blue': ['0'], 'green': ['']}

- Query strings parameters may
  1.  Have multiple values
  2.  Have a single value
  3.  Be present with no value
  4.  Be omitted entirely
- If we try and access them using a dictionary, we get different results

``` python
print("Red: {0}".format(my_values.get("red")))
print("Green: {0}".format(my_values.get("green")))
print("Opacity: {0}".format(my_values.get("opacity")))
```

    Red: ['5']
    Green: ['']
    Opacity: None

- Might like to assign $0$ to a missing parameter or blank parameter
- We can write a complicated python expression to do this
  - Why?
    - Empty string, empty list and zero are all `False`
    - Means that in the below expressions, if the first part is `False`,
      then the rest evaluates to $0$

  ``` python
    red = my_values.get("red", [""])[0] or 0
    green = my_values.get("green", [""])[0] or 0
    opacity = my_values.get("opacity", [""])[0] or 0

    print(f"Red:        {red!r}")
    print(f"Green:      {green!r}")
    print(f"Opacity:    {opacity!r}")
  ```

      Red:        '5'
      Green:      0
      Opacity:    0

  - In the `"red"` case, red is in the dictionary and so is retrieved
    - The value is non-zero and so `True`
    - The first expression ends and `"5"` is returned
  - In the `"green"` case, green is in the dictionary
    - The empty string is retrieved
    - Evaluates to `False`
    - So we move to the second sub-expression which results in `0` being
      returned
  - In the `"opacity"` case, opacity is not in the dictionary
    - `get` returns `[""]`
    - We then access the list to get the empty string
    - This evaluates to `False`
    - We move to the second sub-expression which results in `0` being
      returned
- This logic is very hard to understand, even while knowing what is
  trying to be achieved
- Still not complete!
  - For the missing values we have the integer `0`
  - For the values that are present we have the string `"5"`
  - So we need to add an extra layer to do a conversion to integer, e.g.

``` python
red = int(my_values.get("red", [""])[0] or 0)
print(f"Red:        {red!r}")
```

    Red:        5

- At this the code while functional is too obscure to be easily
  understood
- Instead we could write a simple function

``` python
def get_first_int(values, key, default=0):
    found = values.get(key, [""])
    if found[0]:
        return int(found[0])
    return default
```

- This is much easier to understand and follow
  - Also easier to modify in the future
- We can rewrite our initial parse as

``` python
red = get_first_int(my_values, "red")
green = get_first_int(my_values, "green")
opacity = get_first_int(my_values, "opacity")

print(f"Red:        {red!r}")
print(f"Green:      {green!r}")
print(f"Opacity:    {opacity!r}")
```

    Red:        5
    Green:      0
    Opacity:    0

- As with anything follow the rules
  - Code is read more than it is written
  - *Don’t repeat yourself*

## Things to Remember

- Python’s syntax lets you write complicated single line expressions
  - These are difficult to read
- Instead break complex expressions into easy to read helper functions
