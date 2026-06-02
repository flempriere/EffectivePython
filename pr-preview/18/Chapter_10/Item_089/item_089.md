# Item 89: Always Pass Resources into Generators and have Callers Clean
them up Outside


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Python provides many tools for automatic resource management and
  automatic cleanup
  1.  Exception handlers (See [Item 80](../Item_080/item_080.qmd))
  2.  `with` statements (See [Item 82](../Item_082/item_082.qmd))
  3.  etc..
- For example, we can use a `finally` clause from a `try` to ensure
  something always executes before a function return

``` python
def my_func():
    try:
        return 123
    finally:
        print("Finally my_func")


print("Before")
print(my_func())
print("After")
```

    Before
    Finally my_func
    123
    After

- However, when using a generator (See [Item
  43](../../Chapter_06/Item_043/item_043.qmd)), `finally` only executes
  after the `StopIteration` is raised
  - i.e. Just after all values have been exhausted (See [Item
    21](../../Chapter_03/Item_021/item_021.qmd))
  - So `finally` is executed *after* the last item is received

``` python
def my_generator():
    try:
        yield 10
        yield 20
        yield 30
    finally:
        print("Finally my_generator")


print("Before")
for i in my_generator():
    print(i)

print("After")
```

    Before
    10
    20
    30
    Finally my_generator
    After

- Not all python generators can be exhausted
  - Then a `StopIteration` might never be raised
  - Thus the `finally` clause itself is not raised
- We can simulate this below,

``` python
# Note this cell has mocked output, as it cannot run inside the rendering engine

def my_generator():
    try:
        yield 10
        yield 20
        yield 30
    finally:
        print("Finally my_generator")


it = my_generator()
print("Before")
print(next(it))
print(next(it))
print("After")
```

    Before
    Before
    10
    20
    After

- When will the `finally` be called?
  - Potentially never
  - If the generator is no longer referenced, the garbage collector
    should clean it up (unless disabled)
    - This should call the `finally`

``` python
import gc


def my_generator():
    try:
        yield 10
        yield 20
        yield 30
    finally:
        print("Finally my_generator")


it = my_generator()
print("Before")
print(next(it))
print(next(it))
print("After")

del it
gc.collect()
```

    Before
    10
    20
    After
    Finally my_generator

    0

- This is powered by the `GeneratorExit`exception
  - This inherits from `BaseException` (See [Item
    86](../Item_086/item_086.qmd))
- Python sends this to non-exhausted generators if it’s not exhausted
  (See [Item 46](../../Chapter_06/Item_046/item_046.qmd))
  - Causes the generator to return, clear it’s stack
  - Technically this type of exception can be caught

``` python
import gc


def catching_generator():
    try:
        yield 40
        yield 50
        yield 60
    except BaseException as e:
        print("Catching handler", type(e), e)
        raise


it = catching_generator()
print("Before")
print(next(it))
print(next(it))
print("After")

del it
gc.collect()
```

    Before
    40
    50
    After
    Catching handler <class 'GeneratorExit'> 

    0

- The bare `raise` at the end of the generator’s exception handler
  ensures the `GeneratorExit` exception propagates correctly
  - Prevents the runtime from breaking
- The `gc` runs it’s own exception handler
  - Means we don’t see the full stack trace itself
- What if another exception is raised?

``` python
import gc


def broken_generator():
    try:
        yield 70
        yield 80
    except BaseException as e:
        print("Catching handler", type(e), e)
        raise RuntimeError("Broken")


it = broken_generator()
print("Before")
print(next(it))
print(next(it))
print("After")

del it
gc.collect()
print("Still going")
```

    Exception ignored while closing generator <generator object broken_generator at 0x7fdca4e55120>:
    Traceback (most recent call last):
      File "/tmp/ipykernel_12100/416899508.py", line 10, in broken_generator
    RuntimeError: Broken

    Before
    70
    80
    After
    Catching handler <class 'GeneratorExit'> 
    Still going

- The `gc` module catches the `RuntimeError` as suppresses it
  - It’s printed out to `sys.stderr`
  - Exception does not return to the main thread
  - Swallowed and insulated from the program
- Thus can’t rely on exception handlers or `finally` clauses in
  generators
  - No guarantee they will execute and report errors to the caller
- To prevent this avoid allocating a resource *within* a generator
  - Instead allocate the resources outside the generator and pass them
    in
- For example, we might write a simple utility that finds the maximum
  length of the first five lines in a file
  - Lends itself naturally to using a simple generator
  - In our initial implementation we might be tempted to simply open the
    path with the generator

``` python
import gc


def lengths_path(path):
    try:
        with open(path) as handle:
            for i, line in enumerate(handle):
                print(f"Line {i}")
                yield len(line.strip())

    finally:
        print("Finally lengths_path")


max_head = 0
it = lengths_path("my_file.txt")

for i, length in enumerate(it):
    if i == 5:
        break
    else:
        max_head = max(max_head, length)
print(max_head)

# Simulate going out of scope and being garbage collected
del it
gc.collect()
```

    Line 0
    Line 1
    Line 2
    Line 3
    Line 4
    Line 5
    11
    Finally lengths_path

    0

- The generator can then be consumed by a loop to calculate the maximum
  then terminate
  - We use a `break` to end the loop *before* the generator is executed
- The generator is garbage collected once it goes out of scope
  - `finally` clause then executes
- We triggered it manually in the block above
- What if we want to avoid waiting for the generator to go out of scope
  before performing cleanup?
  - We don’t want to have a loose file handle sitting around longer than
    we need
  - We want the `finally` to run in the original loop call stack
    - Ensures errors are raised at the appropriate point
- For an example of where we might want to ensure this consider a mutex
  lock
  - We need it to be released as soon as possible otherwise the resource
    cannot be accessed
  - If not correctly cleaned up the program might deadlock
- We rework the generator to accept a file handle rather than file path

``` python
def lengths_handle(handle):
    try:
        for i, line in enumerate(handle):
            print(f"Line {i}")
            yield len(line.strip())
    finally:
        print("Finally lengths_handle")


max_head = 0
with open("my_file.txt") as handle:
    # it creation moved into loop to ensure clean-up after loop exits
    for i, length in enumerate(lengths_handle(handle)):
        if i == 5:
            break
        else:
            max_head = max(max_head, length)

print(max_head)
print("Handle closed:", handle.closed)
```

    Line 0
    Line 1
    Line 2
    Line 3
    Line 4
    Line 5
    Finally lengths_handle
    11
    Handle closed: True

- We then wrap the loop and generator in a `with` statement to manage
  the file handler
  - Ensures the file is opened and closed as expected
- The generator itself hasn’t exited
  - But the file handle it’s consuming has been closed out
  - Works because we don’t need the generator itself to do any cleanup
- The `GeneratorExit` exception forces generators to exit eventually
  - Prevents non-exhausted generators from leaking memory
  - The downside is they swallow errors
    - Reasonable most of the time
    - But you need to be aware, so that you can plan around it when
      required

## Things to Remember

- `finally` clauses in functions execute before a function returns
- `finally` clauses in generator functions run after exhaustion
  indicated by `StopIteration`
- The garbage collector injects `GeneratorExit` exceptions to ensure
  cleanup of generators that are no longer in scope and have not been
  exhausted
- Prefer to pass resources into generators to ensure control of cleanup
  rather than assuming the generator will allocate and cleanup
