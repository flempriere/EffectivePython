# Item 103: Prefer `deque` for Producer-Consumer Queues


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- A first-in, first-out (FIFO) queue, is a common data structure
  - Sometimes called a *producer-consumer* queue
- Useful when we want to process data in the order it is received
- A natural default is to use the `list` type
- E.g. consider an email archival service
  - A first function receives emails
    - Then either returns it or raises a `NoEmailError` (See [Item
      32](../../Chapter_05/Item_032/item_032.qmd))
  - Second function then enqueues received emails to be processed
    - Uses the `append` list method to add to the end of a list
  - Consuming function then takes elements from the queue
    - Use `pop(0)` to remove the first list element
  - Finally wrap everything in a simple loop construct
    - Alternates between producing and consuming until told to stop (See
      [Item 75](../../Chapter_09/Item_075/item_075.qmd))
    - Takes in a `keep_running` function argument to know when to stop

``` python
from dataclasses import dataclass


@dataclass
class Email:
    sender: str
    receiver: str
    message: str


class NoEmailError(Exception):
    pass


def try_receive_email():
    # Mock receiving an email
    return Email("Alice", "Bob", "Hello, World!")


def produce_emails(queue):
    try:
        email = try_receive_email()
    except NoEmailError:
        return
    else:
        print("Received Email")
        queue.append(email)  # Producer


def consume_one_email(queue):
    if not queue:
        return
    email = queue.pop(0)  # Consumer
    print(f"Consumed {email.message}")


def loop(queue, keep_running):
    while keep_running():
        produce_emails(queue)
        consume_one_email(queue)


# Keep running function
def my_end_func():
    count = list(range(3))

    def func():
        if count:
            count.pop()
            return True
        return False

    return func


# Run the queue
loop([], my_end_func())
```

    Received Email
    Consumed Hello, World!
    Received Email
    Consumed Hello, World!
    Received Email
    Consumed Hello, World!

- Why split the processing?
  - Commonly due to latency, or throughput
- - Minimise latency of accepting new items
  - Throughput of enqueued items is constant
- Queues enable a consistent performance profile (See [Item
  70](../../Chapter_09/Item_070/item_070.qmd))
- When the queue gets large, `list` performance begins to degrade
  - Even *superlinearly*
- Can again use `timeit` to micro-benchmark (See [Item
  93](../../Chapter_11/Item_093/item_093.qmd))
  - Here we benchmark the cost of adding new items to a queue

``` python
import timeit


def list_append_benchmark(count):

    def run(queue):
        for i in range(count):
            queue.append(i)

    return timeit.timeit(
        setup="queue = []", stmt="run(queue)", globals=locals(), number=1
    )


for i in range(1, 6):
    count = i * 1_000_000
    delay = list_append_benchmark(count)
    print(f"Count {count:>5,} takes: {delay * 1e3:>6.2f}ms")
```

    Count 1,000,000 takes:  43.80ms
    Count 2,000,000 takes:  82.26ms
    Count 3,000,000 takes: 120.07ms
    Count 4,000,000 takes: 161.50ms
    Count 5,000,000 takes: 199.85ms

- Append takes roughly constant time for `list` type
- The total time for enqueuing scales linearly with the data
  - There is overhead for `list` to increase its capacity
  - Amortised across repeated calls
- We can also look at the cost for the `pop(0)` operation

``` python
import timeit


def list_pop_benchmark(count):

    def prepare():
        return list(range(count))

    def run(queue):
        while queue:
            queue.pop(0)

    return timeit.timeit(
        setup="queue = prepare()", stmt="run(queue)", globals=locals(), number=1
    )


for i in range(1, 6):
    count = i * 10_000
    delay = list_pop_benchmark(count)
    print(f"Count {count:>5,} takes: {delay * 1e3:>6.2f}ms")
```

    Count 10,000 takes:   7.15ms
    Count 20,000 takes:  27.23ms
    Count 30,000 takes:  60.04ms
    Count 40,000 takes: 108.73ms
    Count 50,000 takes: 173.17ms

