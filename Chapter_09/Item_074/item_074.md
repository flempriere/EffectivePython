# Item 74: Consider `ThreadPoolExecutor` When Threads Are Necessary for

Concurrency

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- `concurrent.futures` is a high-level built-in for handling
  asynchronous tasks
- It provides `ThreadPoolExecutor`
  - Combines best of raw threads (See [Item
    72](../Item_072/item_072.qmd) and [Item
    73](../Item_073/item_073.qmd))
- We’ll again refactor the game of life to use it (See [item
  71](../Item_071/item_071.qmd))
- We’ll start with the basic building block implementation below

``` python
from threading import Thread, Lock

from multiprocessing.pool import ThreadPool
ALIVE = "*"
EMPTY = "-"


class Grid:
    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.rows = []
        for _ in range(self.height):
            self.rows.append([EMPTY] * self.width)

    def get(self, x, y):
        return self.rows[y % self.height][x % self.width]

    def set(self, x, y, state):
        self.rows[y % self.height][x % self.width] = state

    def __str__(self):
        output = "\n".join(["".join(row) for row in self.rows])
        return output


class LockingGrid(Grid):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.lock = Lock()

    def __str__(self):
        return super().__str__()

    def get(self, x, y):
        with self.lock:
            return super().get(x, y)

    def set(self, x, y, state):
        with self.lock:
            return super().set(x, y, state)


# Helper functions for state transition
def count_neighbours(x, y, get_cell):
    n = get_cell(x, y - 1)  # grid is index x increases left, y increases down
    ne = get_cell(x + 1, y - 1)
    e = get_cell(x + 1, y)
    se = get_cell(x + 1, y + 1)
    s = get_cell(x, y + 1)
    sw = get_cell(x - 1, y + 1)
    w = get_cell(x - 1, y)
    nw = get_cell(x - 1, y - 1)
    neighbour_states = [n, ne, e, se, s, sw, w, nw]

    count = sum([cell == ALIVE for cell in neighbour_states])
    return count


# In theory this works on some I/O but for this demo is the same as the old code
def game_logic(state, neighbours):
    if state == ALIVE:
        if neighbours < 2:
            return EMPTY  # Die: Too few
        elif neighbours > 3:
            return EMPTY  # Die: Too many
    else:
        if neighbours == 3:
            return ALIVE  # Regenerate

    return state


def step_cell(x, y, get_cell, set_cell):
    state = get_cell(x, y)
    neighbours = count_neighbours(x, y, get_cell)
    next_state = game_logic(state, neighbours)
    set_cell(x, y, next_state)


# Single-threaded implementation
def simulate(grid):
    next_grid = Grid(grid.width, grid.height)  # create a new instance of next grid
    for y in range(grid.height):
        for x in range(grid.width):
            step_cell(x, y, grid.get, next_grid.set)
    return next_grid


# Program Driver
class ColumnPrinter:
    def __init__(self):
        self.columns = []

    def append(self, data):
        self.columns.append(data)

    def __str__(self):
        row_count = 1
        for data in self.columns:
            row_count = max(row_count, len(data.splitlines()) + 1)

        rows = [""] * row_count
        for j in range(row_count):
            for i, data in enumerate(self.columns):
                line = data.splitlines()[max(0, j - 1)]
                if j == 0:
                    padding = " " * (len(line) // 2)
                    rows[j] += padding + str(i) + padding
                else:
                    rows[j] += line
                if (i + 1) < len(self.columns):
                    rows[j] += " | "
        return "\n".join(rows)


grid = LockingGrid(9, 5)
grid.set(3, 0, ALIVE)
grid.set(4, 1, ALIVE)
grid.set(2, 2, ALIVE)
grid.set(3, 2, ALIVE)
grid.set(4, 2, ALIVE)


columns = ColumnPrinter()
for i in range(5):
    columns.append(str(grid))
    grid = simulate(grid)
print(columns)
```

        0     |     1     |     2     |     3     |     4
    ---*----- | --------- | --------- | --------- | ---------
    ----*---- | --*-*---- | ----*---- | ---*----- | ----*----
    --***---- | ---**---- | --*-*---- | ----**--- | -----*---
    --------- | ---*----- | ---**---- | ---**---- | ---***---
    --------- | --------- | --------- | --------- | ---------

- We implement fan-out by submitting job requests to the executor
  - Executor runs these in a separate thread
- We then later wait for results to fan-in
- The code for the executor looks like below,
  - With dummy code rather than the previous implementation to highlight
    the actual `simulate_pool` function
  - There are some slight changes to make the shim work but they are
    listed in the comments

