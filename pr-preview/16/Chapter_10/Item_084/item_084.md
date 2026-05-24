# Item 84: Beware of Exception Variables Disappearing


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Exception variables are not accessible after an `except` block
  - This is in contrast to `for` loop variables (See [Item
    20](../../Chapter_03/Item_020/item_020.qmd))

``` python
class MyError(Exception):
    pass


try:
    raise MyError(123)
except MyError as e:
    print(f"Inside {e=}")  # Works

print(f"Outside {e=}")  # Raises
```

    Inside e=MyError(123)

    NameError: name 'e' is not defined
    ---------------------------------------------------------------------------
    NameError                                 Traceback (most recent call last)
    Cell In[1], line 10
          7 except MyError as e:
          8     print(f"Inside {e=}")  # Works
    ---> 10 print(f"Outside {e=}")  # Raises

    NameError: name 'e' is not defined

- This includes the scope of a `finally` branch in a
  `try/except/finally` construct

``` python
class MyError(Exception):
    pass


try:
    raise MyError(123)
except MyError as e:
    print(f"Inside {e=}")  # Works
finally:
    print(f"Finally {e=}")  # Raises
```

    Inside e=MyError(123)

    NameError: name 'e' is not defined
    ---------------------------------------------------------------------------
    NameError                                 Traceback (most recent call last)
    Cell In[2], line 10
          8     print(f"Inside {e=}")  # Works
          9 finally:
    ---> 10     print(f"Finally {e=}")  # Raises

    NameError: name 'e' is not defined

- If we want to use the result outside the block, have to define another
  variable
  - e.g. for logging purposes

``` python
result = "Unhandled exception"


class MyError(Exception):
    pass


class OtherError(Exception):
    pass


try:
    raise MyError(123)
except MyError as e:
    result = e
except OtherError as e:
    result = e
else:
    result = "Success"
finally:
    print(f"Log {result=}")
```

    Log result=MyError(123)

- Need the `result` variable to exist and be assigned before the
  `try/except` block
  - Prevents an unhandled exception failing to set `result`
  - Instead of seeing the actual error we get a runtime error

``` python
%reset -f

class MyError(Exception):
    pass


class OtherError(Exception):
    pass


try:
    raise OtherError(123)
except MyError as e:
    result = e
else:
    result = "Success"
finally:
    print(f"Log {result=}")
```

    NameError: name 'result' is not defined
    ---------------------------------------------------------------------------
    OtherError                                Traceback (most recent call last)
    Cell In[4], line 12
         11 try:
    ---> 12     raise OtherError(123)
         13 except MyError as e:

    OtherError: 123

    During handling of the above exception, another exception occurred:

    NameError                                 Traceback (most recent call last)
    Cell In[4], line 18
         16     result = "Success"
         17 finally:
    ---> 18     print(f"Log {result=}")

    NameError: name 'result' is not defined

- As usual with python it’s worth remembering that different variable
  “types” have different scopes and lifetimes e.g.
  - `for` loop variables
  - generator expressions variables
  - List comprehensions variables (See [Item
    42](../../Chapter_06/Item_042/item_042.qmd))

## Things to Remember

- Exception variables caught via the `with` in an `except` block only
  exist within the `except` block
- To catch an exception and access it in a subsequent block or enclosing
  scope it must be assigned to an already defined variable in the outer
  scope
