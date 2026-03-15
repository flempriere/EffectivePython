# Item 7: Consider Conditional Expressions for Simple Inline Logic

- [Things to Remember](#things-to-remember)

- Python `if` statements are *not* expressions
  - The whole block does not evaluate to a result
- Python also supports *conditional expressions*
  - Provide `if`/`elif`/`else` behaviour anywhere we can use an
    expression

``` python
i = 3
x = "even" if i % 2 == 0 else "odd"
print(x)
```

    odd

- Analogous to a ternary operator in other languages
- In python the result of a truthful expression comes first
- For example, here the `fail()` is never called, because the middle
  expression `False` is the one controlling the branch

``` python
def fail():
    raise Exception("Oops")

x = fail() if False else 20
print(x)
```

    20

- `if` syntax mimics that for filtering
- Here we can use `if` to control what values are included in a list
  comprehension

``` python
result = [x/4 for x in range(10) if x % 2 == 0]
print(result)
```

    [0.0, 0.5, 1.0, 1.5, 2.0]

- Observe the format is still *result* precedes the *test* condition
- Prior to conditional expressions people would emulate them with
  *boolean expressions*

``` python
i = 3
x = (i % 2 == 0 and "even") or "odd"
print(x)
```

    odd

- This emulates the first conditional expression
  - Relies on understanding python’s quirks for evaluating boolean
    expressions
  - `and` returns the first falsely value or last truthy
  - `or` returns the first truthy or last falsey
- Doesn’t generalise to when you want a falsey result from a truthy
  condition, e.g.

``` python
i = 2
x = (i % 2 == 0 and []) or [1]
print(x)
```

    [1]

- This always evaluates to `[1]`

- Avoid using boolean expressions

- Can instead use a regular `if`, `else` statement

``` python
i = 3

if  i % 2 == 0:
    x = "even"
else:
    x = "odd"
print(x)
```

    odd

- This is longer, but
  - Easier to add more logic to each conditional branch
  - e.g. debugging information

``` python
i = 3
if i % 2 == 0:
    x = "even"
else:
    x = "odd"
    print("It was odd!")
print(x)
```

    It was odd!
    odd

- Can add additional `elif` blocks

``` python
i = 3
if i % 2 == 0:
    x = "even"
elif i % 3 == 0:
    x = "divisible by three"
else:
    x = "odd, and not divisible by three"
print(x)
```

    divisible by three

- If we need the brevity of a conditional expression, we can just write
  a [helper function](../Item_004/item_004.qmd)
  - Which can also be reused

``` python
i = 3

def number_group(i):
    if i % 2 == 0:
        return "even"
    else:
        return "odd"
x = number_group(i)
print(x)
```

    odd

- When to then use conditionals?
  - Avoid if they have to split over multiple lines, e.g.

    ``` python
      x = (
          my_long_function_call(1, 2, 3)
          if i % 2 == 0
          else my_other_long_function_call(4, 5, 6)
      )
    ```

  - Here the expression is the same length as if we had just written it
    using a normal `if...else` construct
- Alternative is assignment expressions
  - Downside is these must be parenthesised in ambiguous contexts
- For example, we could write

``` python
x = 2
y = 1
if x and (z := x > y):
    print(z)
```

    True

- But we get a syntax error if we exclude the parenthesis

``` python
x = 2
y = 1
if x and z := x > y:
    print(z)
```

    SyntaxError: cannot use assignment expressions with expression (382079110.py, line 3)
      Cell In[11], line 3
        if x and z := x > y:
           ^
    SyntaxError: cannot use assignment expressions with expression

- Not required for conditional expressions
  - Does not mean that it’s any clearer

  ``` python
    if x > y if z else w: # ambiguous
        ...
    if x > (y if z else w): # clear
  ```

- Assignment expressions also need parentheses inside a function call
  argument list

``` python
z = dict(your_value=(y := 1))
print(z)
```

    {'your_value': 1}

- Omitting them causes a syntax error

``` python
w = dict(other_value = y := 1)
print(w)
```

    SyntaxError: invalid syntax (1473295337.py, line 1)
      Cell In[13], line 1
        w = dict(other_value = y := 1)
                                 ^
    SyntaxError: invalid syntax

- Conditional expressions don’t but the longer text may make it harder
  to read

``` python
v = dict(my_value = 1 if x else 3)
```

## Things to Remember

- Conditional expressions let you put an `if` statement where you might
  want an expression
- Order of the test expression, true result and false result is
  different to the typical ternary expression
  - It goes `true result if test expression else false result`
- Don’t use conditional expressions where they increase ambiguity and
  reduce readability
- Prefer standard `if` conditions and helper functions
