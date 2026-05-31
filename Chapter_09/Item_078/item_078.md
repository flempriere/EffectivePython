# Item 78: Maximise Responsiveness of `asyncio` Event Loops with

`async`-Friendly Worker Threads

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- We’ve seen how to incrementally migrate code to `asyncio` (See [Item
  77](../Item_077/item_077.qmd))
  - We could implement a coroutine to tail input files and merge them
    into one output

``` python
import asyncio

async def run_tasks(handles, intervals, output_path):
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
```

- The downside to this code is that it’s comparatively noisy and
  repetitive
  - `run_in_executor` is effectively a marker that identifies the
    boundary between synchronous and asynchronous programming
- We could reduce this boilerplate if rather than trying to run `open`,
  `close` and and `write` asynchronously we run them synchronously
- The new version is then
  - Reintroducing the test code from [Item 77](../Item_077/item_077.qmd)

``` python
import collections  # for testing
import os  # for testing
import random  # for testing
import string  # for testing
from tempfile import TemporaryDirectory  # for testing
from threading import Thread  # for testing

# For actual implementation
import asyncio
import time


#  Top Down async refactor stage 2
async def run_tasks(handles, interval, output_path):
    with open(output_path, "wb") as output:  # Changed

        async def write_async(data):  # Changed to blocking
            output.write(data)

        async with asyncio.TaskGroup() as group:
            for handle in handles:
                group.create_task(tail_async(handle, interval, write_async))


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


async def tail_async(handle, interval, write_func):  # change to async def
    loop = asyncio.get_event_loop()  # get the event loop
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
        while random.random() < 0.5:
            i += 1
            time.sleep(random.random() * interval)
            letters = random.choices(string.ascii_lowercase, k=10)
            data = f"{path}-{i:02}-{''.join(letters)}\n"
            f.write(data.encode())
            f.flush()


def start_write_threads(directory, file_count):
    paths = []
    for i in range(file_count):
        path = os.path.join(directory, str(i))
        with open(path, "w"):
            pass  # ensures file created
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
        print(f"File: {key}. Expected {expected_lines} lines, found {found_lines}")
        assert expected_lines == found_lines, f"{expected_lines!r} == {found_lines!r}"


tmpdir, input_paths, handles, output_path = setup()

# outside of jupyter note book replace await with asyncio.run()
await run_tasks(handles, 0.1, output_path)

confirm_merge(input_paths, output_path)

tmpdir.cleanup()
print("All tests passed!")
```

    File: /tmp/tmp_ehi45x8/0. Expected [b'/tmp/tmp_ehi45x8/0-01-liqnnhvkwl\n'] lines, found [b'/tmp/tmp_ehi45x8/0-01-liqnnhvkwl\n']
    File: /tmp/tmp_ehi45x8/1. Expected [b'/tmp/tmp_ehi45x8/1-01-dqghmjhaby\n', b'/tmp/tmp_ehi45x8/1-02-vdbafagzch\n'] lines, found [b'/tmp/tmp_ehi45x8/1-01-dqghmjhaby\n', b'/tmp/tmp_ehi45x8/1-02-vdbafagzch\n']
    File: /tmp/tmp_ehi45x8/2. Expected [] lines, found []
    File: /tmp/tmp_ehi45x8/3. Expected [] lines, found []
    File: /tmp/tmp_ehi45x8/4. Expected [b'/tmp/tmp_ehi45x8/4-01-ubnsgbxwim\n'] lines, found [b'/tmp/tmp_ehi45x8/4-01-ubnsgbxwim\n']
    All tests passed!

- Now the code looks better but we now have blocking system calls
  - This can prevent other coroutines from making progress
- This can introduce latency and limit responsiveness
  - Especially across concurrent servers
- Can we measure how often a coroutine is blocking the event loop?
  - The `debug` parameter in `asyncio.run` can be set to `True`
  - Will then print out additional debug information
    - I have not been able to replicate this in jupyter notebooks, so
      recommend running the below as a script (minus the jupyter bits
      See [slow_coroutine.py](./slow_coroutine.py))

``` python
import asyncio
import time


async def slow_coroutine():
    time.sleep(0.5)  # Simulate blocking I/O


# To run outside of jupyter
# asyncio.run(slow_coroutine(), debug=True)

# In theory required to work with jupyter
loop = asyncio.get_running_loop()
loop.set_debug(True)

await slow_coroutine()
```

- To minimise interruptions to the program, need to minimise potential
  system calls from the main event loop
  - Can do `run_in_executor` as we’ve already seen to delegate to a
    Thread Pool
  - Has all the associated boilerplate
- We could instead create a *new* `Thread` subclass (See [Item
  68](../Item_068/item_068.qmd))
  - Encapsulate all the logic surrounding the write as an independent
    event loop

