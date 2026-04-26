# Item 69: Use Lock to Prevent Data Races in Threads

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Given the GIL (See [Item 68](../Item_068/item_068.qmd)) you might
  think you there is no need for mutexes and or locks at all
  - Implicitly if the GIL locks the interpreter it should lock
    underlying data structures right?
  - This is not true!
    - The GIL operates at the bytecode level
    - Multiple threads can therefore operate on a data structure
      simultaneously
      - Any data structure operation that requires multiple byte code
        instructions could lead to a race condition
- For example, consider a program that counts data in parallel
  - e.g. sampling light levels from a sensor network
  - Each sensor has it’s own worker thread
    - Reading is a form of blocking I/O
  - After reading from a sensor, the worker thread increments a shared
    counter with the light level received

``` python
from threading import Thread

counter = 0


def read_sensor(sensor_index):
    # Returns sensor data or raises an exception
    pass


def get_offset(data):
    # Always returns 1 or greater
    return 1


def worker(sensor_index, how_many):
    global counter
    for _ in range(how_many):
        data = read_sensor(sensor_index)
        counter += get_offset(data)


how_many = 10**6
sensor_count = 4

threads = []
for i in range(sensor_count):
    thread = Thread(target=worker, args=(i, how_many))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

expected = how_many * sensor_count
print(f"Counter should be {expected}, got {counter}")
```

    Counter should be 4000000, got 3322762

- You should see that the result above seems wrong
- This is because we still have race conditions
- Here because the python interpreter enforces fairness this results in
  *premption*
  - Threads are suspended while running
  - Another thread starts up and does some work
  - When suspension occurs is not fixed
    - Can occur midway through a *transaction*
    - A transaction is a series of atomic operations that should be
      completed without together
- The operation below looks like an *atomic* operation
  - But it is actually a multi-step transaction

``` python
    counter += get_offset(data) # looks atomic

    # is equivalent to:
    value = counter # read current counter value
    delta = get_offset(data) # calculate get_offset
    result = value + delta # add and set
    counter = result # set
```

- Suspension of a thread can occur at any point in the above sequence
- The interleaving can cause old values to be reassigned to the counter
  - Results in missed counts
- A simulated result might look like

``` python
def get_offset():
    # Always returns 1 or greater
    return 1


counter = 0

# Running in Thread A
value_a = counter
delta_a = get_offset()  # represents
# Switch to thread B
value_b = counter  # reads old value of counter
delta_b = get_offset()
result_b = value_b + delta_b
counter = result_b
print(f"Counter after thread B:", counter)
# Context switch back to thread A
result_a = value_a + delta_a  # old value of counter used
counter = result_a
print(f"Counter after thread A:", counter)
```

    Counter after thread B: 1
    Counter after thread A: 1

- Thread B interrupts A before it can finish setting the counter
- Thread B then reads the old value of counter and finishes updating the
  counter
- Thread A then restarts and uses the old value of counter to overwrite
  it
- To prevent these race conditions, `Threading` provides a number of
  synchronisation mechanisms
  - The most basic is `Lock`
  - It’s a simple mutex
- We can rewrite our counter program with a `Lock` so that only one
  thread can update `counter` at a time
  - We add a lock `counter_lock` to lock any access to `counter`
  - We then update our `Worker` class adding a `with` context to use the
    lock before accessing `counter`
    - `with` adds an extra layer on indentation so makes it clear where
      the lock is active
    - Also means we don’t have to manually manage the locking ourself

``` python
from threading import Thread, Lock

counter = 0
counter_lock = Lock()  # new lock for synchronisation


def read_sensor(sensor_index):
    # Returns sensor data or raises an exception
    pass


def get_offset(data):
    # Always returns 1 or greater
    return 1


def worker(sensor_index, how_many):
    global counter
    for _ in range(how_many):
        data = read_sensor(sensor_index)
        with counter_lock:  # add a lock to counter access
            counter += get_offset(data)


how_many = 10**6
sensor_count = 4

threads = []
for i in range(sensor_count):
    thread = Thread(target=worker, args=(i, how_many))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

expected = how_many * sensor_count
print(f"Counter should be {expected}, got {counter}")
```

    Counter should be 4000000, got 4000000

## Things to Remember

- The python GIL only provides a mutex at the bytecode level
  - It is still possible for data races between threads at the program
    level
- Allowing multiple threads to access shared mutable state will lead to
  corrupted data structures
  - Use mutexes to enforce proper access patterns
- Use the `Lock` class from `threading` to enforce invariants between
  multiple threads