``` python
from concurrent.futures import ThreadPoolExecutor

ALIVE = "*"
EMPTY = "-"

# Dummy functions and data to demonstrate the process
grid = [[ALIVE, EMPTY, ALIVE], [EMPTY, EMPTY, EMPTY], [EMPTY, ALIVE, EMPTY]]
expected_grid = [[ALIVE, ALIVE, ALIVE], [ALIVE, ALIVE, ALIVE], [ALIVE, ALIVE, ALIVE]]


# dummy get cell
def get_cell(x, y):
    pass


# fake set_cell, has an additional grid field to simulate method
def set_cell(x, y, state, grid):
    grid[y % len(grid)][x % len(grid[0])] = state


# dummy step cell - has additiona grid field to simulate method
def step_cell_on_grid(x, y, get_cell, set_cell, grid):
    set_cell(x, y, ALIVE, grid)


def simulate_pool(pool, grid):
    # actual line: next_grid = LockingGrid(grid.width, grid.height)
    next_grid = grid[:]

    step_cell = lambda x, y, get_cell, set_cell: step_cell_on_grid(
        x, y, get_cell, set_cell, next_grid
    )  # not in implementation -> shim here
    futures = []
    for y in range(len(grid)):  # Here grid.height
        for x in range(len(grid[0])):  # Here grid.width
            args = (
                x,
                y,
                get_cell,
                set_cell,
            )  # get_cell -> grid.get, #set_cell -> next_grid.get
            future = pool.submit(step_cell, *args)  # Fan-out
            futures.append(future)

    for future in futures:
        future.result()
    return next_grid


# Demonstration

with ThreadPoolExecutor(max_workers=4) as pool:
    out_grid = simulate_pool(pool, grid)
    print(out_grid)
    assert out_grid == expected_grid
```

    [['*', '*', '*'], ['*', '*', '*'], ['*', '*', '*']]

- Threads can be allocated to the pool in advance
  - Don’t have to pay the creation cost each iteration
- Can limit the number of threads the pool can use via the `max_workers`
  parameter
  - Prevents a memory blow-out
- Our complete solution then looks like

``` python
from concurrent.futures import ThreadPoolExecutor
from threading import Thread, Lock

ALIVE = "*"
EMPTY = "-"


class Grid:
    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.rows = []
        for _ in range(self.height):
            self.rows.append([EMPTY] * self.width)

    def get(self, x, y):
        return self.rows[y % self.height][x % self.width]

    def set(self, x, y, state):
        self.rows[y % self.height][x % self.width] = state

    def __str__(self):
        output = "\n".join(["".join(row) for row in self.rows])
        return output


class LockingGrid(Grid):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.lock = Lock()

    def __str__(self):
        return super().__str__()

    def get(self, x, y):
        with self.lock:
            return super().get(x, y)

    def set(self, x, y, state):
        with self.lock:
            return super().set(x, y, state)


# Helper functions for state transition
def count_neighbours(x, y, get_cell):
    n = get_cell(x, y - 1)  # grid is index x increases left, y increases down
    ne = get_cell(x + 1, y - 1)
    e = get_cell(x + 1, y)
    se = get_cell(x + 1, y + 1)
    s = get_cell(x, y + 1)
    sw = get_cell(x - 1, y + 1)
    w = get_cell(x - 1, y)
    nw = get_cell(x - 1, y - 1)
    neighbour_states = [n, ne, e, se, s, sw, w, nw]

    count = sum([cell == ALIVE for cell in neighbour_states])
    return count


# In theory this works on some I/O but for this demo is the same as the old code
def game_logic(state, neighbours):
    if state == ALIVE:
        if neighbours < 2:
            return EMPTY  # Die: Too few
        elif neighbours > 3:
            return EMPTY  # Die: Too many
    else:
        if neighbours == 3:
            return ALIVE  # Regenerate

    return state


def step_cell(x, y, get_cell, set_cell):
    state = get_cell(x, y)
    neighbours = count_neighbours(x, y, get_cell)
    next_state = game_logic(state, neighbours)
    set_cell(x, y, next_state)


# Implementation using a thread pool
def simulate_pool(pool, grid):
    next_grid = LockingGrid(grid.width, grid.height)

    futures = []
    for y in range(len(grid.height)):
        for x in range(len(grid.width)):
            args = (x, y, grid.get, set_cell)
            future = pool.submit(step_cell, *args)  # Fan-out
            futures.append(future)

    for future in futures:
        future.result()

    return next_grid


# Program Driver
class ColumnPrinter:
    def __init__(self):
        self.columns = []

    def append(self, data):
        self.columns.append(data)

    def __str__(self):
        row_count = 1
        for data in self.columns:
            row_count = max(row_count, len(data.splitlines()) + 1)

        rows = [""] * row_count
        for j in range(row_count):
            for i, data in enumerate(self.columns):
                line = data.splitlines()[max(0, j - 1)]
                if j == 0:
                    padding = " " * (len(line) // 2)
                    rows[j] += padding + str(i) + padding
                else:
                    rows[j] += line
                if (i + 1) < len(self.columns):
                    rows[j] += " | "
        return "\n".join(rows)


grid = LockingGrid(9, 5)
grid.set(3, 0, ALIVE)
grid.set(4, 1, ALIVE)
grid.set(2, 2, ALIVE)
grid.set(3, 2, ALIVE)
grid.set(4, 2, ALIVE)


columns = ColumnPrinter()
with ThreadPoolExecutor(max_workers=10) as pool:
    for i in range(5):
        columns.append(str(grid))
        grid = simulate(grid)
    print(columns)
```

        0     |     1     |     2     |     3     |     4
    ---*----- | --------- | --------- | --------- | ---------
    ----*---- | --*-*---- | ----*---- | ---*----- | ----*----
    --***---- | ---**---- | --*-*---- | ----**--- | -----*---
    --------- | ---*----- | ---**---- | ---**---- | ---***---
    --------- | --------- | --------- | --------- | ---------

