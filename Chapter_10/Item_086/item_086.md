# Item 86: Understand the Difference between `Exception` and
`BaseException`


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Python documentation recommends inheriting from the `Exception` base
  class
  - The true root class is `BaseException`
  - Subclasses of `BaseException` that are not also subclasses of
    `Exception` are used for python’s internal error-handling
- For example, using CTRL+C
  - Typically this is expected to cause a program interrupt
  - Python implements this in a platform dependent manner
  - But will generate a `KeyboardInterrupt` and raise it in the main
    thread
    - Does not inherit from `Exception`
    - Means that can’t be stopped by a `except Exception` block
      - Which is good, we don’t want a python user to accidentally
        prevent their program from being able to close
- We’ll demonstrate this below with a simple block that simulates an
  infinite loop

``` python
import sys


def do_processing():
    raise KeyboardInterrupt  # Simulate CTRL+C being pressed


def main(argv):
    while True:
        try:
            do_processing()  # Interrupted
        except Exception as e:
            print("Error:", type(e), e)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

    KeyboardInterrupt: 
    ---------------------------------------------------------------------------
    KeyboardInterrupt                         Traceback (most recent call last)
    Cell In[1], line 18
         14     return 0
         17 if __name__ == "__main__":
    ---> 18     sys.exit(main(sys.argv))

    Cell In[1], line 11, in main(argv)
          9 while True:
         10     try:
    ---> 11         do_processing()  # Interrupted
         12     except Exception as e:
         13         print("Error:", type(e), e)

    Cell In[1], line 5, in do_processing()
          4 def do_processing():
    ----> 5     raise KeyboardInterrupt

    KeyboardInterrupt: 

- One might then be tempted to catch `BaseException`
  - E.g. if we wanted to ensure some cleanup always occurs before
    program termination
    - Flush open files to disk
- Might also be tempted to use it to insulate components against
  potential errors
  - Or provide robust APIs (See [Item 85](../Item_085/item_085.qmd) and
    [Item 121](../../Chapter_14/Item_121/item_121.qmd))
- Can use a nonzero return value to indicate the program has exited with
  an error code

``` python
import sys


def do_processing(data):
    raise KeyboardInterrupt  # Simulate CTRL+C being pressed


def main(argv):
    data_path = argv[1]
    handle = open(data_path, "w+")

    while True:
        try:
            do_processing(handle)  # Interrupted
        except Exception as e:
            print("Error:", type(e), e)
        except BaseException:
            print("Cleanup up interrupt")
            handle.flush()
            handle.close()
            return 1
    return 0


if __name__ == "__main__":
    with open("foo.txt", "w") as f:
        f.write("File exists")
    sys.exit(main(argv=["ignore", "foo.txt"]))
```

    Cleanup up interrupt

    SystemExit: 1
    An exception has occurred, use %tb to see the full traceback.

    SystemExit: 1

    /home/runner/work/EffectivePython/EffectivePython/.venv/lib/python3.14/site-packages/IPython/core/interactiveshell.py:3755: UserWarning: To exit: use 'exit', 'quit', or Ctrl-D.
      warn("To exit: use 'exit', 'quit', or Ctrl-D.", stacklevel=1)

- Other exception types also inherit from `BaseException`
  - This includes `SystemExit` (Caused by `sys.exit` and
    `GeneratorExit`, See [Item 89](../Item_089/item_089.qmd))
  - More might be added in the future
- Python treats exceptions as mechanisms for executing desired behaviour
  - Not for reporting error conditions
    - Hence the disjoint class hierarchy
- Catching these behaviours can fundamentally break the python runtime
  - Avoid them
- A better approach is to use `try/finally` blocks (See [Item
  80](../Item_080/item_080.qmd)) and `with` statements (See [Item
  82](../Item_082/item_082.qmd))
  - Ensures cleanup runs regardless of where an exception is raised from

``` python
import sys


def do_processing(data):
    raise KeyboardInterrupt  # Simulate CTRL+C being pressed


def main(argv):
    data_path = argv[1]
    handle = open(data_path, "w+")

    try:
        while True:
            try:
                do_processing(handle)
            except Exception as e:
                print("Error:", type(e), e)
    finally:
        print("Cleaning up finally")  # Always runs
        handle.flush()
        handle.close()
    return 0


if __name__ == "__main__":
    with open("foo.txt", "w") as f:
        f.write("File exists")
    sys.exit(main(argv=["ignore", "foo.txt"]))
```

    Cleaning up finally

    KeyboardInterrupt: 
    ---------------------------------------------------------------------------
    KeyboardInterrupt                         Traceback (most recent call last)
    Cell In[3], line 28
         26 with open("foo.txt", "w") as f:
         27     f.write("File exists")
    ---> 28 sys.exit(main(argv=["ignore", "foo.txt"]))

    Cell In[3], line 15, in main(argv)
         13 while True:
         14     try:
    ---> 15         do_processing(handle)
         16     except Exception as e:
         17         print("Error:", type(e), e)

    Cell In[3], line 5, in do_processing(data)
          4 def do_processing(data):
    ----> 5     raise KeyboardInterrupt

    KeyboardInterrupt: 

- If you need to catch a `BaseException` or it’s subclasses you need to
  ensure the error is correctly propagated
  - Ensures code higher up the call stack can receive and consume it
- E.g. We might want to confirm that a user wants to quit before
  proceeding with a `KeyboardInterrupt`
  - We could do so via a bare `raise`
    - Ensures the `traceback` is preserved (See [Item
      87](../Item_087/item_087.qmd))

``` python
import sys


