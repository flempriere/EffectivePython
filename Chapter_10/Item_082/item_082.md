# Item 82: Consider `contextlib` and `with` Statements for Reusable
`try/finally` behaviour


- [Notes](#notes)
  - [Enabling `as` Targets](#enabling-as-targets)
- [Things to Remember](#things-to-remember)

## Notes

- `with` statement allows a block of code to be run within a special
  *context*
  - We’ve seen this before with file handlers and mutex Locks (See [Item
    69](../../Chapter_09/Item_069/item_069.qmd))
  - Allows code to be run with a resource, then for that resource to be
    released

``` python
# Managing a Lock via a context

from threading import Lock

lock = Lock()
with lock:
    print("Doing something with the lock...")
print("lock released")
```

    Doing something with the lock...
    lock released

- The above example is equivalent to the following `try/finally` block
  (See [Item 80](../Item_080/item_080.qmd))
  - Because `Lock` implements the methods to be used as a `with` context
    object

``` python
# Managing a lock via try/finally
from threading import Lock

lock = Lock()
lock.acquire()
try:
    print("Doing something with the lock")
finally:
    lock.release()
```

    Doing something with the lock

- `with` statement version eliminates the `try/finally` boilerplate
- Automatically ensures each `acquire` is matched to a `release`
- If we want to make our own objects work as a context object for `with`
  we can do so via the `contextlib` built-in (See [Item
  38](../../Chapter_05/Item_038/item_038.qmd) for an example usage)
  - `contextmanager` is a decorator for enabling simple functions to be
    context objects
- The other approach is to define `__enter__` and `__exit__`
  - This is an OOP approach
- For example, consider implementing logging
  - We might want to wrap a region of code to have a higher level of
    logging
  - By default the program logger will report `WARNING` and `ERROR`
    messages

``` python
import logging


def my_function():
    logging.debug("Some debug data")  # low level debug information
    logging.error("Error log here")  # high level error
    logging.debug("More debug data")  # low level debug information


# Only reports the error message
my_function()
```

    ERROR:root:Error log here

- If we want to elevate the logging can now use a `contextmanager`
  - Write a helper function to boost the logging severity
  - Then runs the code in the `with`
  - Then returns the logging level to previous

``` python
from contextlib import contextmanager
import logging


def my_function():
    logging.debug("Some debug data")  # low level debug information
    logging.error("Error log here")  # high level error
    logging.debug("More debug data")  # low level debug information


# Called with initial default logging config
print("* Before:", flush=True)
my_function()


@contextmanager
def debug_logging(level):
    logger = logging.getLogger()
    old_level = logger.getEffectiveLevel()
    logger.setLevel(level)
    try:
        yield
    finally:
        logger.setLevel(old_level)


with debug_logging(logging.DEBUG):
    print("* Inside:", flush=True)
    my_function()

print("* After:", flush=True)
my_function()
```

    * Before:

    ERROR:root:Error log here

    * Inside:

    DEBUG:root:Some debug data
    ERROR:root:Error log here
    DEBUG:root:More debug data

    * After:

    ERROR:root:Error log here

- The `yield` passes control back from the `with` context management to
  the contexts of the block statement (See [Item
  43](../../Chapter_06/Item_043/item_043.qmd))
- Exceptions raised in the `with` block are re-raised by the `yield`
  expression (See [Item 47](../../Chapter_06/Item_047/item_047.qmd))
- We can then call `my_function` again
  - This time *inside* the context of `debug_logging` at the set level
  - All debug messages should be printed now
- Running the function again, outside the context should show the old
  level of debugging

### Enabling `as` Targets

- A context manager in a `with` statement may also return an object
- Object is assigned to a local object via the `as` keyword
- Let’s code within a `with` statement access it’s context (See [Item
  76](../../Chapter_09/Item_076/item_076.qmd))
- For example, a common use case is opening a file, interacting with it,
  and ensuring it’s closed correctly
  - Can do with the `open` statement in `with`
  - Use `as` to receive the opened file handler
  - Closed as part of the context clean up at the end of the `with`

``` python
import os

with open("my_output.txt", "w") as handle:
    handle.write("This is some data!")

os.remove("my_output.txt")
print("Wrote to a file...")
```

    Wrote to a file...

- The equivalent `try/finally` block is again bulky and less pythonic

``` python
import os

handle = open("my_output.txt", "w")
try:
    handle.write("This is some data!")
finally:
    handle.close()
    os.remove("my_output.txt")
```

- `as` also ensures that we don’t have to worry about all the edge cases
  of making sure the file is closed
- Custom objects can also provide their context object for an `as`
  - Rather than a naked `yield` instead `yield` a value
- We can do this with our logging function from before
  - Let it return a `Logger` instance as well as setting it’s level
  - Let’s us have distinct loggers for the context

``` python
from contextlib import contextmanager
import logging


def my_function():
    logging.debug("Some debug data")  # low level debug information
    logging.error("Error log here")  # high level error
    logging.debug("More debug data")  # low level debug information


# Called with initial default logging config
print("* Before:", flush=True)
my_function()


@contextmanager
def log_level(level, name):
    logger = logging.getLogger(name)
    old_level = logger.getEffectiveLevel()
    logger.setLevel(level)
    try:
        yield logger
    finally:
        logger.setLevel(old_level)


with log_level(logging.DEBUG, "my-log") as my_logger:
    print("* Inside context:", flush=True)
    my_logger.debug(f"This is a message for {my_logger.name}!")
    logging.debug("This will not print - In the global logger")

print("* After:", flush=True)
logger = logging.getLogger("my-log")
logger.debug("Debug will not print")
logger.error("Error will print")
```

    * Before:

    ERROR:root:Error log here

    * Inside context:

    DEBUG:my-log:This is a message for my-log!

    * After:

    ERROR:my-log:Error will print

- In the above example we define a `Logger`, `my-log` to use inside the
  context
  - Set it’s level to debug
  - Inside the context debug messages sent to *this* logger are reported
  - Inside the context, debug messages in other loggers are not reported
  - Outside the context `my-log` is treated with the same global logging
    setting
    - Debug messages are not reported
- If we wanted to change the logger’s name, now only need to change the
  argument supplied to the context
- `with` allows us to decouple context creation, from context
  interaction

## Things to Remember

- `with` provides `try/finally` like logic in a reusable and cleaner
  interface
- `contextlib` built-in provides the `contextmanager` decorator for
  converting simple functions to context objects
- context objects can `yield` a value to be assigned to a local variable
  in a `with` block via the `as` statement
  - Useful for letting code directly interact with a context
