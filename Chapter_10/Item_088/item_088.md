# Item 88: Consider Explicitly Chaining Exceptions to Clarify Tracebacks


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Python uses exceptions as it’s main method of handling or identifying
  errors (See [Item 32](../../Chapter_05/Item_032/item_032.qmd))
  - For example, accessing a missing key on a dictionary leads to a
    `KeyError`

``` python
my_dict = {}
my_dict["does not exist"]
```

    KeyError: 'does not exist'
    ---------------------------------------------------------------------------
    KeyError                                  Traceback (most recent call last)
    Cell In[1], line 2
          1 my_dict = {}
    ----> 2 my_dict["does not exist"]

    KeyError: 'does not exist'

- As expected can catch the exception (See [Item
  80](../Item_080/item_080.qmd))

``` python
my_dict = {}
try:
    my_dict["does not exist"]
except KeyError:
    print("Could not find key!")
```

    Could not find key!

- If we encounter another exception while handling the first, this will
  distort the output

``` python
class MissingError(Exception):
    pass


my_dict = {}
try:
    my_dict["does not exist"]  # Raises the first exception
except KeyError:
    raise MissingError("Oops")  # Raises second exception
```

    MissingError: Oops
    ---------------------------------------------------------------------------
    KeyError                                  Traceback (most recent call last)
    Cell In[3], line 7
          6 try:
    ----> 7     my_dict["does not exist"]  # Raises the first exception
          8 except KeyError:

    KeyError: 'does not exist'

    During handling of the above exception, another exception occurred:

    MissingError                              Traceback (most recent call last)
    Cell In[3], line 9
          7     my_dict["does not exist"]  # Raises the first exception
          8 except KeyError:
    ----> 9     raise MissingError("Oops")  # Raises second exception

    MissingError: Oops

- The `MissingError` raised in the `except KeyError` block is propagated
  up to the caller
  - But the stack trace includes information about the original
    `KeyError` raised in the `try` block
  - Python assigns an exceptions `__context__` to the exception instance
    being handled by an `except` block
- If we catch both variables, we can see how the exceptions are
  *chained* together

``` python
class MissingError(Exception):
    pass


my_dict = {}
try:
    try:
        my_dict["does not exist"]
    except KeyError:
        raise MissingError("Oops!")
except MissingError as e:
    print("Second:", repr(e))
    print("First: ", repr(e.__context__))
```

    Second: MissingError('Oops!')
    First:  KeyError('does not exist')

- For complex code, manually controlling the chaining process can help
  make the errors clearer
  - This chaining can be achieved via the `from` clause in a `raise`
    statement
- For example, we could implement this into a function `lookup`

``` python
class MissingError(Exception):
    pass


def lookup(my_key):
    try:
        return my_dict[my_key]
    except KeyError:
        raise MissingError


my_dict = {"my key 1": 123}

# Key exists, works
print(lookup("my key 1"))

# Key missing, MissingError exception raised
print(lookup("my key 2"))
```

    123

    MissingError: 
    ---------------------------------------------------------------------------
    KeyError                                  Traceback (most recent call last)
    Cell In[5], line 7, in lookup(my_key)
          6 try:
    ----> 7     return my_dict[my_key]
          8 except KeyError:

    KeyError: 'my key 2'

    During handling of the above exception, another exception occurred:

    MissingError                              Traceback (most recent call last)
    Cell In[5], line 18
         15 print(lookup("my key 1"))
         17 # Key missing, MissingError exception raised
    ---> 18 print(lookup("my key 2"))

    Cell In[5], line 9, in lookup(my_key)
          7     return my_dict[my_key]
          8 except KeyError:
    ----> 9     raise MissingError

    MissingError: 

- We might want to augment the `lookup` function to connect to a remote
  database server
  - This might populate the `my_dict` potentially as a cache when a key
    is missing
  - We’ll create a mock `contact_server` function that mocks this
    behaviour

``` python
def contact_server(my_key):
    print(f"Looking up {my_key!r} in server")
    return "server value"


def lookup(my_key):
    try:
        return my_dict[my_key]
    except KeyError:
        result = contact_server(my_key)
        my_dict[my_key] = result  # Fill the local cache
        return result


my_dict = {}
print("Call 1")
print("Result:", lookup("my key"))
print("Call 2")
print("Result:", lookup("my key"))
```

    Call 1
    Looking up 'my key' in server
    Result: server value
    Call 2
    Result: server value

