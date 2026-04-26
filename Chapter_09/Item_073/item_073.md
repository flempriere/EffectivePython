# Item 73: Understand how Using Queue for Concurrency Requires

Refactoring

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- We seen that raw threads have issues with supporting fan-out / fan-in
  architectures (See [Item 72](../Item_072/item_072.qmd))
- Another approach is to use `Queue` to construct a threaded pipeline
  (See [Item 70](../Item_070/item_070.qmd))
- We’ll continue working with the Game of Life Example (See [Item
  71](../Item_071/item_071.qmd))
- Rather than dynamically create `Thread` instances for each cell, the
  `Queue` approach
  1. Uses a fixed number of worker threads
  2. Workers perform I/O as required
- This approach
  - Keeps a bounded level of resource usage
  - Eliminates cost of starting and destroying threads each step
- We construct two `Queue` instances
  1. Takes in cells to be updated
  2. Delivers updated cells
- We’ll reuse `StoppableWorker` (See [Item
  70](../Item_070/item_070.qmd)) for our worker threads
  - Have to then define a function `game_logic_thread` for the
    concurrent worker threads to execute
    - Threads receive the cell coordinates, the number of neighbours and
      the cell state
    - Determine the new cell state
    - Return a tuple containing the cell coordinates and it’s new state
- Last step is to then start the queue
  - We’ll inject some demonstration test data

``` python
from threading import Thread
from queue import Queue, ShutDown


# Pipeline set-up
in_queue = Queue()
out_queue = Queue()


class StoppableWorker(Thread):
    def __init__(self, func, in_queue, out_queue):
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue

    def run(self):
        while True:
            try:
                item = self.in_queue.get()
            except ShutDown:
                return
            else:
                result = self.func(item)
                self.out_queue.put(result)
                self.in_queue.task_done()


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


def game_logic_thread(item):
    x, y, state, neighbours = item
    try:
        next_state = game_logic(state, neighbours)
    except Exception as e:
        next_state = e
    return (x, y, next_state)


threads = []
for _ in range(5):
    thread = StoppableWorker(game_logic_thread, in_queue, out_queue)
    thread.start()
    threads.append(thread)

# Demonstration
ALIVE = "*"
EMPTY = "-"

grid = [[ALIVE, EMPTY, ALIVE], [EMPTY, EMPTY, EMPTY], [EMPTY, ALIVE, EMPTY]]
for y, row in enumerate(grid):
    for x, state in enumerate(row):
        in_queue.put((x, y, state, 2 if state == ALIVE else 3))  # fan out
in_queue.join()
count = out_queue.qsize()

expected_grid = [[ALIVE, ALIVE, ALIVE], [ALIVE, ALIVE, ALIVE], [ALIVE, ALIVE, ALIVE]]
for x, y, state in out_queue.queue:
    assert expected_grid[x][y] == state
```

- Now need to update `simulate` to use the queues to request state
  transitions
  - Then wait on and receive responses
- Items added to `in_queue` are fanned-out the worker threads
- Collected in the `out_queue` for fan-in and consumption by `simulate`

``` python
from threading import Thread
from queue import Queue, ShutDown

# Game logic

ALIVE = "*"
EMPTY = "-"


class SimulationError(Exception):
    pass


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


# Queue Pipeline logic
class StoppableWorker(Thread):
    def __init__(self, func, in_queue, out_queue):
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue

    def run(self):
        while True:
            try:
                item = self.in_queue.get()
            except ShutDown:
                return
            else:
                result = self.func(item)
                self.out_queue.put(result)
                self.in_queue.task_done()


def game_logic_thread(item):
    x, y, state, neighbours = item
    try:
        next_state = game_logic(state, neighbours)
    except Exception as e:
        next_state = e
    return (x, y, next_state)


in_queue = Queue()
out_queue = Queue()

threads = []
N_THREADS = 4
for _ in range(N_THREADS):
    thread = StoppableWorker(game_logic_thread, in_queue, out_queue)
    thread.start()
    threads.append(thread)


def simulate_pipeline(grid, in_queue, out_queue):
    for y in range(grid.height):
        for x in range(grid.width):
            state = grid.get(x, y)
            neighbours = count_neighbours(x, y, grid.get)
            in_queue.put((x, y, state, neighbours))
    in_queue.join()
    item_count = out_queue.qsize()

    next_grid = Grid(grid.width, grid.height)
    for _ in range(item_count):
        item = out_queue.get()
        x, y, next_state = item
        if isinstance(next_state, Exception):
            raise SimulationError(x, y) from next_state
        next_grid.set(x, y, next_state)
    return next_grid


# Demonstration
initial_state = [[ALIVE, EMPTY, ALIVE], [EMPTY, EMPTY, EMPTY], [EMPTY, ALIVE, EMPTY]]
expected_state = [[ALIVE, ALIVE, ALIVE], [ALIVE, ALIVE, ALIVE], [ALIVE, ALIVE, ALIVE]]

grid = Grid(3, 3)
for y, row in enumerate(initial_state):
    for x, state in enumerate(row):
        grid.set(x, y, state)

result = simulate_pipeline(grid, in_queue, out_queue)
print(result)
assert result.rows == expected_state
```

    ***
    ***
    ***

