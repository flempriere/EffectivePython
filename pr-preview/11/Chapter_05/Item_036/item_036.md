# Item 36: Use `None` and Docstrings to Specify Dynamic Default
Arguments


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Sometimes we might want to use a function call, new object or
  container as a keyword argument default value
- e.g. printing timestamped log messages
  - Caller might specify a time, but by default we want to use the
    current time
- A naive approach is,

``` python
from time import sleep
from datetime import datetime

def log(message, when=datetime.now()):
    print(f"{when}: {message}")

log("Hi there")
sleep(0.1)
log("Hello again")
```

    2026-04-21 15:17:05.267380: Hi there
    2026-04-21 15:17:05.267380: Hello again

- Erroneously assumes that `datetime.now` is called whenever `log` is
  called with the default `when` value
  - The function is actually executed once when the function is defined
    at module import time
  - The same occurs if we for example try to pass an empty list
    - The same list is used
- Correct convention is to use `None`
  - Actual behaviour is then documented in the function docstring

``` python
from time import sleep
from datetime import datetime

def log(message, when=None):
    """
    Logs a message with a timestamp

    Parameters
    ----------
    message : str
        Message to print
    when : datetime | None
        datetime of when message occurred. If `when`
        is none, the current time is used. By default `None`

    Returns
    -------
    None
    """
    if when is None:
        when = datetime.now()
    print(f"{when}: {message}")

log("Hi there")
sleep(0.1)
log("Hello again")
```

    2026-04-21 15:17:05.376474: Hi there
    2026-04-21 15:17:05.476832: Hello again

- Again, suppose we tried to write function that loads json data,

``` python
import json

def decode(data, default={}):
    try:
        return json.loads(data)
    except ValueError:
        return default

foo = decode("Bad data")
foo["stuff"] = 5
bar = decode("also bad")
bar["meep"] = 1
print("Foo:", foo)
print("Bar:", bar)

assert foo is bar
```

    Foo: {'stuff': 5, 'meep': 1}
    Bar: {'stuff': 5, 'meep': 1}

- Same issue arises, the dictionary created by `default` is shared by
  all calls to `decode`
- Have to use `None` as a placeholder then explicitly create the
  dictionary

``` python
import json


def decode(data, default=None):
    """
    Load json data from a string

    Parameters
    ----------
    data : string
        JSON-encoded string to load
    default : dict[str, object]
        Value to return if decoding fails.
        By default an empty dictionary

    Returns
    -------
    dict[str, object]
        Decoded dictionary
    """

    try:
        return json.loads(data)
    except ValueError:
        if default is None:
            default = {}
        return default


foo = decode("Bad data")
foo["stuff"] = 5
bar = decode("also bad")
bar["meep"] = 1
print("Foo:", foo)
print("Bar:", bar)

assert foo is not bar
```

    Foo: {'stuff': 5}
    Bar: {'meep': 1}

- We can extend this further via typing

``` python
from time import sleep
from datetime import datetime

def log_typed(message: str, when: datetime | None = None) -> None:
    """
    Logs a message with a timestamp

    Parameters
    ----------
    message : str
        Message to print
    when : datetime | None
        datetime of when message occurred. If `when`
        is none, the current time is used. By default `None`

    Returns
    -------
    None
    """
    if when is None:
        when = datetime.now()
    print(f"{when}: {message}")

log("Hi there")
sleep(0.1)
log("Hello again")
```

    2026-04-21 15:17:05.501623: Hi there
    2026-04-21 15:17:05.601985: Hello again

## Things to Remember

- Default arguments are evaluated once at function definition
  - Dynamic mutable objects are thus shared across function calls
- Use `None` as a placeholder default value if the actual default must
  be initialised dynamically
  - Document the intended behaviour in the docstring
  - Check for `None`
- Using `None` can also be supported with type annotations