- Only the first call above results in a server lookup
- However, now imagine that the remote server *does not* have the record
  requested
  - `contact_server` might then raise a new exception to indicate this
    result

``` python
class ServerMissingKeyError(Exception):
    pass


def contact_server(my_key):
    print(f"Looking up {my_key!r} in server")
    raise ServerMissingKeyError


def lookup(my_key):
    try:
        return my_dict[my_key]
    except KeyError:
        result = contact_server(my_key)
        my_dict[my_key] = result  # Fill the local cache
        return result


my_dict = {}
print("Call")
print("Result:", lookup("my key"))
```

    Call
    Looking up 'my key' in server

    ServerMissingKeyError: 
    ---------------------------------------------------------------------------
    KeyError                                  Traceback (most recent call last)
    Cell In[7], line 12, in lookup(my_key)
         11 try:
    ---> 12     return my_dict[my_key]
         13 except KeyError:

    KeyError: 'my key'

    During handling of the above exception, another exception occurred:

    ServerMissingKeyError                     Traceback (most recent call last)
    Cell In[7], line 21
         19 my_dict = {}
         20 print("Call")
    ---> 21 print("Result:", lookup("my key"))

    Cell In[7], line 14, in lookup(my_key)
         12     return my_dict[my_key]
         13 except KeyError:
    ---> 14     result = contact_server(my_key)
         15     my_dict[my_key] = result  # Fill the local cache
         16     return result

    Cell In[7], line 7, in contact_server(my_key)
          5 def contact_server(my_key):
          6     print(f"Looking up {my_key!r} in server")
    ----> 7     raise ServerMissingKeyError

    ServerMissingKeyError: 

- Above mocks the result of the raised exception from a missing record
  - A traceback indicates both the `ServerMissingKeyError` and the
    original `KeyError`
- But this now changes the `lookup` function interface
  - We might want to abstract this by converting a
    `ServerMissingKeyError` into the `MissingError` of the original
    interface
  - For a concrete example of why we might want to do this, it could be
    the case that `ServerMissingKeyError` is an exception defined in a
    dependency we don’t control (See [Item
    121](../../Chapter_14/Item_121/item_121.qmd))
    - E.g. Our database provider

``` python
class ServerMissingKeyError(Exception):
    pass


class MissingError(Exception):
    pass


def contact_server(my_key):
    print(f"Looking up {my_key!r} in server")
    raise ServerMissingKeyError


def lookup(my_key):
    try:
        return my_dict[my_key]
    except KeyError:
        try:
            result = contact_server(my_key)
        except ServerMissingKeyError:
            raise MissingError  # convert the server error
        else:
            my_dict[my_key] = result  # Fill the local cache
            return result


my_dict = {}
print("Call")
print("Result:", lookup("my key"))
```

    Call
    Looking up 'my key' in server

    MissingError: 
    ---------------------------------------------------------------------------
    KeyError                                  Traceback (most recent call last)
    Cell In[8], line 16, in lookup(my_key)
         15 try:
    ---> 16     return my_dict[my_key]
         17 except KeyError:

    KeyError: 'my key'

    During handling of the above exception, another exception occurred:

    ServerMissingKeyError                     Traceback (most recent call last)
    Cell In[8], line 19, in lookup(my_key)
         18 try:
    ---> 19     result = contact_server(my_key)
         20 except ServerMissingKeyError:

    Cell In[8], line 11, in contact_server(my_key)
         10 print(f"Looking up {my_key!r} in server")
    ---> 11 raise ServerMissingKeyError

    ServerMissingKeyError: 

    During handling of the above exception, another exception occurred:

    MissingError                              Traceback (most recent call last)
    Cell In[8], line 29
         27 my_dict = {}
         28 print("Call")
    ---> 29 print("Result:", lookup("my key"))

    Cell In[8], line 21, in lookup(my_key)
         19     result = contact_server(my_key)
         20 except ServerMissingKeyError:
    ---> 21     raise MissingError  # convert the server error
         22 else:
         23     my_dict[my_key] = result  # Fill the local cache

    MissingError: 

