# Item 77: Mix Threads and Coroutines to Ease the Transition to

`asyncio`

- [Notes](#notes)
  - [Top-Down Approach](#top-down-approach)
  - [Bottom-up Approach](#bottom-up-approach)
- [Things to Remember](#things-to-remember)

## Notes

- The previous [item](../Item_076/item_076.qmd) demonstrated how to port
  a relatively small self-contained program from threading to
  asynchronous programming
- With larger programs, they generally have to be ported incrementally
  - Often have to update tests along the way and verify preserved
    behaviour
- The issue with doing so is having intermediate code that has to
  intermix both blocking I/O and asynchronous I/O (See [Item
  68](../Item_068/item_068.qmd) and [Item 75](../Item_075/item_075.qmd))
  - Means we have to threads that can run coroutines and,
  - Coroutines that can run thread
- `asyncio` provides built-in support for interoperability
- For example, consider a program that merges log files into a single
  output stream
  - Useful for aiding with debugging
- Given an input file handle
  - Need to detect if new data is available
  - Then read that input
  - The `tell` method checks where a file handle is in a file
    - Can use to check if this matches the length of the file
  - When no data is present, we raise an exception (See [Item
    32](../../Chapter_05/Item_032/item_032.qmd))

``` python
class NoNewData(Exception):
    pass


def readline(handle):
    offset = handle.tell()  # Get the current handle offset
    handle.seek(0, 2)  # move forward to end of file
    length = handle.tell()  # get the length of the file

    if length == offset:
        raise NoNewData

    handle.seek(offset, 0)  # move the handle back to where it was
    return handle.readline()  # read the line


# demonstrate via reading from a single line file
with open("input_line.txt", "r") as f:
    print("First line:", readline(f))
    print("Trying to read a second line:", readline(f))
```

    First line: This is a line

    NoNewData:
    ---------------------------------------------------------------------------
    NoNewData                                 Traceback (most recent call last)
    Cell In[1], line 20
         18 with open("input_line.txt", "r") as f:
         19     print("First line:", readline(f))
    ---> 20     print("Trying to read a second line:", readline(f))

    Cell In[1], line 11, in readline(handle)
          8 length = handle.tell()  # get the length of the file
         10 if length == offset:
    ---> 11     raise NoNewData
         13 handle.seek(offset, 0)  # move the handle back to where it was
         14 return handle.readline()

    NoNewData:

- We want to provide a loop construct around the above function so that
  we can offload the work to a thread
- This construct needs to
  1. Accept an input file
      - Specifically a file handle
  2. loop to be able to wait on input
      - We’ll use a simple `while` loop
      - Run as long as the file is open
  3. Need to be able to write to an output file
      - Could hardcode this
        - Would then take an output file
      - Instead, we’ll use a callback function that controls how to
        write the line (See [Item
        48](../../Chapter_07/Item_048/item_048.qmd))
- We’ll also accept a sleep `interval` parameter to limit the amount of
  busy waiting

``` python
import time

def tail_file(handle, interval, write_func):
    while not handle.closed:
        try:
            line = readline(handle)
        except NoNewData:
            time.sleep(interval)
        else:
            write_func(line)
```

- Traditional fan-out would be to listen to each input file on a
  distinct worker thread
  - fan-in into a single output file
- We can do this with a closure (See [Item
  33](../../Chapter_05/Item_033/item_033.qmd))
  - Need to take care to use a lock on the output file for data
    integrity (See [Item 69](../Item_069/item_069.qmd))
  - Can then serialise writes to the output file
  - Then simply have to spin up the threads and then wait on them via
    `join`
- `run_threads` keeps running while any worker thread is still active
  - Threads stay alive until their input file is closed
  - Closing the file is controlled by the external environment
- The basic test framework is based on that provided in the [original
  example code](../../effectivepython/example_code/item_077.py)
  - `write_random_data` is a simple function to generate test data
    - Uses a weighted coin toss to determine the number of lines to
      write
    - Then simply,
      1. Sleeps for an `interval`
      2. Writes a line containing the file path, the line number and a
          random ascii string
      3. Ensures the data is encoded and flushed
  - `start_write_threads` sets up threads to write a number of random
    files
    - Takes a directory to write them to
    - Takes the number of files to write
      - Ensures the files exist
    - Starts a thread to write the random data to each file
    - Returns a list containing the names of the written files
  - `close_all` takes a list of file handles and after a pre-determined
    wait period, closes them all
    - Here one second
    - Performs the external handle shut down for `run_threads`
  - `setup` configures a temporary directory to generate and run the
    tests in
    - Temporary directory ensures that all the test data is cleaned up
      after execution
    - Then calls `start_write_threads` to start writing the test data
    - Then for each written file, opens a new handle
      - These are to be used by the `run_thread` function to delegate
        files to worker threads
    - Then calls `close_all` to ensure after a certain period of time
      the file handles are closed
      - Sufficiently long that the files should all have been completely
        written too
      - We run this in a separate thread so that other work can continue
- The actual test code is `confirm_merge`
  - Takes in a list of the input file paths
  - We then use two defaultdict’s using the `list` function to build an
    `expected` and `found` dictionary
    - The `found` dictionary is constructed by reading the generated
      output file
      - For each line in the output we try and see if it matches any
        lines in any of the input files
      - We then append it to the dictionary such that the structure
        means that each input path is a key to the list of its lines
        that are found in the output
    - The `expected` dictionary works similarly
      - For each input file, we create a list of it’s line
  - We then confirm that the `found` dictionary matches the `expected`
    dictionary
- To execute the test we do the following,
  1. run `setup`
  2. run `run_threads` (this is the code we’re testing)
  3. run `confirm_merge` to confirm that `run_threads` correctly merged
      into the merge file
  4. Cleanup the temporary directory

``` python
import collections # for testing
import os # for testing
import random # for testing
import string # for testing
from tempfile import TemporaryDirectory # for testing
# For actual implementation
import time
from threading import Thread, Lock

#  Run the threads
def run_threads(handles, interval, output_path):
    with open(output_path, "wb") as output:
        lock = Lock()

        # closure function
        def write(data):
            with lock:
                output.write(data)

        threads = []
        for handle in handles:
            args = (handle, interval, write)
            thread = Thread(target=tail_file, args=args)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
# Previous API
class NoNewData(Exception):
    pass


def readline(handle):
    offset = handle.tell()  # Get the current handle offset
    handle.seek(0, 2)  # move forward to end of file
    length = handle.tell()  # get the length of the file

    if length == offset:
        raise NoNewData

    handle.seek(offset, 0)  # move the handle back to where it was
    return handle.readline()  # read the line

def tail_file(handle, interval, write_func):
    while not handle.closed:
        try:
            line = readline(handle)
        except NoNewData:
            time.sleep(interval)
        else:
            write_func(line)

# Testing the implementation
def write_random_data(path, interval):
    with open(path, "wb") as f:
        i = 0
        while random.random() < 0.25:
            i += 1
            time.sleep(random.random() * interval)
            letters = random.choices(string.ascii_lowercase, k=10)
            data = f"{path}-{i:02}-{"".join(letters)}\n"
            f.write(data.encode())
            f.flush()

def start_write_threads(directory, file_count):
    paths = []
    for i in range(file_count):
        path = os.path.join(directory, str(i))
        with open(path, "w"):
            pass # ensures file created
        paths.append(path)
        args = (path, 0.1)
        thread = Thread(target=write_random_data, args=args)
        thread.start()
    return paths

def close_all(handles):
    time.sleep(1)
    for handle in handles:
        handle.close()

def setup():
    tmpdir = TemporaryDirectory()
    input_paths = start_write_threads(tmpdir.name, 5)

    handles = []
    for path in input_paths:
        handle = open(path, "rb")
        handles.append(handle)

    Thread(target=close_all, args=(handles,)).start()
    output_path = os.path.join(tmpdir.name, "merged")
    return tmpdir, input_paths, handles, output_path

def confirm_merge(input_paths, output_path):
    found = collections.defaultdict(list)
    with open(output_path, "rb") as f:
        for line in f:
            for path in input_paths:
                if line.find(path.encode()) == 0:
                    found[path].append(line)

    expected = collections.defaultdict(list)
    for path in input_paths:
        with open(path, "rb") as f:
            expected[path].extend(f.readlines())

    for key, expected_lines in expected.items():
        found_lines = found[key]
        assert (
            expected_lines == found_lines
        ), f"{expected_lines!r} == {found_lines!r}"

tmpdir, input_paths, handles, output_path = setup()

run_threads(handles, 0.1, output_path)

confirm_merge(input_paths, output_path)

tmpdir.cleanup()
```

- The goal is again to convert this code over to use an `async`
  framework
- Can do this either,
  1. top-down
  2. bottom-up

### Top-Down Approach

- Here we start at the high level architecture of the code
  - Work down from `main` and other entry points
  - Finish with the leaf classes and functions
- Approach useful when maintaining common modules used across multiple
  programs
  - Porting the entry points minimises the breaking changes associated
    with migrating the common
    - Rather than breaking all programs immediately, we prime programs
      so we can change the common
- Concrete steps
  1. Change top level function to use `async def`
  2. Wrap all I/O calls to use `asyncio.run_in_executor`
      - These I/O calls may block the event loop
  3. Ensure synchronisation of resources used in `run_in_executor`
      - Either via `Lock` or `asyncio.run_coroutine_threadsafe`
      - Use a fan-in event instance
  4. Aim to eliminate `get_event_loop` and `run_in_executor` calls
      - Move down the hierarchy
      - Convert intermediate functions and methods to coroutines
        - Where they consume or perform I/O
- For Example, to rewrite `run_threads`

``` python
import asyncio

async def run_tasks_mixed(handles, interval, output_path):
    loop = asyncio.get_event_loop()

    output = await loop.run_in_executor(None, open, output_path, "wb")
    try:
        async def write_async(data):
            await loop.run_in_executor(None, output.write, data)

        def write(data):
            coro = write_async(data)
            future = asyncio.run_coroutine_threadsafe(coro, loop)
            future.result()

        tasks = []
        for handle in handles:
            task = loop.run_in_executor(None, tail_file, handle, interval, write)
            tasks.append(task)

        await asyncio.gather(*tasks)

    finally:
        await loop.run_in_executor(None, output.close)
```

- `run_in_executor` places a function call on the event loop
  - Function is run via a `ThreadPoolExecutor` (See [Item
    74](../Item_074/item_074.qmd))
  - This makes sure that it doesn’t contaminate the event loop thread
- Multiple calls to `run_in_executor` without an `await` result in
  `run_tasks_mixed` fanning-out the execution
  - Leads to concurrent lines of work
  - Up to one for each input file
- `asyncio.gather` fans in `tail_file`threads (See [Item
  71](../Item_071/item_071.qmd))
- No longer have a need for a `Lock` in the write
  - Instead we use `asyncio.run_coroutine_threadsafe`
  - Let’s a thread call a coroutine
    - Here `write_async`
    - Coroutine executes in the supplied event loop
      - Here of the main routine
      - All coroutines executing in the same event loop effectively
        synchronises them
      - Writes occur one at a time
  - Once the `asyncio.TaskGroup` awaitable is resolved can assume all
    output files have also completed
    - Can then close the output file handle
    - No need to worry about race conditions
- Then need to verify that the program still works as expected
  - We can reuse our existing test harness

``` python
import collections # for testing
import os # for testing
import random # for testing
import string # for testing
from tempfile import TemporaryDirectory # for testing
from threading import Thread # for testing

# For actual implementation
import asyncio
import time


#  Top Down async refactor
async def run_tasks_mixed(handles, interval, output_path):
    loop = asyncio.get_event_loop() # gets the event loop to pass to run_coroutine_threadsafe

    output = await loop.run_in_executor(None, open, output_path, "wb")
    try:
        async def write_async(data):
            await loop.run_in_executor(None, output.write, data) # asunc write implementation

        def write(data): # tail file still expects a normal function so have to create a wrapper
            coro = write_async(data)
            future = asyncio.run_coroutine_threadsafe(coro, loop)
            future.result()

        tasks = []
        for handle in handles:
            task = loop.run_in_executor(None, tail_file, handle, interval, write)
            tasks.append(task) # async run tail_file

        await asyncio.gather(*tasks) # join the results

    finally:
        await loop.run_in_executor(None, output.close) # no longer context managed so have to close manually

# Previous API
class NoNewData(Exception):
    pass


def readline(handle):
    offset = handle.tell()  # Get the current handle offset
    handle.seek(0, 2)  # move forward to end of file
    length = handle.tell()  # get the length of the file

    if length == offset:
        raise NoNewData

    handle.seek(offset, 0)  # move the handle back to where it was
    return handle.readline()  # read the line

def tail_file(handle, interval, write_func):
    while not handle.closed:
        try:
            line = readline(handle)
        except NoNewData:
            time.sleep(interval)
        else:
            write_func(line)

# Testing the implementation
def write_random_data(path, interval):
    with open(path, "wb") as f:
        i = 0
        while random.random() < 0.25:
            i += 1
            time.sleep(random.random() * interval)
            letters = random.choices(string.ascii_lowercase, k=10)
            data = f"{path}-{i:02}-{"".join(letters)}\n"
            f.write(data.encode())
            f.flush()

def start_write_threads(directory, file_count):
    paths = []
    for i in range(file_count):
        path = os.path.join(directory, str(i))
        with open(path, "w"):
            pass # ensures file created
        paths.append(path)
        args = (path, 0.1)
        thread = Thread(target=write_random_data, args=args)
        thread.start()
    return paths

def close_all(handles):
    time.sleep(1)
    for handle in handles:
        handle.close()

def setup():
    tmpdir = TemporaryDirectory()
    input_paths = start_write_threads(tmpdir.name, 5)

    handles = []
    for path in input_paths:
        handle = open(path, "rb")
        handles.append(handle)

    Thread(target=close_all, args=(handles,)).start()
    output_path = os.path.join(tmpdir.name, "merged")
    return tmpdir, input_paths, handles, output_path

def confirm_merge(input_paths, output_path):
    found = collections.defaultdict(list)
    with open(output_path, "rb") as f:
        for line in f:
            for path in input_paths:
                if line.find(path.encode()) == 0:
                    found[path].append(line)

    expected = collections.defaultdict(list)
    for path in input_paths:
        with open(path, "rb") as f:
            expected[path].extend(f.readlines())

    for key, expected_lines in expected.items():
        found_lines = found[key]
        assert (
            expected_lines == found_lines
        ), f"{expected_lines!r} == {found_lines!r}"

tmpdir, input_paths, handles, output_path = setup()

# outside of jupyter note book replace await with asyncio.run()
await run_tasks_mixed(handles, 0.1, output_path)

confirm_merge(input_paths, output_path)

tmpdir.cleanup()
```

- Now we want to repeat the process, moving further down the tech stack
- Next functions to modify is `tail_file`
  - We write a new `tail_file_async`
    - Changes are
      1. Now call `readline` asynchronously via `run_in_executor`
      2. Replace `time.sleep` with the async, `asyncio.sleep`
      3. `await` on the call to `write_func`
          - i.e. promote the received function handle to a coroutine
            handle
- With those changes can then update `run_tasks_mixed`
  - No longer a need to use `run_coroutine_threadsafe`
  - No longer need to use the `write` wrapper
    - Can pass the coroutine directly
  - Now use `asyncio.TaskGroup` to handle fan-out/in of `tail_async`
    (available since Python 3.11)

``` python
import collections # for testing
import os # for testing
import random # for testing
import string # for testing
from tempfile import TemporaryDirectory # for testing
from threading import Thread # for testing

# For actual implementation
import asyncio
import time


#  Top Down async refactor stage 2
async def run_tasks(handles, interval, output_path):
    loop = asyncio.get_event_loop()

    output = await loop.run_in_executor(None, open, output_path, "wb")
    try:
        async def write_async(data):
            await loop.run_in_executor(None, output.write, data)

        async with asyncio.TaskGroup() as group:
            for handle in handles:
                group.create_task(tail_async(handle, interval, write_async))
    finally:
        await loop.run_in_executor(None, output.close)

# Previous API
class NoNewData(Exception):
    pass


def readline(handle):
    offset = handle.tell()  # Get the current handle offset
    handle.seek(0, 2)  # move forward to end of file
    length = handle.tell()  # get the length of the file

    if length == offset:
        raise NoNewData

    handle.seek(offset, 0)  # move the handle back to where it was
    return handle.readline()  # read the line

async def tail_async(handle, interval, write_func): # change to async def
    loop = asyncio.get_event_loop() # get the event loop
    while not handle.closed:
        try:
            line = await loop.run_in_executor(None, readline, handle)
        except NoNewData:
            await asyncio.sleep(interval)
        else:
            await write_func(line)

# Testing the implementation
def write_random_data(path, interval):
    with open(path, "wb") as f:
        i = 0
        while random.random() < 0.25:
            i += 1
            time.sleep(random.random() * interval)
            letters = random.choices(string.ascii_lowercase, k=10)
            data = f"{path}-{i:02}-{"".join(letters)}\n"
            f.write(data.encode())
            f.flush()

def start_write_threads(directory, file_count):
    paths = []
    for i in range(file_count):
        path = os.path.join(directory, str(i))
        with open(path, "w"):
            pass # ensures file created
        paths.append(path)
        args = (path, 0.1)
        thread = Thread(target=write_random_data, args=args)
        thread.start()
    return paths

def close_all(handles):
    time.sleep(1)
    for handle in handles:
        handle.close()

def setup():
    tmpdir = TemporaryDirectory()
    input_paths = start_write_threads(tmpdir.name, 5)

    handles = []
    for path in input_paths:
        handle = open(path, "rb")
        handles.append(handle)

    Thread(target=close_all, args=(handles,)).start()
    output_path = os.path.join(tmpdir.name, "merged")
    return tmpdir, input_paths, handles, output_path

def confirm_merge(input_paths, output_path):
    found = collections.defaultdict(list)
    with open(output_path, "rb") as f:
        for line in f:
            for path in input_paths:
                if line.find(path.encode()) == 0:
                    found[path].append(line)

    expected = collections.defaultdict(list)
    for path in input_paths:
        with open(path, "rb") as f:
            expected[path].extend(f.readlines())

    for key, expected_lines in expected.items():
        found_lines = found[key]
        assert (
            expected_lines == found_lines
        ), f"{expected_lines!r} == {found_lines!r}"

tmpdir, input_paths, handles, output_path = setup()

# outside of jupyter note book replace await with asyncio.run()
await run_tasks(handles, 0.1, output_path)

confirm_merge(input_paths, output_path)

tmpdir.cleanup()
```

- The next step if one was to continue would be to port `readline`
- Almost every step in `readline` is blocking I/O
  - Not clear doing so would be an improvement
  - Likely loss of clarity

### Bottom-up Approach

- Alternative approach is bottom-up
- We again have four steps but reverse the direction
  - Go from leaves up

1. Create asynchronous version of each leaf function being ported
2. Change synchronous functions to be able to call coroutine versions
    and run event loop
    - Does not implement real asynchronous behaviour at this time
3. Move up the hierarchy
    - Make this layer coroutines
    - Again replace synchronous functions
4. Delete synchronous wrappers around coroutines at the previous layer

- If as above we decide that we don’t want to rewrite `readline` we
  would start at `tail_file`
  - `tail_file` now acts as a wrapper around `tail_async` hiding the
    coroutine
  - `write_func` which must be a function not a coroutine can then be
    run by `write_async` via `run_in_executor`
  - We create an event loop for each `tail_file` thead to ensure worker
    coroutine runs until completion
    - Do so via the `run_until_complete`
    - blocks the current thread and drives event loop until the
      coroutine exits
      - Acts like the equivalent threaded, blocking I/O version

``` python
import asyncio

def tail_file(handle, interval, write_func):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def write_async(data):
        await loop.run_in_executor(None, write_func, data)

    coro = tail_async(handle, interval, write_async)
    loop.run_until_complete(coro)
```

- We can plug this in and run our test harness

``` python
import collections # for testing
import os # for testing
import random # for testing
import string # for testing
from tempfile import TemporaryDirectory # for testing
# For actual implementation
import asyncio
import time
from threading import Thread, Lock

# Rewritten with bottom-up refactor to async

#  Run the threads
def run_threads(handles, interval, output_path):
    with open(output_path, "wb") as output:
        lock = Lock()

        # closure function
        def write(data):
            with lock:
                output.write(data)

        threads = []
        for handle in handles:
            args = (handle, interval, write)
            thread = Thread(target=tail_file, args=args)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
# Previous API
class NoNewData(Exception):
    pass


def readline(handle):
    offset = handle.tell()  # Get the current handle offset
    handle.seek(0, 2)  # move forward to end of file
    length = handle.tell()  # get the length of the file

    if length == offset:
        raise NoNewData

    handle.seek(offset, 0)  # move the handle back to where it was
    return handle.readline()  # read the line

# Changed to wrap async implementation
def tail_file(handle, interval, write_func):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def write_async(data):
        await loop.run_in_executor(None, write_func, data)

    coro = tail_async(handle, interval, write_async)
    loop.run_until_complete(coro)

# async tail_file iimplementation
async def tail_async(handle, interval, write_func): # change to async def
    loop = asyncio.get_event_loop() # get the event loop
    while not handle.closed:
        try:
            line = await loop.run_in_executor(None, readline, handle)
        except NoNewData:
            await asyncio.sleep(interval)
        else:
            await write_func(line)

# Testing the implementation
def write_random_data(path, interval):
    with open(path, "wb") as f:
        i = 0
        while random.random() < 0.25:
            i += 1
            time.sleep(random.random() * interval)
            letters = random.choices(string.ascii_lowercase, k=10)
            data = f"{path}-{i:02}-{"".join(letters)}\n"
            f.write(data.encode())
            f.flush()

def start_write_threads(directory, file_count):
    paths = []
    for i in range(file_count):
        path = os.path.join(directory, str(i))
        with open(path, "w"):
            pass # ensures file created
        paths.append(path)
        args = (path, 0.1)
        thread = Thread(target=write_random_data, args=args)
        thread.start()
    return paths

def close_all(handles):
    time.sleep(1)
    for handle in handles:
        handle.close()

def setup():
    tmpdir = TemporaryDirectory()
    input_paths = start_write_threads(tmpdir.name, 5)

    handles = []
    for path in input_paths:
        handle = open(path, "rb")
        handles.append(handle)

    Thread(target=close_all, args=(handles,)).start()
    output_path = os.path.join(tmpdir.name, "merged")
    return tmpdir, input_paths, handles, output_path

def confirm_merge(input_paths, output_path):
    found = collections.defaultdict(list)
    with open(output_path, "rb") as f:
        for line in f:
            for path in input_paths:
                if line.find(path.encode()) == 0:
                    found[path].append(line)

    expected = collections.defaultdict(list)
    for path in input_paths:
        with open(path, "rb") as f:
            expected[path].extend(f.readlines())

    for key, expected_lines in expected.items():
        found_lines = found[key]
        assert (
            expected_lines == found_lines
        ), f"{expected_lines!r} == {found_lines!r}"

tmpdir, input_paths, handles, output_path = setup()

run_threads(handles, 0.1, output_path)

confirm_merge(input_paths, output_path)

tmpdir.cleanup()
```

- Having converted `tail_file` the next step is to convert `run_threads`
  - Here the implementations converge (since that’s the whole program)
- This gives a great starting point for `asyncio` implementation
- From this point we can consider more advanced uses of `asyncio` (See
  [Item 78](../Item_078/item_078.qmd))

## Things to Remember

- `run_in_executor` is an awaitable method
  - Attached to the `asyncio` event loop
  - Enables coroutines to run synchronous functions via a
    `ThreadPoolExecutor` worker thread
  - Supports top-down migration to `asyncio`
- `run_until_complete` is a method of the `asyncio` event loop
  - Enables synchronous code to run a coroutine to completion