- Total time for `pop` scales quadratically with the `list` size
- Occurs since `pop(0)` causes every element to be shifted down one
  index
  - Effectively reassigns the entire list
- To get around the scaling issues with `list` we can instead use
  `deque`
  - Built-in class from the `collecions` module
- `deque` implements are *double-ended queue*
  - Constant time operations for inserting, or removing from either end
    of the queue
  - Ideal for FIFO
- To add items to the end of a `deque` we still use `append`
- To consume we use `deque.popleft`
- The updated scheme is then,

``` python
from dataclasses import dataclass
import collections


@dataclass
class Email:
    sender: str
    receiver: str
    message: str


class NoEmailError(Exception):
    pass


def try_receive_email():
    # Mock receiving an email
    return Email("Alice", "Bob", "Hello, World!")


def produce_emails(queue):
    try:
        email = try_receive_email()
    except NoEmailError:
        return
    else:
        print("Received Email")
        queue.append(email)  # Producer


def consume_one_email(queue):
    if not queue:
        return
    email = queue.popleft()  # Consumer
    print(f"Consumed {email.message}")


def loop(queue, keep_running):
    while keep_running():
        produce_emails(queue)
        consume_one_email(queue)


# Keep running function
def my_end_func():
    count = list(range(3))

    def func():
        if count:
            count.pop()
            return True
        return False

    return func


# Run the queue
loop(collections.deque(), my_end_func())
```

    Received Email
    Consumed Hello, World!
    Received Email
    Consumed Hello, World!
    Received Email
    Consumed Hello, World!

- Can verify via a micro-benchmark again

``` python
import collections
import timeit


def deque_append_benchmark(count):
    def prepare():
        return collections.deque()

    def run(queue):
        for i in range(count):
            queue.append(i)

    return timeit.timeit(
        setup="queue = prepare()", stmt="run(queue)", globals=locals(), number=1
    )


for i in range(1, 6):
    count = i * 100_000
    delay = deque_append_benchmark(count)
    print(f"Count {count:>5,} takes {delay * 1e3:>6.2f}ms")
```

    Count 100,000 takes   3.42ms
    Count 200,000 takes   6.22ms
    Count 300,000 takes  11.04ms
    Count 400,000 takes  15.11ms
    Count 500,000 takes  19.49ms

- Still shows an approximate constant time cost
- Can also benchmark `popleft`

``` python
import collections
import timeit


def deque_popleft_benchmark(count):
    def prepare():
        return collections.deque(range(count))

    def run(queue):
        while queue:
            queue.popleft()

    return timeit.timeit(
        setup="queue = prepare()", stmt="run(queue)", globals=locals(), number=1
    )


for i in range(1, 6):
    count = i * 100_000
    delay = deque_popleft_benchmark(count)
    print(f"Count {count:>5,} takes {delay * 1e3:>6.2f}ms")
```

    Count 100,000 takes   3.66ms
    Count 200,000 takes   6.55ms
    Count 300,000 takes  10.26ms
    Count 400,000 takes  13.77ms
    Count 500,000 takes  18.10ms

- Here this scales linearly with the number of `popleft` calls, rather
  than quadratic like with `pop(0)`
- Thus when writing a producer-consumer queue, consider a `deque`
- As always benchmark before you optimise (See [Item
  92](../../Chapter_11/Item_092/item_092.qmd))

## Things to Remember

- `list` can be used to implement a FIFO queue via the `append(item)`
  and `pop(0)` calls
  - Scales quadratically with queue length due to `pop(0)` resulting in
    relocating the underlying list elements
- `deque` is a collection in the `collections` built-in
  - Provides a double-ended queue data structure
  - Provides constant time operations for inserting or removing from the
    beginning and end
  - Use `append` and `popleft` to implement a FIFO queue
