# Item 83: Always make `try` Blocks as Short as Possible

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Setting up a `try/except` block normally involves a lot of overhead in
  setting up exception handling
  - Making sure the correct exceptions are caught etc. (See [Item
    80](../Item_080/item_080.qmd))
- For example, handling a remote procedure call (RPC) often needs
  exception management

``` python
connection = object()  # mock


class RPCError(Exception):
    pass


def lookup_request(connection):
    raise RPCError("Lookup failed")


def close_connection(connection):
    print("Connection closed")


try:
    request = lookup_request(connection)
except RPCError:
    print("Encountered error!")
    close_connection(connection)
```

    Encountered error!
    Connection closed

- If we later want to add more logic around this `try/except` block,
  natural idea to add code into the `try` section e.g.
  - Special case handling
  - Data processing

``` python
connection = object()  # mock


class RPCError(Exception):
    pass


def lookup_request(connection):
    print("Request looked up")  # Changed
    return object()  # represents request returned


def is_cached(connection, request):  # Added
    raise RPCError("cache failed")


def close_connection(connection):
    print("Connection closed")


try:
    request = lookup_request(connection)
    if is_cached(connection, request):
        request = None
except RPCError:
    print("Encountered error!")
    close_connection(connection)
```

    Request looked up
    Encountered error!
    Connection closed

- Here the `try` block catches both errors
  - But now it’s not clear if the error is from `is_cached` or
    `lookup_request`
- In practice, each source of errors should belong in it’s *own*
  `try/except` block
  - Rest should go in an `else`
    - Useful if we don’t want to catch errors but propagate them
  - If need’s error handling, then it’s own `try/except`

``` python
connection = object()  # mock


class RPCError(Exception):
    pass


def lookup_request(connection):
    print("Request looked up")  # Changed
    return object()  # represents request returned


def is_cached(connection, request):  # Added
    raise RPCError("cache failed")


def close_connection(connection):
    print("Connection closed")


try:
    request = lookup_request(connection)
except RPCError:
    print("Encountered error!")
    close_connection(connection)
else:  # `is_cached` now raises the error
    if is_cached(connection, request):  # Moved
        request = None
```

    Request looked up

    RPCError: cache failed
    ---------------------------------------------------------------------------
    RPCError                                  Traceback (most recent call last)
    Cell In[3], line 27
         25     close_connection(connection)
         26 else:  # `is_cached` now raises the error
    ---> 27     if is_cached(connection, request):  # Moved
         28         request = None

    Cell In[3], line 14, in is_cached(connection, request)
         13 def is_cached(connection, request):  # Added
    ---> 14     raise RPCError("cache failed")

    RPCError: cache failed

- Ensures you only catch the exceptions you intend to catch
- Can also work out *what* is the source of the exception

## Things to Remember

- Large `try` blocks can catch unexpected exceptions
- Prefer multiple `try` blocks to distinguish the source of exceptions
- Use `try/else` when multiple methods can raise exceptions, but only a
  subset of them should be caught