def do_processing():
    raise KeyboardInterrupt  # Simulate CTRL+C being pressed


def main(argv):
    while True:
        try:
            do_processing()
        except Exception as e:
            print("Error:", type(e), e)
        except KeyboardInterrupt:
            print("Confirm quit placeholder...")
            found = "y"  # Replace with line below to actually simulate the input
            # found = input("Terminate? [y/n]: ")
            if found == "y":
                raise


if __name__ == "__main__":
    with open("foo.txt", "w") as f:
        f.write("File exists")
    sys.exit(main(argv=["ignore"]))
```

    Confirm quit placeholder...

    KeyboardInterrupt: 
    ---------------------------------------------------------------------------
    KeyboardInterrupt                         Traceback (most recent call last)
    Cell In[4], line 25
         23 with open("foo.txt", "w") as f:
         24     f.write("File exists")
    ---> 25 sys.exit(main(argv=["ignore"]))

    Cell In[4], line 11, in main(argv)
          9 while True:
         10     try:
    ---> 11         do_processing()
         12     except Exception as e:
         13         print("Error:", type(e), e)

    Cell In[4], line 5, in do_processing()
          4 def do_processing():
    ----> 5     raise KeyboardInterrupt

    KeyboardInterrupt: 

- Another use case is to provide enhanced logging (See [Item
  87](../Item_087/item_087.qmd))
- E.g. consider a decorator which logs all inputs and outputs (See [Item
  38](../../Chapter_05/Item_038/item_038.qmd))
  - We want to include all raised exceptions

``` python
import functools


def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            result = e
            raise
        finally:
            print(f"Called {func.__name__}(*{args!r}, **{kwargs!r}) got {result!r}")

    return wrapper


@log
def my_func(x):
    x / 0


my_func(123)
```

    Called my_func(*(123,), **{}) got ZeroDivisionError('division by zero')

    ZeroDivisionError: division by zero
    ---------------------------------------------------------------------------
    ZeroDivisionError                         Traceback (most recent call last)
    Cell In[5], line 23
         18 @log
         19 def my_func(x):
         20     x / 0
    ---> 23 my_func(123)

    Cell In[5], line 8, in log.<locals>.wrapper(*args, **kwargs)
          5 @functools.wraps(func)
          6 def wrapper(*args, **kwargs):
          7     try:
    ----> 8         result = func(*args, **kwargs)
          9     except Exception as e:
         10         result = e

    Cell In[5], line 20, in my_func(x)
         18 @log
         19 def my_func(x):
    ---> 20     x / 0

    ZeroDivisionError: division by zero

- The above decorator works for standard `Exception`, but can break for
  other `BaseException` subclasses

``` python
import functools
import sys


def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            result = e
            raise
        finally:
            print(f"Called {func.__name__}(*{args!r}, **{kwargs!r}) got {result!r}")

    return wrapper


@log
def other_func(x):
    if x > 0:
        sys.exit(1)


other_func(456)
```

    UnboundLocalError: cannot access local variable 'result' where it is not associated with a value
    ---------------------------------------------------------------------------
    SystemExit                                Traceback (most recent call last)
    Cell In[6], line 9, in log.<locals>.wrapper(*args, **kwargs)
          8 try:
    ----> 9     result = func(*args, **kwargs)
         10 except Exception as e:

    Cell In[6], line 22, in other_func(x)
         21 if x > 0:
    ---> 22     sys.exit(1)

    SystemExit: 1

    During handling of the above exception, another exception occurred:

    UnboundLocalError                         Traceback (most recent call last)
    Cell In[6], line 25
         21     if x > 0:
         22         sys.exit(1)
    ---> 25 other_func(456)

    Cell In[6], line 14, in log.<locals>.wrapper(*args, **kwargs)
         12     raise
         13 finally:
    ---> 14     print(f"Called {func.__name__}(*{args!r}, **{kwargs!r}) got {result!r}")

    UnboundLocalError: cannot access local variable 'result' where it is not associated with a value

- This is because the `finally` block runs regardless of if an exception
  was caught or not
  - Means that `result` has not been assigned (See [Item
    84](../Item_084/item_084.qmd))
  - Since `SystemExit` is not an subclass of `Exception`
- To fix this we have to ensure we catch the `BaseException`

``` python
import functools
import sys


def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except BaseException as e:
            result = e
            raise
        finally:
            print(f"Called {func.__name__}(*{args!r}, **{kwargs!r}) got {result!r}")

    return wrapper


@log
def other_func(x):
    if x > 0:
        sys.exit(1)


other_func(456)
```

    Called other_func(*(456,), **{}) got SystemExit(1)

    SystemExit: 1
    An exception has occurred, use %tb to see the full traceback.

    SystemExit: 1

- In general try to avoid handling `BaseException`, but when you do need
  to, beware to make sure you’re following them correctly

## Things to Remember

- Python uses `BaseException` to implement internal behaviours
  - These bypass `except Exception` clauses
- `try/finally` statements, `with` statements and similar constructs can
  handle raised `BaseException` child classes
- There are reasons to catch `BaseException`
  - Doing so can be error prone
