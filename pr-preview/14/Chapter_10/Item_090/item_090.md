# Item 90: Never set `__debug__` to `False`


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Consider the following `assert` statement

``` python
n = 3
assert n % 2 == 0, f"{n=} not even"
```

    AssertionError: n=3 not even
    ---------------------------------------------------------------------------
    AssertionError                            Traceback (most recent call last)
    Cell In[1], line 2
          1 n = 3
    ----> 2 assert n % 2 == 0, f"{n=} not even"

    AssertionError: n=3 not even

- This can be unrolled to the following,

``` python
if __debug__:
    if not (n % 2 == 0):
        raise AssertionError(f"{n=} not even")
```

    AssertionError: n=3 not even
    ---------------------------------------------------------------------------
    AssertionError                            Traceback (most recent call last)
    Cell In[2], line 3
          1 if __debug__:
          2     if not (n % 2 == 0):
    ----> 3         raise AssertionError(f"{n=} not even")

    AssertionError: n=3 not even

- `__debug__` is a global built-in variable indicating if a program is
  in debug mode
- You can use this too, to gate the execution of debugging code

``` python
def expensive_check(x):
    return x % 2 == 0


items = [1, 2, 3]
if __debug__:
    for i in items:
        assert expensive_check(i), f"Failed {i=}"
```

    AssertionError: Failed i=1
    ---------------------------------------------------------------------------
    AssertionError                            Traceback (most recent call last)
    Cell In[3], line 8
          6 if __debug__:
          7     for i in items:
    ----> 8         assert expensive_check(i), f"Failed {i=}"

    AssertionError: Failed i=1

- Setting the value of `__debug__` is to pass the `-O` command-line
  argument at startup
- An invocation with debug set `True` would look like,

``` shell
$ python3 -c 'assert False, "FAIL"; print("OK")'
Traceback ...
AssertionError: FAIL
```

- An invocation with the `-O` option to suppress debug might then look
  like

``` shell
$ python3 -O -c 'assert False, "FAIL"; print("OK")'
OK
```

- `__debug__` is one of the view python values that cannot be modified
  at runtime (See [Item 3](../../Chapter_01/Item_003/item_003.qmd))

``` python
__debug__ = False  # Should fail
```

    SyntaxError: cannot assign to __debug__ (3290014215.py, line 1)
      Cell In[4], line 1
        __debug__ = False  # Should fail
        ^
    SyntaxError: cannot assign to __debug__

- Once set, `__debug__` can’t be changed
- `__debug__` *was* intended to allow users to optimise code between
  debug and release profiles
- *However*, many modules, frameworks and libraries depend on `assert`
  to validate their runtime (See [Item 81](../Item_081/item_081.qmd))
  - This means turning off `__debug__` *can* break a program
  - The speed up value of turning off debug is also generally
    questionable
- If you have expensive code that should be disabled in some runtimes
  - Manually implement it
  - Use functions and your own globals
- `assert` statements are typically more valuable always being kept on
  - Especially in low level code
  - `assert`’s help provide guarantees around where a programs
    assumptions hold
  - If an `assert` is passing, then we know that’s not the source of the
    problem
- Prefer liberal use of `assert` over spurious micro-optimisation of
  turning off `__debug__`

## Things to Remember

- `__debug__` is a global built-in variable indicating the debug state
  of a python program
  - By default it set to `True`
- `assert` statements only execute if `__debug__` is `True`
- The `-O` command-line flag can be used to set `__debug__` to `False`
  - Indicates `assert` statements are ignored
- `assert` statements can be used to narrow the cause of a bug even when
  they don’t directly fail