- This results in a large traceback showing *three* sequentially raised
  exceptions
  1.  `KeyError` from failed dictionary lookup
  2.  `ServerMissingKeyError` from failed remote lookup
  3.  `MissingError` from conversion of the exception
- This is a lot of noise that might not cleanly convey what has happened
- We could use `from` in combination with `raise` to clean up the trace
  - Here we want to obfuscate the server lookup
  - i.e. Chain the `MissingError` directly to the `KeyError`

``` python
class ServerMissingKeyError(Exception):
    pass


class MissingError(Exception):
    pass


def contact_server(my_key):
    print(f"Looking up {my_key!r} in server")
    raise ServerMissingKeyError


def lookup(my_key):
    try:
        return my_dict[my_key]
    except KeyError as e:
        try:
            result = contact_server(my_key)
        except ServerMissingKeyError:
            raise MissingError from e  # Hide the `ServerMissingKeyError`
        else:
            my_dict[my_key] = result  # Fill the local cache
            return result


my_dict = {}
print("Call")
print("Result:", lookup("my key"))
```

    Call
    Looking up 'my key' in server

    MissingError: 
    ---------------------------------------------------------------------------
    KeyError                                  Traceback (most recent call last)
    Cell In[9], line 16, in lookup(my_key)
         15 try:
    ---> 16     return my_dict[my_key]
         17 except KeyError as e:

    KeyError: 'my key'

    The above exception was the direct cause of the following exception:

    MissingError                              Traceback (most recent call last)
    Cell In[9], line 29
         27 my_dict = {}
         28 print("Call")
    ---> 29 print("Result:", lookup("my key"))

    Cell In[9], line 21, in lookup(my_key)
         19     result = contact_server(my_key)
         20 except ServerMissingKeyError:
    ---> 21     raise MissingError from e  # Hide the `ServerMissingKeyError`
         22 else:
         23     my_dict[my_key] = result  # Fill the local cache

    MissingError: 

- We can see from the stack trace above the `MissingError` is now
  directly connected to the `KeyError`
- While not explicitly printed, the `ServerMissingKeyError` is still
  accessible from the `MissingError` objects context
  - `from` overrides the raised exceptions `__cause__` dunder attribute
    - Set’s it to the provided value
    - Also sets `__suppress_context__` dunder attribute to `True`
- This can be seen below,

``` python
class ServerMissingKeyError(Exception):
    pass


class MissingError(Exception):
    pass


def contact_server(my_key):
    print(f"Looking up {my_key!r} in server")
    raise ServerMissingKeyError


def lookup(my_key):
    try:
        return my_dict[my_key]
    except KeyError as e:
        try:
            result = contact_server(my_key)
        except ServerMissingKeyError:
            raise MissingError from e  # Hide the `ServerMissingKeyError`
        else:
            my_dict[my_key] = result  # Fill the local cache
            return result


my_dict = {}
print("Call")
try:
    print(lookup("my key"))
except Exception as e:
    print("Exception:", repr(e))
    print("Context:  ", repr(e.__context__))
    print("Cause:    ", repr(e.__cause__))
    print("Suppress: ", repr(e.__suppress_context__))
```

    Call
    Looking up 'my key' in server
    Exception: MissingError()
    Context:   ServerMissingKeyError()
    Cause:     KeyError('my key')
    Suppress:  True

- Python’s exception-chain handling infrastructure is a built-in
  - Not something that can be accessed directly
  - Instead use `traceback` (See [Item 87](../Item_087/item_087.qmd))
    - This will miss some information

``` python
import traceback


class ServerMissingKeyError(Exception):
    pass


class MissingError(Exception):
    pass


def contact_server(my_key):
    print(f"Looking up {my_key!r} in server")
    raise ServerMissingKeyError


def lookup(my_key):
    try:
        return my_dict[my_key]
    except KeyError as e:
        try:
            result = contact_server(my_key)
        except ServerMissingKeyError:
            raise MissingError from e  # Hide the `ServerMissingKeyError`
        else:
            my_dict[my_key] = result  # Fill the local cache
            return result


my_dict = {}
print("Call")
try:
    print(lookup("my key"))
except Exception as e:
    stack = traceback.extract_tb(e.__traceback__)
    for frame in stack:
        print(frame.line)
```

    Call
    Looking up 'my key' in server
    print(lookup("my key"))
    raise MissingError from e  # Hide the `ServerMissingKeyError`

