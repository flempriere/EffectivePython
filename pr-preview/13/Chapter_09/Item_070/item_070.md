# Item 70: Use `Queue` to Coordinate Work Between Threads


- [Notes](#notes)
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
    1.  Receive a constant stream of images from a digital camera
    2.  Resize them
    3.  Add them to a photo gallery online
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
  1.  We busy wait on the `done_queue` to check if all work has finished
  2.  In `Worker` the `run` method executes endlessly in the busy loop
      - No clean way to signal that the thread should exit
  3.  A backup in the pipeline can cause a crash
      - If the first phase is fast but the second is slow the second
        phase queue will grow
      - Eventually program runs out of memory and crashes
- Pipelines are great, but creating a producer-consumer queue is
  difficult

## Things to Remember
