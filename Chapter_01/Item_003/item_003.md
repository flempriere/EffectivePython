# Item 3: Never Expect Python to Detect Errors at Compile Time

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Python doesn’t have a strict compile time
- It’s an interpreted language
- When a python program is loaded
  - Source code is parsed into abstract syntax trees
  - Checked for obvious syntax errors
    - This will raise a `SyntaxError`

``` python
if True # Bad Syntax
    print("hello")
```

    SyntaxError: expected ':' (1911516749.py, line 1)
      Cell In[1], line 1
        if True # Bad Syntax
                ^
    SyntaxError: expected ':'

    - Errors in literals can also be caught

``` python
1.3j5 # Bad number
```

    SyntaxError: invalid imaginary literal (59466289.py, line 1)
      Cell In[2], line 1
        1.3j5 # Bad number
           ^
    SyntaxError: invalid imaginary literal

- Not likely to get much than that

  - Basic tokenization errors
  - Parse errors

- Because python is dynamic, variable definitions and lifetimes are
  difficult to track

- Means that something obviously wrong like below, is not strictly
  invalid, so can’t be flagged as an error at parse time

``` python
def bad_reference():
    print(local_var)
    local_var = 123
```

- The error will only trip once we try to execute it

``` python
bad_reference()
```

    UnboundLocalError: cannot access local variable 'local_var' where it is not associated with a value
    ---------------------------------------------------------------------------
    UnboundLocalError                         Traceback (most recent call last)
    Cell In[4], line 1
    ----> 1 bad_reference()

    Cell In[3], line 2, in bad_reference()
          1 def bad_reference():
    ----> 2     print(local_var)
          3     local_var = 123

    UnboundLocalError: cannot access local variable 'local_var' where it is not associated with a value

- To emphasise this issue, we can see that in the function below,
  sometimes `x` is valid, sometimes not

``` python
def sometimes_ok(x):
    if x:
        local_var = 123
    print(local_var)
```

- If we call it, with a truthful value for `x`, every work fine

``` python
sometimes_ok(True)
```

    123

- If not,

``` python
sometimes_ok(False)
```

    UnboundLocalError: cannot access local variable 'local_var' where it is not associated with a value
    ---------------------------------------------------------------------------
    UnboundLocalError                         Traceback (most recent call last)
    Cell In[7], line 1
    ----> 1 sometimes_ok(False)

    Cell In[5], line 4, in sometimes_ok(x)
          2 if x:
          3     local_var = 123
    ----> 4 print(local_var)

    UnboundLocalError: cannot access local variable 'local_var' where it is not associated with a value

- Python can also struggle with mathematical errors, e.g.

``` python
def bad_math():
    return 1 / 0


bad_math()
```

    ZeroDivisionError: division by zero
    ---------------------------------------------------------------------------
    ZeroDivisionError                         Traceback (most recent call last)
    Cell In[8], line 5
          1 def bad_math():
          2     return 1 / 0
    ----> 5 bad_math()

    Cell In[8], line 2, in bad_math()
          1 def bad_math():
    ----> 2     return 1 / 0

    ZeroDivisionError: division by zero

- Can’t immediately infer this is wrong because the `/` operator might
  have been overloaded

- Some other problems python will fail to statically detect are

  1. undefined methods
  2. too many or too few arguments to a function call
  3. mismatched return types

- Linting tools like [Flake 8](../Item_002/item_002.qmd#automation) and
  Ruff (see above) can help catch these

  - More advanced techniques are *type checkers*
  - We’ll discuss these later

- Even with these tools its important to be aware that most python
  errors will be caught at run time

  - This is because python prioritises run time flexibility

- Therefore it’s important to,

  1. Check assumptions are correct at run time
  2. Verify program correctness with automated tests

## Things to Remember

- Python detects most errors at run time
- Community projects like linters and type checkers can help catch some
  types of errors