``` python
import asyncio
from threading import Thread


class WriteThread(Thread):
    def __init__(self, output_path):
        super().__init__()
        self.output_path = output_path
        self.output = None
        self.loop = asyncio.new_event_loop()

    def run(self):
        asyncio.set_event_loop(self.loop)
        with open(self.output_path, "wb") as self.output:
            self.loop.run_forever()

        # Run one final round of callbacks so the await on
        # stop() in another event loop will be resolved

        self.loop.run_until_complete(asyncio.sleep(0))

    async def real_write(self, data):
        self.output.write(data)

    async def write(self, data):
        coro = self.real_write(data)
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        await asyncio.wrap_future(future)

    async def real_stop(self):
        self.loop.stop()

    async def stop(self):
        coro = self.real_stop()
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        await asyncio.wrap_future(future)

    async def __aenter__(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.start)
        return self

    async def __aexit__(self, *_):
        await self.stop()
```

- Coroutines in other threads can call and await on the `write` method
  - Provides a thread-safe wrapper for `real_write`
    - No need for an explicit `Lock` (See [Item
      69](../Item_069/item_069.qmd))
  - `real_write` does the actual system call
- Similarly provide a `real_stop` method and a thread-safe wrapper
  `stop`
  - Let’s coroutines tell the worker thread to stop
- To let the class be used with a context manager (i.e. `with`
  statements) we define the `__aenter__` and `__aexit__` dunder methods
  - Ensures the thread is appropriately started and stopped (See [Item
    76](../Item_076/item_076.qmd) for background)
- Can now refactor `run_tasks` into a fully asynchronous version
  - Doesn’t interfere with main event loop’s default executor
  - Avoid’s running system calls in main event loop

``` python
import collections  # for testing
import os  # for testing
import random  # for testing
import string  # for testing
from tempfile import TemporaryDirectory  # for testing

# For actual implementation
import asyncio
import time
from threading import Thread


class WriteThread(Thread):
    def __init__(self, output_path):
        super().__init__()
        self.output_path = output_path
        self.output = None
        self.loop = asyncio.new_event_loop()

    def run(self):
        asyncio.set_event_loop(self.loop)
        with open(self.output_path, "wb") as self.output:
            self.loop.run_forever()

        # Run one final round of callbacks so the await on
        # stop() in another event loop will be resolved

        self.loop.run_until_complete(asyncio.sleep(0))

    async def real_write(self, data):
        self.output.write(data)

    async def write(self, data):
        coro = self.real_write(data)
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        await asyncio.wrap_future(future)

    async def real_stop(self):
        self.loop.stop()

    async def stop(self):
        coro = self.real_stop()
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        await asyncio.wrap_future(future)

    async def __aenter__(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.start)
        return self

    async def __aexit__(self, *_):
        await self.stop()


# Fully asynchronous implementation
async def run_fully_async(handles, interval, output_path):
    async with WriteThread(output_path) as output, asyncio.TaskGroup() as group:
        for handle in handles:
            group.create_task(tail_async(handle, interval, output.write))


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


async def tail_async(handle, interval, write_func):  # change to async def
    loop = asyncio.get_event_loop()  # get the event loop
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
        while random.random() < 0.5:
            i += 1
            time.sleep(random.random() * interval)
            letters = random.choices(string.ascii_lowercase, k=10)
            data = f"{path}-{i:02}-{''.join(letters)}\n"
            f.write(data.encode())
            f.flush()


def start_write_threads(directory, file_count):
    paths = []
    for i in range(file_count):
        path = os.path.join(directory, str(i))
        with open(path, "w"):
            pass  # ensures file created
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
        print(f"File: {key}. Expected {expected_lines} lines, found {found_lines}")
        assert expected_lines == found_lines, f"{expected_lines!r} == {found_lines!r}"


tmpdir, input_paths, handles, output_path = setup()

# outside of jupyter note book replace await with asyncio.run()
await run_fully_async(handles, 0.1, output_path)

confirm_merge(input_paths, output_path)

tmpdir.cleanup()

print("All tests passed!")
```

    File: /tmp/tmp9lx57p8v/0. Expected [] lines, found []
    File: /tmp/tmp9lx57p8v/1. Expected [b'/tmp/tmp9lx57p8v/1-01-pxvywnecos\n'] lines, found [b'/tmp/tmp9lx57p8v/1-01-pxvywnecos\n']
    File: /tmp/tmp9lx57p8v/2. Expected [] lines, found []
    File: /tmp/tmp9lx57p8v/3. Expected [] lines, found []
    File: /tmp/tmp9lx57p8v/4. Expected [] lines, found []
    All tests passed!

## Things to Remember

- System calls in coroutines can cause latency and reduce responsiveness
  - Especially thread creation and blocking I/O
- Pass `debug=True` to `asyncio.run` to detect when coroutines are
  blocking the event loop
- Consider defining helper thread classes that provide
  coroutine-friendly interfaces when dealing with code that crosses the
  async/sync boundary
