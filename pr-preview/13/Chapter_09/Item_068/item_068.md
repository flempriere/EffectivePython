# Item 68: Use Threads for Blocking I/O; Avoid for Parallelism


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- The reference or standard implementation of Python is called CPython
- CPython runs a program in two steps
  1.  Source text is parsed and compiled into *bytecode*
      - Low-level representation of program as 8-bit instructions
      - From python 3.6 it’s technically 16-bit *wordcode*
  2.  Bytecode is run using a stack-based interpreter
      - Interpreter has a state that must be maintained during program
        execution
      - Coherency is enforced via the *Global Interpreter Local* (GIL)
- The GIL is a mutex preventing the interpreter from being preempted by
  another thread
  - This interruption could corrupt the state (e.g. garbage collection
    reference counts)
  - GIL prevents these interruptions
- In other languages multiple-execution threads can be run on multiple
  CPUs
  - Supports multiple simultaneous threads of execution
- GIL means only one thread can make progress at a time
  - Threads thus do not lead to a practical speed-up
- This luck of true concurrency is a significant negative to the GIL
  - Newer versions of Python (3.13+) are working to remove the GIL
- For example, consider the following naive factorisation algorithm

``` python
def factorise(number):
    for i in range(1, number+ 1):
        if number % i == 0:
            yield i

import time
numbers = [7775876, 6694411, 5038540, 5426782,
           9934740, 9168996, 5271226, 8288002,
           9403196, 6678888, 6776096, 9582542,
           7107467, 9633726, 5747908, 7613918]

start = time.perf_counter()
for number in numbers:
    list(factorise(number))

end = time.perf_counter()
delta = end - start
print(f"Took {delta:.3f} seconds")
```

    Took 5.457 seconds

- In another language might seem natural to do this computation using
  multiple threads of execution
  - Let’s try in python

``` python
from threading import Thread


def factorise(number):
    for i in range(1, number + 1):
        if number % i == 0:
            yield i


class FactoriseThread(Thread):
    def __init__(self, number):
        super().__init__()
        self.number = number

    def run(self):
        self.factors = list(factorise(self.number))


import time

numbers = [
    7775876,
    6694411,
    5038540,
    5426782,
    9934740,
    9168996,
    5271226,
    8288002,
    9403196,
    6678888,
    6776096,
    9582542,
    7107467,
    9633726,
    5747908,
    7613918,
]

start = time.perf_counter()

threads = []
for number in numbers:
    thread = FactoriseThread(number)
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

end = time.perf_counter()
delta = end - start
print(f"Took {delta:.3f} seconds")
```

    Took 5.492 seconds

- Here the program takes longer to execute than the single-threaded
  - Presumably because I’m asking for too many threads and it’s causing
    overhead
- There are mechanisms to get true concurrency (See [Item
  79](../Item_079/item_079.qmd))
  - Not the case for `Thread` with older python versions

> [!NOTE]
>
> As mentioned since Python 3.13 there is an experimental option to
> compile Python without the GIL. Support for this is more widespread in
> Python 3.14 and Python 3.15. This can allow standard `Thread`
> implementations to achieve a true speed up, as seen above.
>
> This is not a panacea. Many C-extensions and common libraries do not
> support this behaviour and have to reconstruct the GIL. Individual
> threads will also suffer a performance overhead due to the need for
> synchronisation

- Why then support multiple threads?
  1.  Multiple threads make it easy for a program to look like it’s
      doing multiple things at once
      - Prevents us having to hand write code to manage juggling tasks
        (See [Item 71](../Item_071/item_071.qmd))
      - Threads automatically handle this process
      - CPython ensures a level of fairness between threads
  2.  Deal with blocking I/O
      - Happens during certain system calls
      - System calls are invoked when python needs the operating system
        to interact with the external environment
      - Includes reading, writing files, network interactions,
        communication with devices, etc.
        - Threads insulate a program from the delay
- For example, consider sending a signal to a radio-controlled
  helicopter via a serial port
  - We’ll use `sleep` to emulate a slow system call
  - Function asks the OS to block for $0.1$ seconds, control then
    reverts to the program

``` python
import select
import socket
import time


def slow_systemcall():
    time.sleep(0.1)


start = time.perf_counter()

for _ in range(5):
    slow_systemcall()


end = time.perf_counter()
delta = end - start
print(f"Took {delta:.3f} seconds")
```

    Took 0.501 seconds

- Program can’t do anything while waiting on the thread to finish
  executing
  - Each system call has to execute sequentially
  - Means that in total takes about $0.5$ seconds
- Bad in practice
  - Often want to calculate the next packet we need to send while the
    current one is being transmitted
  - Otherwise our helicopter for example, might crash
- For example, rewriting above but with `Thread`
  - While the thread is running we can do some calculation for our next
    message

``` python
import select
import socket
import time
from threading import Thread


def slow_systemcall():
    time.sleep(0.1)


def compute_helicopter_position(index):
    return index


start = time.perf_counter()


threads = []
for _ in range(5):
    thread = Thread(target=slow_systemcall)
    thread.start()
    threads.append(thread)

for i in range(5):  # compute the next message set
    compute_helicopter_position(i)

for thread in threads:  # wait the threads to finish
    thread.join()


end = time.perf_counter()
delta = end - start
print(f"Took {delta:.3f} seconds")
```

    Took 0.101 seconds

- All the system calls are now able to run in parallel
  - Since the system calls do not interact with the GIL they can take
    advantage of multiple threads of execution
- Python threads will,
  1.  Acquire the GIL
  2.  Encounter a system call
  3.  Release the GIL
  4.  Perform the system call
  5.  Wait for system call to finish
  6.  Reacquire the GIL
- There are other techniques for dealing with blocking I/O
  - Consider the `asyncio` built-in library
  - But other approaches may require more effort to refactor the code
    (See [Item 75](../Item_075/item_075.qmd) and [Item
    77](../Item_077/item_077.qmd))

## Things to Remember

- Python threads can’t run in parallel on multiple cores due to the GIL
  - Newer version of Python (3.13 and up) have experimental support that
    removes the GIL
- Python threads still have uses despite the GIL
  - They give an easy way to look like a program does multiple things at
    the same time
- Python threads can be used to make multiple system calls in parallel
  - Let you perform computation and blocking I/O simultaneously
