# Item 87: Use `traceback` for Enhanced Exception Reporting

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Uncaught exceptions propagate up to the entry point of the program
  - Result in exiting with an error code
- The interpreter will print out a *traceback* of the stack trace
  - Aids in identifying the source of the error
- E.g. The below assert (See [Item 81](../Item_081/item_081.qmd))
  demonstrates the trace

``` python
def inner_func(message):
    assert False, message


def outer_func(message):
    inner_func(message)


outer_func("Oops!")
```

    AssertionError: Oops!
    ---------------------------------------------------------------------------
    AssertionError                            Traceback (most recent call last)
    Cell In[1], line 9
          5 def outer_func(message):
          6     inner_func(message)
    ----> 9 outer_func("Oops!")

    Cell In[1], line 6, in outer_func(message)
          5 def outer_func(message):
    ----> 6     inner_func(message)

    Cell In[1], line 2, in inner_func(message)
          1 def inner_func(message):
    ----> 2     assert False, message

    AssertionError: Oops!

- The default behaviour is designed for single-threaded code
  - Can break for concurrent programs (See [Item
    71](../../Chapter_09/Item_071/item_071.qmd))
- Requests on one request can bubble up to the entry point and crash all
  other requests
- One solution is a blanket `try/except` block (See [Item
  85](../Item_085/item_085.qmd) and [Item 86](../Item_086/item_086.qmd))
- The following `request` class mocks this behaviour

``` python
class Request:
    def __init__(self, body):
        self.body = body
        self.response = None


def do_work(data):
    assert False, data


def handle(request):
    try:
        do_work(request.body)
    except BaseException as e:
        print(repr(e))
        request.response = 400  # Bad Request Error


request = Request("My Message")
handle(request)
```

    AssertionError('My Message')

- The string `repr` of an exception loses all the associated stack trace
  information
- We can rectify this with the `traceback` built-in module
  - Allows runtime manipulation of traceback information
  - `print_tb` let’s us print out the stack trace

``` python
import traceback


class Request:
    def __init__(self, body):
        self.body = body
        self.response = None


def do_work(data):
    assert False, data


def handle(request):
    try:
        do_work(request.body)
    except BaseException as e:
        traceback.print_tb(e.__traceback__)  # Changed
        print(repr(e))
        request.response = 400


request = Request("My Message")
handle(request)
```

    AssertionError('My Message')

      File "/tmp/ipykernel_11859/1677808877.py", line 16, in handle
        do_work(request.body)
        ~~~~~~~^^^^^^^^^^^^^^
      File "/tmp/ipykernel_11859/1677808877.py", line 11, in do_work
        assert False, data
               ^^^^^

- The traceback contains more information we can examine
  - File name
  - Line number
  - Source code line
  - Containing function name
- We can use this to dynamically interrogate the stack trace
  - e.g. to display in GUI/TUI
- We could make our `handle` for example list the function names in the
  stack trace

``` python
import traceback


class Request:
    def __init__(self, body):
        self.body = body
        self.response = None


def do_work(data):
    assert False, data


def handle(request):
    try:
        do_work(request.body)
    except BaseException as e:
        stack = traceback.extract_tb(e.__traceback__)  # Changed
        for frame in stack:
            print(frame.name)
        print(repr(e))
        request.response = 400


request = Request("My Message")
handle(request)
```

    handle
    do_work
    AssertionError('My Message')

- We can use `traceback` for more advanced error handling
- For example, we might want to save a log of exceptions encountered in
  a separate file
  - Encoded as one JSON payload per line
  - Can be implemented via a wrapper

``` python
import json
import traceback


class Request:
    def __init__(self, body):
        self.body = body
        self.response = None


def do_work(data):
    assert False, data


def log_if_error(file_path, target, *args, **kwargs):
    try:
        target(*args, **kwargs)
    except BaseException as e:
        stack = traceback.extract_tb(e.__traceback__)
        stack_without_wrapper = stack[1:]
        trace_dict = dict(
            stack=[item.name for item in stack_without_wrapper],
            error_type=type(e).__name__,
            error_message=str(e),
        )
        json_data = json.dumps(trace_dict)

        with open(file_path, "a") as f:
            f.write(json_data)
            f.write("\n")


log_file = "my_log.jsonl"
log_if_error(log_file, do_work, "First error")
log_if_error(log_file, do_work, "Second error")
with open(log_file) as f:
    for line in f:
        print(line, end="")
os.remove(log_file)
```

    {"stack": ["do_work"], "error_type": "AssertionError", "error_message": "First error"}
    {"stack": ["do_work"], "error_type": "AssertionError", "error_message": "Second error"}
    {"stack": ["do_work"], "error_type": "AssertionError", "error_message": "First error"}
    {"stack": ["do_work"], "error_type": "AssertionError", "error_message": "Second error"}

    NameError: name 'os' is not defined
    ---------------------------------------------------------------------------
    NameError                                 Traceback (most recent call last)
    Cell In[5], line 39
         37     for line in f:
         38         print(line, end="")
    ---> 39 os.remove(log_file)

    NameError: name 'os' is not defined

- For more uses of `traceback` including formatting, printing, traversal
  of stack traces consult the
  [docs](https://docs.python.org/3/library/traceback.html)
  - There are some edge cases that must be handled manually (See [Item
    88](../Item_088/item_088.qmd))

## Things to Remember

- Unhandled exceptions propagate up to program entry point
  - Interpreter prints a nicely formatted list of stack frames
- Highly concurrent programs can cause issues with correctly printing
  out a stack trace
- The `traceback` built-in module enables interaction with the stack
  frames
  - You can then perform further processing of the stack trace