- Here we only see the trace up to the point that the propagated
  exception calls
- To extract chained exception information we need to consider the
  `__cause__` and `__context__` attributes
- We can define a function `get_cause`
  - This identifies the cause or context of an exception
  - Could be called recursively or in a loop to walk the full exception
    stack

``` python
import traceback


class ServerMissingKeyError(Exception):
    pass


class MissingError(Exception):
    pass


def contact_server(my_key):
    print(f"Looking up {my_key!r} in server")
    raise ServerMissingKeyError


def lookup(my_key):
    try:
        return my_dict[my_key]
    except KeyError as e:
        try:
            result = contact_server(my_key)
        except ServerMissingKeyError:
            raise MissingError  # Convert the `ServerMissingKeyError`
        else:
            my_dict[my_key] = result  # Fill the local cache
            return result


# Handling the cause
def get_cause(exc):
    if exc.__cause__ is not None:
        return exc.__cause__
    elif not exc.__suppress_context__:
        return exc.__context__
    else:
        return None


my_dict = {}
print("Call")
try:
    print(lookup("my key"))
except Exception as e:
    while e is not None:
        stack = traceback.extract_tb(e.__traceback__)
        for i, frame in enumerate(stack, 1):
            print(i, frame.line)
        e = get_cause(e)
        if e:
            print("Caused by")
```

    Call
    Looking up 'my key' in server
    1 print(lookup("my key"))
    2 raise MissingError  # Convert the `ServerMissingKeyError`
    Caused by
    1 result = contact_server(my_key)
    2 raise ServerMissingKeyError
    Caused by
    1 return my_dict[my_key]

- Another way to shorten the chain would be to cut it off at some point
  - For example we might suppress the `KeyError` and instead report the
    `ServerMissingKeyError`
  - We can do this by using `raise ServerMissingKeyError from None`

``` python
import traceback


class ServerMissingKeyError(Exception):
    pass


class MissingError(Exception):
    pass


def contact_server(my_key):
    print(f"Looking up {my_key!r} in server")
    raise ServerMissingKeyError from None


def lookup(my_key):
    try:
        return my_dict[my_key]
    except KeyError as e:
        try:
            result = contact_server(my_key)
        except ServerMissingKeyError:
            raise MissingError  # Convert the `ServerMissingKeyError`
        else:
            my_dict[my_key] = result  # Fill the local cache
            return result


my_dict = {}
print("Call")
print(lookup("my key"))
```

    Call
    Looking up 'my key' in server

    MissingError: 
    ---------------------------------------------------------------------------
    ServerMissingKeyError                     Traceback (most recent call last)
    Cell In[13], line 22, in lookup(my_key)
         21 try:
    ---> 22     result = contact_server(my_key)
         23 except ServerMissingKeyError:

    Cell In[13], line 14, in contact_server(my_key)
         13 print(f"Looking up {my_key!r} in server")
    ---> 14 raise ServerMissingKeyError from None

    ServerMissingKeyError: 

    During handling of the above exception, another exception occurred:

    MissingError                              Traceback (most recent call last)
    Cell In[13], line 32
         30 my_dict = {}
         31 print("Call")
    ---> 32 print(lookup("my key"))

    Cell In[13], line 24, in lookup(my_key)
         22     result = contact_server(my_key)
         23 except ServerMissingKeyError:
    ---> 24     raise MissingError  # Convert the `ServerMissingKeyError`
         25 else:
         26     my_dict[my_key] = result  # Fill the local cache

    MissingError: 

- We can now see that the `KeyError` is no longer reported in the chain

## Things to Remember

- An exception raised from inside an `except` clause will have the
  original exception set as it’s `__context__` value
- `raise` supports a `from` statement
  - Enables explicitly indicating the previous exception that caused
    this one
- Explicitly chaining exceptions will cause Python to only print the
  provided chain rather than the automatically chained exception
