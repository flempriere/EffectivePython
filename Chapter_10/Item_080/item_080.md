# Item 80: Take Advantage of Each Block in `try/except/else/finally`


- [Notes](#notes)
  - [`finally` Blocks](#finally-blocks)
  - [`else` Blocks](#else-blocks)
  - [Everything Together](#everything-together)
- [Things to Remember](#things-to-remember)

## Notes

- Exception handling comprises four time blocks in which action might
  want to be taken
  - `try`, `except`, `else`, `finally`

### `finally` Blocks

- `finally` lets you run cleanup code while allowing exceptions to
  propagate up
- This is useful for cleaning up contextual objects like file handles
  (See [Item 82](../Item_082/item_082.qmd))
- Any exception raised propagates up to the calling code
  - But `finally` block runs first

``` python
import os


def try_finally_example(filename):
    print("* Opening a file")

    handle = open(filename, encoding="utf-8")  # May Raise OSError
    try:
        print("* Reading data")
        return handle.read()  # May raise UnicodeDecodeError
    finally:
        print("* Calling close()")
        handle.close()  # Always run after try block
        os.remove(filename)  # Clean up - purely here for the example


filename = "random_data.txt"

with open(filename, "wb") as f:
    f.write(b"\xf1\xf2\xf3\xf4\xf5")  # Invalid utf-8

data = try_finally_example(filename)
```

    * Opening a file
    * Reading data
    * Calling close()

    UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf1 in position 0: invalid continuation byte
    ---------------------------------------------------------------------------
    UnicodeDecodeError                        Traceback (most recent call last)
    Cell In[1], line 22
         19 with open(filename, "wb") as f:
         20     f.write(b"\xf1\xf2\xf3\xf4\xf5")  # Invalid utf-8
    ---> 22 data = try_finally_example(filename)

    Cell In[1], line 10, in try_finally_example(filename)
          8 try:
          9     print("* Reading data")
    ---> 10     return handle.read()  # May raise UnicodeDecodeError
         11 finally:
         12     print("* Calling close()")

    File <frozen codecs>:325, in BufferedIncrementalDecoder.decode(self, input, final)
        322 def decode(self, input, final=False):
        323     # decode input (taking the buffer into account)
        324     data = self.buffer + input
    --> 325     (result, consumed) = self._buffer_decode(data, self.errors, final)
        326     # keep undecoded input until the next call
        327     self.buffer = data[consumed:]

    UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf1 in position 0: invalid continuation byte

- In the above example, we call `open` before the `try` block to prevent
  exceptions during `open` from triggering the `finally` block
  - This would lead to `close()` being called on an unopened file handle

### `else` Blocks

- `try/except/else` makes it clear which exceptions are handled
- When no exception is raised by a `try` then the `else` block runs
- `else` block allows minimising the code in the `try` block
  - Can isolate the `try` to the specific exception-raising code
  - Improves readability (See [Item 83](../Item_083/item_083.qmd))
- For example, consider loading JSON dictionary data

``` python
import json


def load_json_key(data, key):
    try:
        print("* Loading JSON data")
        result_dict = json.loads(data)  # May raise ValueError
    except ValueError:
        print("* Handling ValueError")
        raise KeyError(key)
    else:
        print("* Looking up key")
        return result_dict[key]  # May raise KeyError


# Successful case
assert load_json_key('{"foo": "bar"}', "foo") == "bar"
print("Successfully loaded the key")

# Except block catch
load_json_key('{"foo": bad payload', "foo")
```

    * Loading JSON data
    * Looking up key
    Successfully loaded the key
    * Loading JSON data
    * Handling ValueError

    KeyError: 'foo'
    ---------------------------------------------------------------------------
    JSONDecodeError                           Traceback (most recent call last)
    Cell In[2], line 7, in load_json_key(data, key)
          6     print("* Loading JSON data")
    ----> 7     result_dict = json.loads(data)  # May raise ValueError
          8 except ValueError:

    File /opt/hostedtoolcache/Python/3.14.5/x64/lib/python3.14/json/__init__.py:352, in loads(s, cls, object_hook, parse_float, parse_int, parse_constant, object_pairs_hook, **kw)
        349 if (cls is None and object_hook is None and
        350         parse_int is None and parse_float is None and
        351         parse_constant is None and object_pairs_hook is None and not kw):
    --> 352     return _default_decoder.decode(s)
        353 if cls is None:

    File /opt/hostedtoolcache/Python/3.14.5/x64/lib/python3.14/json/decoder.py:345, in JSONDecoder.decode(self, s, _w)
        341 """Return the Python representation of ``s`` (a ``str`` instance
        342 containing a JSON document).
        343 
        344 """
    --> 345 obj, end = self.raw_decode(s, idx=_w(s, 0).end())
        346 end = _w(s, end).end()

    File /opt/hostedtoolcache/Python/3.14.5/x64/lib/python3.14/json/decoder.py:363, in JSONDecoder.raw_decode(self, s, idx)
        362 except StopIteration as err:
    --> 363     raise JSONDecodeError("Expecting value", s, err.value) from None
        364 return obj, end

    JSONDecodeError: Expecting value: line 1 column 9 (char 8)

    During handling of the above exception, another exception occurred:

    KeyError                                  Traceback (most recent call last)
    Cell In[2], line 21
         18 print("Successfully loaded the key")
         20 # Except block catch
    ---> 21 load_json_key('{"foo": bad payload', "foo")

    Cell In[2], line 10, in load_json_key(data, key)
          8 except ValueError:
          9     print("* Handling ValueError")
    ---> 10     raise KeyError(key)
         11 else:
         12     print("* Looking up key")

    KeyError: 'foo'

- On success, decode the json in the `try` block
  - Then perform lookup in the `else` block
- If input can’t be decoded as JSON
  - Then the `except` catches the `ValueError` and handles the exception
- If the JSON is decoded successfully, but the lookup then raises an
  exception
  - Outside the `try` block
  - Propagates to the caller

### Everything Together

- Use `try/except/else/finally` all together to combine behaviours
- For example we might want to
  1.  Read from a file
  2.  Process the file
  3.  Update the file
- Use `try` to read and process
- `except` handles exceptions
- `else` performs the update
- `finally` ensures the file handle is cleaned up

``` python
import json

UNDEFINED = object()


def divide_json(path):
    print("* Opening file")
    handle = open(path, "r+")  # May raise OSError
    try:
        print("* Reading data")
        data = handle.read()
        print("* Loading JSON data")  # May raise UnicodeDecodeError
        op = json.loads(data)  # May raise ValueError
        print("* Performing calculation")
        value = op["numerator"] / op["denominator"]  # May raise ZeroDivideError
    except ZeroDivisionError:
        print("* Handling ZeroDivisionError")
        return UNDEFINED
    else:
        print("* Writing Calculation")
        op["result"] = value
        result = json.dumps(op)
        handle.seek(0)  # May raise OSError
        handle.write(result)  # May raise OSError
        return value
    finally:
        print("* Calling close()")
        handle.close()


temp_path = "random_data.json"

with open(temp_path, "w") as f:
    f.write('{"numerator": 1, "denominator": 10}')

# valid, try, else, finally runs
print("Valid - try, else, finally runs")
assert divide_json(temp_path) == 0.1

# invalid, but handled, try, except, finally runs
print("Invalid but handled - try, except, finally runs")
with open(temp_path, "w") as f:
    f.write('{"numerator": 1, "denominator": 0}')

assert divide_json(temp_path) is UNDEFINED

# invalid json, try, finally runs
print("Invalid, not handled - try, finally runs")
with open(temp_path, "w") as f:
    f.write('{"numerator": 1 bad data}')

divide_json(temp_path)
```

    Valid - try, else, finally runs
    * Opening file
    * Reading data
    * Loading JSON data
    * Performing calculation
    * Writing Calculation
    * Calling close()
    Invalid but handled - try, except, finally runs
    * Opening file
    * Reading data
    * Loading JSON data
    * Performing calculation
    * Handling ZeroDivisionError
    * Calling close()
    Invalid, not handled - try, finally runs
    * Opening file
    * Reading data
    * Loading JSON data
    * Calling close()

    JSONDecodeError: Expecting ',' delimiter: line 1 column 17 (char 16)
    ---------------------------------------------------------------------------
    JSONDecodeError                           Traceback (most recent call last)
    Cell In[3], line 52
         49 with open(temp_path, "w") as f:
         50     f.write('{"numerator": 1 bad data}')
    ---> 52 divide_json(temp_path)

    Cell In[3], line 13, in divide_json(path)
         11 data = handle.read()
         12 print("* Loading JSON data")  # May raise UnicodeDecodeError
    ---> 13 op = json.loads(data)  # May raise ValueError
         14 print("* Performing calculation")
         15 value = op["numerator"] / op["denominator"]  # May raise ZeroDivideError

    File /opt/hostedtoolcache/Python/3.14.5/x64/lib/python3.14/json/__init__.py:352, in loads(s, cls, object_hook, parse_float, parse_int, parse_constant, object_pairs_hook, **kw)
        347     s = s.decode(detect_encoding(s), 'surrogatepass')
        349 if (cls is None and object_hook is None and
        350         parse_int is None and parse_float is None and
        351         parse_constant is None and object_pairs_hook is None and not kw):
    --> 352     return _default_decoder.decode(s)
        353 if cls is None:
        354     cls = JSONDecoder

    File /opt/hostedtoolcache/Python/3.14.5/x64/lib/python3.14/json/decoder.py:345, in JSONDecoder.decode(self, s, _w)
        340 def decode(self, s, _w=WHITESPACE.match):
        341     """Return the Python representation of ``s`` (a ``str`` instance
        342     containing a JSON document).
        343 
        344     """
    --> 345     obj, end = self.raw_decode(s, idx=_w(s, 0).end())
        346     end = _w(s, end).end()
        347     if end != len(s):

    File /opt/hostedtoolcache/Python/3.14.5/x64/lib/python3.14/json/decoder.py:361, in JSONDecoder.raw_decode(self, s, idx)
        352 """Decode a JSON document from ``s`` (a ``str`` beginning with
        353 a JSON document) and return a 2-tuple of the Python
        354 representation and the index in ``s`` where the document ended.
       (...)    358 
        359 """
        360 try:
    --> 361     obj, end = self.scan_once(s, idx)
        362 except StopIteration as err:
        363     raise JSONDecodeError("Expecting value", s, err.value) from None

    JSONDecodeError: Expecting ',' delimiter: line 1 column 17 (char 16)

- On success, the `try`, `else` then `finally` block runs
- On a handled exception the `try`, `except`, `finally` block runs
- On an unhandled exception the `try`, `finally` block runs
- Has the advantage that blocks intuitively work together
  - Exceptions raised in the `else` are those clearly not expected to be
    handled

## Things to Remember

- The `try/finally` block lets you run code after a `try` block
  regardless of if an exception was raised
- The `else` block minimises code in a `try` block
  - Distinguishes a successful case from a `try/except`
- An `else` lets you perform additional actions after a successful `try`
  block
  - Runs before a common cleanup in a `finally` block
