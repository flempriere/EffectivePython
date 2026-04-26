# Item 70: Use `Queue` to Coordinate Work Between Threads

- [Notes](#notes)
  - [`Queue` to the Rescue](#queue-to-the-rescue)
- [Things to Remember](#things-to-remember)

## Notes

- Concurrent python programs often need to coordinate work
- A useful construct is a pipeline of functions
- Pipeline works like an assembly line
  - Many phases run in serial
  - Each phase is a specific function call
    - Functions can work concurrently
    - Each processes work for it’s phase
  - Work is added at the start of the pipeline
    - Work progresses until it completes all phases
- This approach is great for work including those with blocking I/O or
  subprocesses
  - Easily to parallelise (See [Item 67](../Item_067/item_067.qmd) and
    [Item 68](../Item_068/item_068.qmd))
- Consider the example of building a live photo editing service
  - The pipeline is as follows
    1. Receive a constant stream of images from a digital camera
    2. Resize them
    3. Add them to a photo gallery online
  - Each step outlined above is a phase in our pipeline
- Let’s define the structure

``` python
def download(item):
    return item


def resize(item):
    return item


def upload(item):
    return item
```

- Now need to set-up a way to hand work between the pipeline phases
  - Can use a thread-safe producer-consumer queue (See [Item
    69](../Item_069/item_069.qmd))
  - We can use the `deque` (double-ended queue) data structure from the
    collections built-in

``` python
from collections import deque
from threading import Lock


def download(item):
    return item


def resize(item):
    return item


def upload(item):
    return item


class MyQueue:
    def __init__(self):
        self.items = deque()
        self.lock = Lock()
```

- The producer (digital camera) adds new images to the end of the queue
  - Define a `put` method
- The consumer (first phase of the pipeline) removes images from the
  front of the `deque`
  - Define a `get` method

``` python
from collections import deque
from threading import Lock


def download(item):
    return item


def resize(item):
    return item


def upload(item):
    return item


class MyQueue:
    def __init__(self):
        self.items = deque()
        self.lock = Lock()

    def put(self, item):
        with self.lock:
            self.items.append(item)

    def get(self):
        with self.lock:
            return self.items.popleft()


test = "Image"
queue = MyQueue()
queue.put(test)
print("Received", queue.get())
```

    Received Image

- We will repeat this process with a new queue for between each step of
  the pipeline
- Then set up some simple threading infrastructure around everything
  - We’ll also check how many times a thread polls for work and the
    actual amount of work done
  - We need to make sure threads behave correctly when trying to poll
    from an empty queue
    - This will trigger an `IndexError`
    - Here we want to introduce a small delay to the thread doesn’t
      immediately poll again
  - Then have to connect the different phases together via the queues
    and the corresponding worker threads
- Lastly we start the threads and inject some fake data
  - Here just five `object` instances
  - The pipeline runs until the `done_queue` has received all items

``` python
from collections import deque
from threading import Lock, Thread
import time


def download(item):
    print("Downloaded an Image")
    return item


def resize(item):
    print("Resized an Image")
    return item


def upload(item):
    print("Uploaded an Image")
    return item


class MyQueue:
    def __init__(self):
        self.items = deque()
        self.lock = Lock()

    def put(self, item):
        with self.lock:
            self.items.append(item)

    def get(self):
        with self.lock:
            return self.items.popleft()


class Worker(Thread):
    def __init__(self, func, in_queue, out_queue):
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.polled_count = 0
        self.work_done = 0

    def run(self):
        while True:
            self.polled_count += 1
            try:
                item = self.in_queue.get()
            except IndexError:
                time.sleep(0.01)  # No work to do
            else:
                result = self.func(item)
                self.out_queue.put(result)
                self.work_done += 1


# Connecting the phases together
download_queue = MyQueue()
resize_queue = MyQueue()
upload_queue = MyQueue()
done_queue = MyQueue()

threads = [
    Worker(download, download_queue, resize_queue),
    Worker(resize, resize_queue, upload_queue),
    Worker(upload, upload_queue, done_queue),
]

for thread in threads:
    thread.start()

n_items = 5
for _ in range(n_items):
    download_queue.put(object())

while len(done_queue.items) < n_items:
    print("Doing some other work...")
    time.sleep(0.01)

processed = len(done_queue.items)
polled = sum(t.polled_count for t in threads)
print(f"Processed {processed} items after polling {polled} times")
```

    Doing some other work...
    Downloaded an Image
    Downloaded an Image
    Downloaded an Image
    Downloaded an Image
    Downloaded an Image
    Resized an Image
    Resized an Image
    Resized an Image
    Resized an Image
    Resized an Image
    Uploaded an Image
    Uploaded an Image
    Uploaded an Image
    Uploaded an Image
    Uploaded an Image
    Processed 5 items after polling 21 times

- Works, but we have the downside that worker threads can poll their
  internal queues quite a lot for new input
  - Depending on the number of items this can result in a large number
    of iterations through the exception handling code for an empty queue
- When workers operate at different speeds an earlier phase can
  bottleneck a later phase
  - Pipeline starves
  - Late threads will busy wait checking the queue
  - Results in wasted CPU cycles
- There are three further issues with the implementation
  1. We busy wait on the `done_queue` to check if all work has finished
  2. In `Worker` the `run` method executes endlessly in the busy loop
      - No clean way to signal that the thread should exit
  3. A backup in the pipeline can cause a crash
      - If the first phase is fast but the second is slow the second
        phase queue will grow
      - Eventually program runs out of memory and crashes
- Pipelines are great, but creating a producer-consumer queue is
  difficult

### `Queue` to the Rescue

- `Queue` from the `queue` built-in module provides an out of the box
  producer-consumer queue
- Busy waiting is eliminated
  - Threads instead block waiting for new input
- For example, here we make a Thread wait for input
  - We establish a queue and define a function `consumer` to consume
    from the queue
  - We then start a thread *before* we’ve put anything on the queue
  - After that we’lll add some fake data to the queue

``` python
from threading import Thread
from queue import Queue

my_queue = Queue()


def consumer():
    print("Consumer waiting")
    my_queue.get()  # Run's after puts
    print("Consumer done")


thread = Thread(target=consumer)
thread.start()

# thread
print("Producer putting")
my_queue.put(object())  # Runs before get above
print("Producer done")
thread.join()
```

    Consumer waiting
    Producer putting
    Producer done
    Consumer done

- We can also allocate a maximum size to a queue to prevent the backup
  issue
  - Calls to `put` will block while the queue is full
- For example, here a thread waits for a while before consuming
  - We’ll let the queue hold one item at a time
  - The delay should mean that the producer attempts to put two items on
    the queue
    - Producer will block on the second put

``` python
from threading import Thread
from queue import Queue
import time

my_queue = Queue(1)  # Queue with buffer size of 1


def consumer():
    time.sleep(0.1)  # Wait
    val = my_queue.get()  # Consume
    print(f"Consumer consumed {val} from the queue")
    val = my_queue.get()
    print(f"Consumer consumed {val} from the queue")
    print("Consumer done")


thread = Thread(target=consumer)
thread.start()

my_queue.put(1)  # Runs first
print("Producer put 1")
my_queue.put(2)  # Should block
print("Producer put 2")
print("Producer done")
thread.join()
```

    Producer put 1
    Consumer consumed 1 from the queue
    Producer put 2
    Producer done
    Consumer consumed 2 from the queue
    Consumer done

- Queue can use the `task_done` method
  - Let’s you track the progress of work
  - Can use it to wait for a phase’s input queue to drain (via `join`)
  - Eliminates the need to poll for a pipeline to finish
- For example, here a thread uses `task_done` to signal it has finished
  doing work
  - Producer then doesn’t need to call `join` or poll
  - Just waits for `in_queue` to finish
    - Call `join` on the Queue directly
  - Queue’s are only joinable once `task_done` is called for all
    enqueued items

``` python
from threading import Thread
from queue import Queue

in_queue = Queue()


def consumer():
    print("Consumer waiting")
    work = in_queue.get()  # Runs second
    print("Consumer working")
    # Doing work
    print("Consumer done")
    in_queue.task_done()


thread = Thread(target=consumer)
thread.start()

print("Producing putting")
in_queue.put(1)  # Runs first
print("Producer waiting")
in_queue.join()  # Runs fourth -> waits for all tasks to finish
print("Producer done")
thread.join()
```

    Consumer waiting
    Producing putting
    Producer waiting
    Consumer working
    Consumer done
    Producer done

- Since Python 3.13, Queue also provides the `shutdown` method
  - Provides a way to terminate worker threads
  - After a thread receives a shutdown signal any `put` call on the
    queue raises an exception
  - `get` calls are still allowed
    - Means that we can still complete any enqueued work
  - Once Queue is fully empty a `ShutDown` exception is raised by `get`
    in the worker thread
    - Means the thread can clean up and exit
- For example, here a thread processes work after `shutdown` is called

``` python
from threading import Thread
from queue import Queue, ShutDown

my_queue = Queue()


def consumer():
    while True:
        try:
            item = my_queue.get()
        except ShutDown:
            print("Terminating!")
            return
        else:
            print("Got item", item)
            my_queue.task_done()


thread = Thread(target=consumer)
my_queue.put(1)
my_queue.put(2)
my_queue.put(3)
my_queue.shutdown()

thread.start()
```

    Got item 1
    Got item 2
    Got item 3
    Terminating!

- We can use all these behaviours in a single worker
- For example, let’s create a worker that,
  1. Processes inputs one at a time
  2. Puts the result on an output queue
  3. Marks the input items as done
  4. Terminates on `ShutDown` exception

``` python
from threading import Thread
from queue import Queue, ShutDown


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


# Simple demonstration
def test_func(item):
    return str(item)


q1 = Queue()
q2 = Queue()

thread = StoppableWorker(test_func, q1, q2)
q1.put(1)
q1.shutdown()

print(f"Input queue: {list(q1.queue)}")
thread.start()
q1.join()
print("Queue finished")
print(f"Output queue: {list(q2.queue)}")
```

    Input queue: [1]
    Queue finished
    Output queue: ['1']

- Now we’ll set up our pipeline threads and queues
- Our starting queue and our final queue will have no capacity
  constraints
  - We’ll constrain the intermediate pipelines (`resize_queue`,
    `upload_queue`) to only handle one item at a time (for demonstrative
    purposes)
- Then just have to inject our demo data into the pipeline
- The last step is to wait for each phase to finish
  - We call `shutdown` on the first step of the phase
  - Then use `join` to block until the phase finishes
  - We then repeat this process for each phase in-turn
  - It’s important to note that we can’t shut down a phase until the
    previous phase has finished
- Once the final queue has finished we receive all the output items in
  the main thread and shutdown the worker threads

``` python
from threading import Thread
from queue import Queue, ShutDown


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


# Setting up our pipeline threads and queues
def download(item):
    return item


def resize(item):
    return item


def upload(item):
    return item


download_queue = Queue()
resize_queue = Queue(1)
upload_queue = Queue(1)
done_queue = Queue()

threads = [
    StoppableWorker(download, download_queue, resize_queue),
    StoppableWorker(resize, resize_queue, upload_queue),
    StoppableWorker(upload, upload_queue, done_queue),
]

for thread in threads:
    thread.start()

for i in range(5):
    download_queue.put(i)

download_queue.shutdown()
download_queue.join()

# All items must at least be in the resize queue
resize_queue.shutdown()
resize_queue.join()

# All items must be at least in the upload queue
upload_queue.shutdown()
upload_queue.join()

# terminate
done_queue.shutdown()
counter = 0

while True:
    try:
        item = done_queue.get()
    except ShutDown:
        break
    else:
        # Process the item
        done_queue.task_done()
        counter += 1

done_queue.join()

for thread in threads:
    thread.join()

print(counter, "items finished")
```

    5 items finished

- We can extend this to use multiple worker threads per phase
  - Can speed up blocking I/O parallelism (See [Item
    68](../Item_068/item_068.qmd))
- First define helper functions
  1. Starts replicas of worker threads
  2. Drain the final queue

``` python
from threading import Thread
from queue import Queue, ShutDown


# Same worker from before
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


# spawn a series of threads
def start_threads(count, *args):
    threads = [StoppableWorker(*args) for _ in range(count)]
    for thread in threads:
        thread.start()
    return threads


# drain the queue
def drain_queue(input_queue):
    input_queue.shutdown()

    counter = 0

    while True:
        try:
            item = input_queue.get()
        except ShutDown:
            break
        else:
            input_queue.task_done()
            counter += 1
    input_queue.join()

    return counter
```

- Now we want to plug this into our existing framework

``` python
from threading import Thread
from queue import Queue, ShutDown


# Same worker from before
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


def download(item):
    return item


def resize(item):
    return item


def upload(item):
    return item


# spawn a series of threads
def start_threads(count, *args):
    threads = [StoppableWorker(*args) for _ in range(count)]
    for thread in threads:
        thread.start()
    return threads


# drain the queue
def drain_queue(input_queue):
    input_queue.shutdown()

    counter = 0

    while True:
        try:
            item = input_queue.get()
        except ShutDown:
            break
        else:
            input_queue.task_done()
            counter += 1
    input_queue.join()

    return counter


download_queue = Queue()
resize_queue = Queue(100)
upload_queue = Queue(100)
done_queue = Queue()

threads = (
    start_threads(3, download, download_queue, resize_queue)
    + start_threads(4, resize, resize_queue, upload_queue)
    + start_threads(5, upload, upload_queue, done_queue)
)

for i in range(2000):
    download_queue.put(i)

download_queue.shutdown()
download_queue.join()

resize_queue.shutdown()
resize_queue.join()

upload_queue.shutdown()
upload_queue.join()

counter = drain_queue(done_queue)

for thread in threads:
    thread.join()

print(counter, "items finished")
```

    2000 items finished

- Queue works well with a linear pipeline
- For other workflows consider other tools e.g. Coroutines

## Things to Remember

- Pipelines let you organise sequences of work
  - Especially I/O bound processes
  - Become suitable for concurrent execution with threads
- Constructing concurrent pipelines by hand can lead to problems,
  including
  1. busy waiting
  2. the challenges of how to communicate for threads to terminate
  3. Knowing when work is done
  4. Preventing memory explosion or bottlenecks
- The `Queue` class from the queue built-in module provides facilities
  and mechanisms for robust pipelines
  1. blocking operations
  2. buffer sizes
  3. joining
  4. shutdown
