# Item 79: Consider `concurrent.futures` for True Parallelism


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- As discussed Python’s GIL generally prevents true parallelism (See
  [Item 68](../Item_068/item_068.qmd))
- The `multiprocessing` built-in bypasses this by enabling multiple
  python interpreters to execute as child processes (See [Item
  67](../Item_067/item_067.qmd))
  - Different child interpreters each have their own independent GILs
  - Each can therefore utilise one CPU core
- Can be accessed via the `concurrent.futures` built-in (See [Item
  74](../Item_074/item_074.qmd))
- For example, consider a simple mathematical process which is easy to
  parallelise, namely determining the `gcd`

``` python
import time


def gcd(pair):
    a, b = pair
    low = min(a, b)
    for i in range(low, 0, -1):
        if a % i == 0 and b % i == 0:
            return i
    raise RuntimeError("Not reachable")


NUMBERS = [
    (19633090, 22659730),
    (20306770, 38141720),
    (15516450, 22296200),
    (20390450, 20208020),
    (18237120, 19249280),
    (22931290, 10204910),
    (12812380, 22737820),
    (38238120, 42372810),
    (38127410, 47291390),
    (12923910, 21238110),
]


def main():
    start = time.perf_counter()
    results = list(map(gcd, NUMBERS))
    end = time.perf_counter()
    delta = end - start
    print(f"Took {delta:.3f} seconds")


if __name__ == "__main__":
    main()
```

    Took 9.284 seconds

- Can’t speed this up via threads due to the GIL
  - Only one CPU can be executing in the interpreter at a time
- But, to illustrate what we’ll do we can look at a `ThreadPoolExecutor`
  implementation

``` python
from concurrent.futures import ThreadPoolExecutor
import time


def gcd(pair):
    a, b = pair
    low = min(a, b)
    for i in range(low, 0, -1):
        if a % i == 0 and b % i == 0:
            return i
    raise RuntimeError("Not reachable")


NUMBERS = [
    (19633090, 22659730),
    (20306770, 38141720),
    (15516450, 22296200),
    (20390450, 20208020),
    (18237120, 19249280),
    (22931290, 10204910),
    (12812380, 22737820),
    (38238120, 42372810),
    (38127410, 47291390),
    (12923910, 21238110),
]


def main():
    start = time.perf_counter()
    pool = ThreadPoolExecutor(max_workers=8)
    results = list(pool.map(gcd, NUMBERS))
    end = time.perf_counter()
    delta = end - start
    print(f"Took {delta:.3f} seconds")


if __name__ == "__main__":
    main()
```

    Took 9.551 seconds

- This may or may not be slower due to the overhead of managing the
  threads
- We can instead distribute this over *Processes*
  - Instead of using a `ThreadPoolExecutor` we use `ProcessPoolExecutor`

> [!NOTE]
>
> We can’t execute the code below in a notebook, because this attempts
> to parse the entire notebook as a python script.
>
> You should still run the example yourself by copying it into a script
> and executing that file. For this purposes we have provided
> [ProcessPoolExecutorExample.py](./ProcessPoolExecutorExample.py)

``` python
from concurrent.futures import ProcessPoolExecutor  # Change the import
import time


def gcd(pair):
    a, b = pair
    low = min(a, b)
    for i in range(low, 0, -1):
        if a % i == 0 and b % i == 0:
            return i
    raise RuntimeError("Not reachable")


NUMBERS = [
    (19633090, 22659730),
    (20306770, 38141720),
    (15516450, 22296200),
    (20390450, 20208020),
    (18237120, 19249280),
    (22931290, 10204910),
    (12812380, 22737820),
    (38238120, 42372810),
    (38127410, 47291390),
    (12923910, 21238110),
]


def main():
    start = time.perf_counter()
    pool = ProcessPoolExecutor(max_workers=8)  # changed to ProcessPoolExecutor
    results = list(pool.map(gcd, NUMBERS))
    end = time.perf_counter()
    delta = end - start
    print(f"Took {delta:.3f} seconds")


if __name__ == "__main__":
    main()
```

- This should result in a meaningful speed decrease

- `ProcessPoolExecutor` does the following,

  1.  Takes each item from `numbers` to `map`
  2.  Serialises the item into binary via `pickle`
  3.  Copies serialized data from the main interpreter to a child
      interpreter process
      - Copy occurs via a socket
  4.  Item is deserialized back into Python objects via `pickle` (in the
      child)
  5.  Runs the `gcd` function on the input data
      - Occurs in parallel with other child processes
  6.  Serializes result in binary data via `pickle`
  7.  Sends the result back through the socket
  8.  Deserializes the data back into Python objects via `pickle` (in
      the main)
  9.  Merges the results from multiple children into a single output
      `list`

- Underneath the hood the implementation is provided via
  `multiprocessing`

- `concurrent.futures` just provides a clean high-level interface

  - Has a high overhead because disconnected processes require
    serialization to communicate
  - Languages without the GIL can coordinate via threads and atomics /
    locks (See [Item 69](../Item_069/item_069.qmd))

- Delegating to subprocesses is useful when a task is

  1.  *Isolated*
      - Doesn’t need to share state with the rest of the program
  2.  *High-Leverage*
      - Requires a small amount of input and output data
      - But requires significant computation
      - Common for many mathematical processes

- When more complex scenarios are encountered instead consider direct
  use of `multiprocessing`

  - Provides mechanisms for
    1.  Shared Memory
    2.  Cross-process locks
    3.  Queues
    4.  Proxies
  - These are very complex
  - Hard to reason even in a single-process, multi-thread environment
    - Adding processes and sockets makes this more complex

- Until you find yourself struggling with the out-of-the-box simplicity
  of `concurrent.futures` avoid directly using `multiprocessing`

- `ThreadPoolExecutor` provides a good starting point for setting up
  concurrent execution of isolated, high-leverage code

  - If code becomes performance bottlenecked can then switch to
    `ProcessPoolExecutor`
  - Then if still an issue consider `multiprocessing` directly or
    another language

## Things to Remember

- `multiprocessing` provides powerful primitives to parallelise python
  computation with minimal effort
- `concurrent.futures` provides a simple, high-level interface to access
  `multiprocessing` via the `ProcessPoolExecutor`
- Avoid the advanced parts of `multiprocessing` until other options have
  been exhausted