- We’ve eliminated the `step_cell` function
  - Calls to `grid.get` and `new_grid.set` now occur inside the pipeline
    (`simulate_pipeline`)
  - We don’t have to modify our `Grid` class to support synchronisation
  - Only main thread touches the grid directly
    - child threads only pass tuples
- Easier to debug the pipeline
  - `game_logic_thread` is able to catch and return any exceptions that
    occur in the child thread
  - This is then checked in the `out_queue`
  - Then a `raise` a corresponding `SimulationError`
- The code below demonstrates, by modifying `game_logic` to raise an
  `OSError`

``` python
from threading import Thread
from queue import Queue, ShutDown

# Game logic

ALIVE = "*"
EMPTY = "-"


class SimulationError(Exception):
    pass


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


# Changed to raise an error
def game_logic(state, neighbours):
    raise OSError("Problem with I/O in game_logic")


# Queue Pipeline logic
class StoppableWorker(Thread):
    def __init__(self, func, in_queue, out_queue):
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue

    def run(self):
        while True:
            try:
                item = self.in_queue.get()
            except ShutDown:
                return
            else:
                result = self.func(item)
                self.out_queue.put(result)
                self.in_queue.task_done()


def game_logic_thread(item):
    x, y, state, neighbours = item
    try:
        next_state = game_logic(state, neighbours)
    except Exception as e:
        next_state = e
    return (x, y, next_state)


in_queue = Queue()
out_queue = Queue()

threads = []
N_THREADS = 4
for _ in range(N_THREADS):
    thread = StoppableWorker(game_logic_thread, in_queue, out_queue)
    thread.start()
    threads.append(thread)


def simulate_pipeline(grid, in_queue, out_queue):
    for y in range(grid.height):
        for x in range(grid.width):
            state = grid.get(x, y)
            neighbours = count_neighbours(x, y, grid.get)
            in_queue.put((x, y, state, neighbours))
    in_queue.join()
    item_count = out_queue.qsize()

    next_grid = Grid(grid.width, grid.height)
    for _ in range(item_count):
        item = out_queue.get()
        x, y, next_state = item
        if isinstance(next_state, Exception):
            raise SimulationError(x, y) from next_state
        next_grid.set(x, y, next_state)
    return next_grid


simulate_pipeline(Grid(1, 1), in_queue, out_queue)
```

    SimulationError: (0, 0)
    ---------------------------------------------------------------------------
    OSError                                   Traceback (most recent call last)
    Cell In[3], line 76, in game_logic_thread(item)
         75 try:
    ---> 76     next_state = game_logic(state, neighbours)
         77 except Exception as e:

    Cell In[3], line 50, in game_logic(state, neighbours)
         49 def game_logic(state, neighbours):
    ---> 50     raise OSError("Problem with I/O in game_logic")

    OSError: Problem with I/O in game_logic

    The above exception was the direct cause of the following exception:

    SimulationError                           Traceback (most recent call last)
    Cell In[3], line 112
        108         next_grid.set(x, y, next_state)
        109     return next_grid
    --> 112 simulate_pipeline(Grid(1, 1), in_queue, out_queue)

    Cell In[3], line 107, in simulate_pipeline(grid, in_queue, out_queue)
        105     x, y, next_state = item
        106     if isinstance(next_state, Exception):
    --> 107         raise SimulationError(x, y) from next_state
        108     next_grid.set(x, y, next_state)
        109 return next_grid

    SimulationError: (0, 0)