- We can use `ThreadPoolExecutor` as a context as demonstrated above
  - Means we don’t need to worry about it’s lifetime or scope
  - Can just limit it to the needed concurrent section
- `ThreadPoolExecutor` automatically propagates exceptions back to the
  caller
  - No need to create a manual exception handling API
  - Occurs when `result` method is called on a `Future` instance

``` python
from concurrent.futures import ThreadPoolExecutor

ALIVE = "*"
EMPTY = "-"


def game_logic(state, neighbours):
    raise OSError("Problem with I/O")


with ThreadPoolExecutor(max_workers=10) as pool:
    task = pool.submit(game_logic, ALIVE, 3)
    task.result()
```

    OSError: Problem with I/O
    ---------------------------------------------------------------------------
    OSError                                   Traceback (most recent call last)
    Cell In[4], line 13
         11 with ThreadPoolExecutor(max_workers=10) as pool:
         12     task = pool.submit(game_logic, ALIVE, 3)
    ---> 13     task.result()

    File /opt/hostedtoolcache/Python/3.14.4/x64/lib/python3.14/concurrent/futures/_base.py:443, in Future.result(self, timeout)
        441     raise CancelledError()
        442 elif self._state == FINISHED:
    --> 443     return self.__get_result()
        445 self._condition.wait(timeout)
        447 if self._state in [CANCELLED, CANCELLED_AND_NOTIFIED]:

    File /opt/hostedtoolcache/Python/3.14.4/x64/lib/python3.14/concurrent/futures/_base.py:395, in Future.__get_result(self)
        393 if self._exception is not None:
        394     try:
    --> 395         raise self._exception
        396     finally:
        397         # Break a reference cycle with the exception in self._exception
        398         self = None

    File /opt/hostedtoolcache/Python/3.14.4/x64/lib/python3.14/concurrent/futures/thread.py:86, in _WorkItem.run(self, ctx)
         83     return
         85 try:
    ---> 86     result = ctx.run(self.task)
         87 except BaseException as exc:
         88     self.future.set_exception(exc)

    File /opt/hostedtoolcache/Python/3.14.4/x64/lib/python3.14/concurrent/futures/thread.py:73, in WorkerContext.run(self, task)
         71 def run(self, task):
         72     fn, args, kwargs = task
    ---> 73     return fn(*args, **kwargs)

    Cell In[4], line 8, in game_logic(state, neighbours)
          7 def game_logic(state, neighbours):
    ----> 8     raise OSError("Problem with I/O")

    OSError: Problem with I/O

- No need to modify to support further I/O parallelism
  - e.g. if `count_neighbours` now has blocking I/O
  - Already runs concurrently because the unit of concurrency is the
    `step_cell` function
- Can also use `concurrent.futures` to perform CPU parallelism
  - Means we can have a common interface for multi-threading and
    multi-processing (See [Item 79](../Item_079/item_079.qmd))
- Thread Pool still shares the limitation of a fixed number of threads
  we saw with Queue
  - Thread pool still a good choice when no asynchronous solution
    e.g. blocking I/O or when degree of parallelism is known
- To maximise I/O parallelism we can use other techniques (See [Item
  75](../Item_075/item_075.qmd))

## Things to Remember

- `ThreadPoolExecutor` enables simple I/O parallelism with limited
  refactoring
- `ThreadPoolExecutor` can avoid the startup cost each time fan-out is
  required
- `ThreadPoolExecutor` automatically propagates exceptions across thread
  boundaries
- `ThreadPoolExecutor` eliminates memory blow-up from raw threads
  - But limits I/O parallelism by bounding the number of threads
