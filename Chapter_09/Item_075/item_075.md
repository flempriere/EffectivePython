# Item 75: Achieve Highly Concurrent I/O with Coroutines

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- The previous solutions to parallel I/O we’ve examined, have all
  fundamentally relied on *threads* (See [Item
  72](../Item_072/item_072.qmd), [Item 73](../Item_073/item_073.qmd) and
  [Item 74](../Item_074/item_074.qmd))

  - Fundamentally these approaches all struggle with large-scale
    simultaneous I/O requests

- An alternative approach is to use *Coroutines*

  - Coroutines allow for functions to interleave their progress
  - Allows for a large number of *apparently* simultaneous functions

- Coroutines are implemented via the `async` and `await` keywords

  - Generators are a form of coroutine (See [Item
    43](../../Chapter_06/Item_043/item_043.qmd) and [Item
    47](../../Chapter_06/Item_047/item_047.qmd))

- Startup cost of a coroutine is a function call

- Running cost is typically less than a kilobyte

- Coroutines are independent functions

  - Like threads
  - Can consume inputs from the environment
  - Produce outputs

- Coroutines pause at each `await`

  - Resume after each *awaitable* is resolved
  - Similar logic to `yield`

- Separate `async` functions can advance in lockstep

  - Gives the impression of simultaneous execution
  - Mimics the concurrency of threads

- Coroutines do not have the following downsides of threads,

  - memory overhead
  - startup cost
  - context switching cost
  - synchronisation primitives

- Coroutines run off an *event loop*

  - Means concurrent I/O can be interleaved for efficient execution

- Again we’ll convert our sequential game of life to this new
  concurrency paradigm

  - Want to allow I/O to occur within `game_logic`

- First step is to promote `game_logic` to a coroutine

  - do this via `async def`
  - Can then `await` on I/O

- An actual implementation (where we read from a socket) might look like

  ``` python
    async def game_logic(state, neighbours):
        # Do some input/output
        data = await my_socket.read(50)
  ```

- We’ll have to simulate the impact with our standard function below

  - Observe we have to `await` the result of an `async` function

``` python
ALIVE = "*"
EMPTY = "-"


async def game_logic(state, neighbours):
    if state == ALIVE:
        if neighbours < 2:
            return EMPTY  # Die: Too few
        elif neighbours > 3:
            return EMPTY  # Die: Too many
    else:
        if neighbours == 3:
            return ALIVE  # Regenerate

    return state


assert await game_logic(ALIVE, 0) == EMPTY
```

- We have two functions that consume `game_logic` namely
  1. `step_cell`
  2. `simulate`
- We’ll need to convert both of these to also be coroutines
- To recover the results from our `async` functions we can use the
  `asyncio` built-in module
  - We’ll create a list of tasks in `simulate` corresponding to a async
    invocation of `step_cell`
  - Then use `asyncio.gather` to wait on those tasks to complete
- The implementation then looks like

``` python
import asyncio

ALIVE = "*"
EMPTY = "-"


class Grid:
    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.rows = [[EMPTY] * self.width for _ in range(self.height)]

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


# converted to async function
async def game_logic(state, neighbours):
    if state == ALIVE:
        if neighbours < 2:
            return EMPTY  # Die: Too few
        elif neighbours > 3:
            return EMPTY  # Die: Too many
    else:
        if neighbours == 3:
            return ALIVE  # Regenerate

    return state


async def step_cell(x, y, get_cell, set_cell):
    state = get_cell(x, y)
    neighbours = count_neighbours(x, y, get_cell)
    next_state = await game_logic(state, neighbours)
    set_cell(x, y, next_state)


async def simulate(grid):
    next_grid = Grid(grid.width, grid.height)
    tasks = [
        step_cell(x, y, grid.get, next_grid.set)
        for x in range(grid.width)
        for y in range(grid.height)
    ]
    await asyncio.gather(*tasks)

    return next_grid


# Demonstrating
grid = Grid(9, 5)
grid.set(3, 0, ALIVE)
grid.set(4, 1, ALIVE)
grid.set(2, 2, ALIVE)
grid.set(3, 2, ALIVE)
grid.set(4, 2, ALIVE)

# grid = asyncio.run(simulate(grid)) # if not running in jupyter notebook uncomment this line and comment out the next
grid = await simulate(grid)
print(grid)
```

    ---------
    --*-*----
    ---**----
    ---*-----
    ---------

- How to understand the coroutine version?
  - Calling `step_cell` doesn’t immediately execute the function
    - Returns a coroutine instance
    - Similar to a generator using `yield` returns a generator instance
    - Deferred execution allows us to *fan-out*
  - `gather` from `asyncio` performs *fan-in*
    - `await` tells the event loop to pause execution of `simulate`
      until `asyncio.gather` has finished
      - This tells the event loop to run all of the associated
        `step_cell` coroutines (See [Item 77](../Item_077/item_077.qmd)
        for a different approach)
  - No locks are required for the `Grid`
    - All execution occurs in one thread
    - I/O is parallelised as part of the interleaving event loop