- We can then drive the pipeline for multiple generations as before
  - Simply have to call `simulate_pipeline` in a loop

``` python
from threading import Thread
from queue import Queue, ShutDown

# Game logic

ALIVE = "*"
EMPTY = "-"


class SimulationError(Exception):
    pass


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


# Queue Pipeline logic
class StoppableWorker(Thread):
    def __init__(self, func, in_queue, out_queue):
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue

    def run(self):
        while True:
            try:
                item = self.in_queue.get()
            except ShutDown:
                return
            else:
                result = self.func(item)
                self.out_queue.put(result)
                self.in_queue.task_done()


def game_logic_thread(item):
    x, y, state, neighbours = item
    try:
        next_state = game_logic(state, neighbours)
    except Exception as e:
        next_state = e
    return (x, y, next_state)


in_queue = Queue()
out_queue = Queue()

threads = []
N_THREADS = 4
for _ in range(N_THREADS):
    thread = StoppableWorker(game_logic_thread, in_queue, out_queue)
    thread.start()
    threads.append(thread)


def simulate_pipeline(grid, in_queue, out_queue):
    for y in range(grid.height):
        for x in range(grid.width):
            state = grid.get(x, y)
            neighbours = count_neighbours(x, y, grid.get)
            in_queue.put((x, y, state, neighbours))
    in_queue.join()
    item_count = out_queue.qsize()

    next_grid = Grid(grid.width, grid.height)
    for _ in range(item_count):
        item = out_queue.get()
        x, y, next_state = item
        if isinstance(next_state, Exception):
            raise SimulationError(x, y) from next_state
        next_grid.set(x, y, next_state)
    return next_grid


# Pretty printing and running the program


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


grid = Grid(9, 5)
grid.set(3, 0, ALIVE)
grid.set(4, 1, ALIVE)
grid.set(2, 2, ALIVE)
grid.set(3, 2, ALIVE)
grid.set(4, 2, ALIVE)


columns = ColumnPrinter()
for i in range(5):
    columns.append(str(grid))
    grid = simulate_pipeline(grid, in_queue, out_queue)
print(columns)
```

        0     |     1     |     2     |     3     |     4
    ---*----- | --------- | --------- | --------- | ---------
    ----*---- | --*-*---- | ----*---- | ---*----- | ----*----
    --***---- | ---**---- | --*-*---- | ----**--- | -----*---
    --------- | ---*----- | ---**---- | ---**---- | ---***---
    --------- | --------- | --------- | --------- | ---------

- This program works and ensures
  1. No memory explosion
  2. Reduced start-up cost to an initial constant time
  3. Restored debuggability through a pass-back mechanism
- However it has the following downsides,
  1. `simulate_pipeline` is harder to follow than the threaded approach
      - The work is defined in an additional `game_logic_thread`
        function
  2. Requires extra support infrastructure
      - Had to build the `StoppableWorker` class
      - Improves readability at cost of complexity
  3. Parallelism is specified upfront
      - Can’t have system tune the required number of threads to the
        workload
  4. Have to manually catch exceptions to enable debugging in the main
      thread
      - Have to ensure Queue structure supports both state transition
        information *and* exceptions
- Biggest problem:
  - Requirement changes might require additional pipeline stages
  - E.g. if `count_neighbours` now requires I/O
    1. Have a `count_neighbours` parallelised stage
    2. Have a `step_cell` parallelised stage (What is currently
        represented)
- This poses further challenges
  1. How to propagate exceptions between stages and the main thread
  2. Need to reintroduce a lock to `Grid` to synchronise between
      pipeline stages (See [Item 72](../Item_072/item_072.qmd) and
      `LockingGrid`)
  3. If our maximum number of threads is fixed, we now have to divide
      them between the stages
      - Can’t dynamically allocate a thread to which ever stage is
        busiest
- Need to add a new queue between the two phases
- Then need to refactor the pipeline to incorporate both phases
- The total refactor might then look like

``` python
from threading import Thread, Lock
from queue import Queue, ShutDown

from threading import Thread
from queue import Queue, ShutDown

# Game logic

ALIVE = "*"
EMPTY = "-"


class SimulationError(Exception):
    pass


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


# Imagine this now also performs some blocking I/O
# Not updating here for simplicity of getting the example to run


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


# Queue Pipeline logic
class StoppableWorker(Thread):
    def __init__(self, func, in_queue, out_queue):
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue

    def run(self):
        while True:
            try:
                item = self.in_queue.get()
            except ShutDown:
                return
            else:
                result = self.func(item)
                self.out_queue.put(result)
                self.in_queue.task_done()


def count_neighbours_thread(item):
    x, y, state, get_cell = item
    try:
        neighbours = count_neighbours(x, y, get_cell)
    except Exception as e:
        neighbours = e
    return (x, y, state, neighbours)


# Have to update to account for possibility of upstream exception
def game_logic_thread(item):
    x, y, state, neighbours = item
    if isinstance(neighbours, Exception):
        next_state = neighbours
    else:
        try:
            next_state = game_logic(state, neighbours)
        except Exception as e:
            next_state = e
    return (x, y, next_state)


in_queue = Queue()
logic_queue = Queue()  # internal queue between neighbour counting and game logic
out_queue = Queue()

threads = []
N_THREADS = 4

# Splitting threads between the two processes (Thread 0, Thread 1)
for _ in range(N_THREADS // 2):
    thread = StoppableWorker(count_neighbours_thread, in_queue, logic_queue)
    thread.start()
    threads.append(thread)
# (Thread 2, Thread 3)
for _ in range(N_THREADS // 2, N_THREADS):
    thread = StoppableWorker(game_logic_thread, logic_queue, out_queue)
    thread.start()
    threads.append(thread)


def simulate_pipeline(grid, in_queue, out_queue):
    for y in range(grid.height):
        for x in range(grid.width):
            state = grid.get(x, y)
            in_queue.put((x, y, state, grid.get))  # Fan out

    in_queue.join()
    logic_queue.join()  # Pipeline sequencing
    item_count = out_queue.qsize()

    next_grid = LockingGrid(grid.width, grid.height)
    for _ in range(item_count):
        x, y, next_state = out_queue.get()  # Fan in
        if isinstance(next_state, Exception):
            raise SimulationError(x, y) from next_state
        next_grid.set(x, y, next_state)
    return next_grid


# Pretty printing and running the program


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
    grid = simulate_pipeline(grid, in_queue, out_queue)
print(columns)
```

        0     |     1     |     2     |     3     |     4
    ---*----- | --------- | --------- | --------- | ---------
    ----*---- | --*-*---- | ----*---- | ---*----- | ----*----
    --***---- | ---**---- | --*-*---- | ----**--- | -----*---
    --------- | ---*----- | ---**---- | ---**---- | ---***---
    --------- | --------- | --------- | --------- | ---------

- This approach works but let’s recapture the number (and range) of
  changes
  1. Had to define a new coordinating function
      `count_neighbours_thread`
  2. Had to redesign how our pipeline checks for exceptions
      - Had to update `simulate_pipeline` to handle the new exceptions
        API
      - Had to update `game_logic_thread` to handle the new exceptions
        API
  3. Had to add a new queue for the intermediate stage
  4. Had to split the threads between the two stages
  5. Had to modify `simulate_pipeline` to run the new pipeline
- This is a relatively large number of changes, spread out of multiple
  parts of the API
  - Means increased complexity and boilerplate
- `Queue` still preferable to raw threads, but it’s extensibility is
  limited by it’s complexibility
  - Consider other techniques (See [Item 74](../Item_074/item_074.qmd)
    and [Item 75](../Item_075/item_075.qmd))

## Things to Remember

- `Queue` can be used with a fixed number of worker threads to scale
  fan-out and fan-in
  - Does this by bounding the number of threads, and managing them at
    the pipeline level rather than per work invocation
- Refactoring existing code to use a `Queue` has significant overhead
  - Especially when dealing with a multiple stage pipeline
- Using `Queue` with a fixed number of threads places a bound on the
  level of supported I/O Parallelism
  - Is not able to provide dynamic load shifting
  - Cannot create more threads to deal with high load
  - Cannot release threads for extended periods of low load