- Outside of jupyter we need a way to start the event loop
  - This can be done with `asyncio.run`
    - we pass the first coroutine to run (here `simulate`)
  - Inside jupyter there is already an event loop running so we can just
    `await` instead
- The complete program is then

``` python
import asyncio

ALIVE = "*"
EMPTY = "-"


class Grid:
    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.rows = [[EMPTY] * self.width for _ in range(self.height)]

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


# converted to async function
async def game_logic(state, neighbours):
    if state == ALIVE:
        if neighbours < 2:
            return EMPTY  # Die: Too few
        elif neighbours > 3:
            return EMPTY  # Die: Too many
    else:
        if neighbours == 3:
            return ALIVE  # Regenerate

    return state


async def step_cell(x, y, get_cell, set_cell):
    state = get_cell(x, y)
    neighbours = count_neighbours(x, y, get_cell)
    next_state = await game_logic(state, neighbours)
    set_cell(x, y, next_state)


async def simulate(grid):
    next_grid = Grid(grid.width, grid.height)
    tasks = [
        step_cell(x, y, grid.get, next_grid.set)
        for x in range(grid.width)
        for y in range(grid.height)
    ]
    await asyncio.gather(*tasks)

    return next_grid


# Demonstrating
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
    # grid = asyncio.run(simulate(grid)) # if not running in jupyter notebook uncomment this line and comment out the next
    grid = await simulate(grid)
print(columns)
```

        0     |     1     |     2     |     3     |     4
    ---*----- | --------- | --------- | --------- | ---------
    ----*---- | --*-*---- | ----*---- | ---*----- | ----*----
    --***---- | ---**---- | --*-*---- | ----**--- | -----*---
    --------- | ---*----- | ---**---- | ---**---- | ---***---
    --------- | --------- | --------- | --------- | ---------

- Result matches
- No longer have any thread overhead
- No issues with exception handling
  - Queues and Thread pools could only re-raise exceptions
  - Can even step through coroutines to see how exceptions are handled
- If requirements change can just convert the specific function to an
  `async` function
  - Add `await` at call sites
  - Much less overhead than the thread-based or queue-based restructure
    (See [Item 76](../Item_076/item_076.qmd))

``` python
import asyncio

ALIVE = "*"
EMPTY = "-"


class Grid:
    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.rows = [[EMPTY] * self.width for _ in range(self.height)]

    def get(self, x, y):
        return self.rows[y % self.height][x % self.width]

    def set(self, x, y, state):
        self.rows[y % self.height][x % self.width] = state

    def __str__(self):
        output = "\n".join(["".join(row) for row in self.rows])
        return output


# Updated to perform async
async def count_neighbours(x, y, get_cell):
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


# converted to async function
async def game_logic(state, neighbours):
    if state == ALIVE:
        if neighbours < 2:
            return EMPTY  # Die: Too few
        elif neighbours > 3:
            return EMPTY  # Die: Too many
    else:
        if neighbours == 3:
            return ALIVE  # Regenerate

    return state


# Updated to handle async count_neighbours
async def step_cell(x, y, get_cell, set_cell):
    state = get_cell(x, y)
    neighbours = await count_neighbours(x, y, get_cell)
    next_state = await game_logic(state, neighbours)
    set_cell(x, y, next_state)


async def simulate(grid):
    next_grid = Grid(grid.width, grid.height)
    tasks = [
        step_cell(x, y, grid.get, next_grid.set)
        for x in range(grid.width)
        for y in range(grid.height)
    ]
    await asyncio.gather(*tasks)

    return next_grid


# Demonstrating
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
    # grid = asyncio.run(simulate(grid)) # if not running in jupyter notebook uncomment this line and comment out the next
    grid = await simulate(grid)
print(columns)
```

        0     |     1     |     2     |     3     |     4
    ---*----- | --------- | --------- | --------- | ---------
    ----*---- | --*-*---- | ----*---- | ---*----- | ----*----
    --***---- | ---**---- | --*-*---- | ----**--- | -----*---
    --------- | ---*----- | ---**---- | ---**---- | ---***---
    --------- | --------- | --------- | --------- | ---------

- Coroutines decouple writing the code from considering the external
  environment (e.g. I/O)
- Let us focus on writing the event loop
  - Implement the logic of the program rather than the intricacies of
    concurrency

## Things to Remember

- Functions defined using `async` are coroutines
  - A caller can receive the result of a coroutine by using the `await`
    keyword
- Coroutines provide an efficient interface for running large numbers of
  functions apparently simultaneously
- Coroutines can use *fan-out* and *fan-in* to parallelise I/O
  - Also avoid the problems associated with thread-based I/O
