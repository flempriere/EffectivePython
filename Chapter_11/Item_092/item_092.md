# Item 92: Profile Before Optimising


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Python’s dynamic behaviour means that sometimes the performance cost
  of operations is not intuitive
  - Some operations that would seem slow are fast, e.g.
    1.  String manipulation
    2.  Use of Generators
  - Some basic operations that would seem fast are slow, e.g.
    1.  Attribute access
    2.  Function calls
- Best way to determine performance and identify bottlenecks is to
  actually profile
  - Python provides a built-in *profiler*
- Profiling lets you focus on the real bottlenecks
- For example, a classic profiling scenario is a sort
  - Insertion sort works by inserting the next item in the unsorted part
    of a list into it’s correct position in the sorted part of the list
  - We’ll demo by implementing an inefficient `insert_value` function to
    determine the insertion point via a linear scan

``` python
def insert_value(array, value):
    for i, existing in enumerate(array):
        if existing > value:
            array.insert(i, value)
            return
    array.append(value)


def insertion_sort(data):
    result = []
    for value in data:
        insert_value(result, value)
    return result
```

- We can then profile the code
  - Generate a list of random numbers and define a `test` function (See
    [Item 39](../../Chapter_05/Item_039/item_039.qmd))
- Python provides two profilers
  - The pure python `profile`
  - C extension module `cProfile`
  - Prefer `cProfile` because it has less of a performance overhead
    - `profile` has an overhead that can skew the results
- We then instantiate a `Profile` object
  - Can then run a profile on a function via the `runcall` method
- To extract the statistics we can use the `pstats` built-in
  - Then use the `Stats` class
    - Provides methods to adjust how we display the profiling

``` python
from cProfile import Profile
from pstats import Stats
from random import randint

max_size = 12**4
data = [randint(0, max_size) for _ in range(max_size)]
test = lambda: insertion_sort(data)


def insert_value(array, value):
    for i, existing in enumerate(array):
        if existing > value:
            array.insert(i, value)
            return
    array.append(value)


def insertion_sort(data):
    result = []
    for value in data:
        insert_value(result, value)
    return result


# Run the profile
profiler = Profile()
profiler.runcall(test)

stats = Stats(profiler)
stats.strip_dirs()
stats.sort_stats("cumulative")
stats.print_stats()
```

             41888 function calls (41884 primitive calls) in 3.413 seconds

       Ordered by: cumulative time

       ncalls  tottime  percall  cumtime  percall filename:lineno(function)
            4    0.000    0.000    3.411    0.853 base_events.py:1977(_run_once)
        20736    3.384    0.000    3.406    0.000 2565863959.py:10(insert_value)
            1    0.001    0.001    3.257    3.257 2565863959.py:7(<lambda>)
            1    0.003    0.003    2.752    2.752 2565863959.py:18(insertion_sort)
            3    0.001    0.000    0.154    0.051 selectors.py:435(select)
        20729    0.023    0.000    0.023    0.000 {method 'insert' of 'list' objects}
            2    0.001    0.000    0.001    0.000 {built-in method time.sleep}
            3    0.000    0.000    0.000    0.000 events.py:92(_run)
            3    0.000    0.000    0.000    0.000 {method 'run' of '_contextvars.Context' objects}
            3    0.000    0.000    0.000    0.000 ioloop.py:750(_run_callback)
            1    0.000    0.000    0.000    0.000 zmqstream.py:684(<lambda>)
            1    0.000    0.000    0.000    0.000 zmqstream.py:573(_handle_events)
            2    0.000    0.000    0.000    0.000 zmqstream.py:653(_rebuild_io_state)
            1    0.000    0.000    0.000    0.000 iostream.py:348(<lambda>)
            1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
            1    0.000    0.000    0.000    0.000 iostream.py:350(_really_send)
           11    0.000    0.000    0.000    0.000 enum.py:1583(__or__)
            1    0.000    0.000    0.000    0.000 socket.py:700(send_multipart)
            3    0.000    0.000    0.000    0.000 {method 'poll' of 'select.epoll' objects}
            2    0.000    0.000    0.000    0.000 zmqstream.py:676(_update_handler)
           48    0.000    0.000    0.000    0.000 enum.py:1576(_get_value)
            1    0.000    0.000    0.000    0.000 zmqstream.py:614(_handle_recv)
            1    0.000    0.000    0.000    0.000 socket.py:771(recv_multipart)
      119/115    0.000    0.000    0.000    0.000 {built-in method builtins.isinstance}
           11    0.000    0.000    0.000    0.000 socket.py:623(send)
            2    0.000    0.000    0.000    0.000 iostream.py:682(_flush)
            5    0.000    0.000    0.000    0.000 enum.py:1594(__and__)
            3    0.000    0.000    0.000    0.000 attrsettr.py:43(__getattr__)
            2    0.000    0.000    0.000    0.000 iostream.py:776(_flush_buffers)
           20    0.000    0.000    0.000    0.000 enum.py:677(__call__)
            2    0.000    0.000    0.000    0.000 typing.py:184(_type_check)
            2    0.000    0.000    0.000    0.000 iostream.py:784(_rotate_buffers)
            1    0.000    0.000    0.000    0.000 asyncio.py:231(add_callback)
            2    0.000    0.000    0.000    0.000 typing.py:1292(__instancecheck__)
            1    0.000    0.000    0.000    0.000 base_events.py:817(call_soon)
            3    0.000    0.000    0.000    0.000 attrsettr.py:66(_get_attr_opt)
            2    0.000    0.000    0.000    0.000 typing.py:1583(__subclasscheck__)
            2    0.000    0.000    0.000    0.000 zmqstream.py:532(sending)
            2    0.000    0.000    0.000    0.000 queue.py:112(empty)
            6    0.000    0.000    0.000    0.000 base_events.py:766(time)
            2    0.000    0.000    0.000    0.000 {built-in method _heapq.heappop}
            3    0.000    0.000    0.000    0.000 {built-in method posix.getppid}
           20    0.000    0.000    0.000    0.000 enum.py:1146(__new__)
           16    0.000    0.000    0.000    0.000 typing.py:1355(__eq__)
            1    0.000    0.000    0.000    0.000 base_events.py:846(_call_soon)
            2    0.000    0.000    0.000    0.000 {built-in method builtins.issubclass}
            1    0.000    0.000    0.000    0.000 zmqstream.py:546(_run_callback)
            3    0.000    0.000    0.000    0.000 <frozen importlib._bootstrap>:1409(_handle_fromlist)
            2    0.000    0.000    0.000    0.000 <frozen abc>:121(__subclasscheck__)
           14    0.000    0.000    0.000    0.000 {built-in method builtins.len}
            6    0.000    0.000    0.000    0.000 typing.py:1361(__hash__)
            1    0.000    0.000    0.000    0.000 iostream.py:288(_check_mp_mode)
            1    0.000    0.000    0.000    0.000 events.py:41(__init__)
            6    0.000    0.000    0.000    0.000 {built-in method time.monotonic}
            3    0.000    0.000    0.000    0.000 {built-in method math.ceil}
            1    0.000    0.000    0.000    0.000 events.py:162(__lt__)
            1    0.000    0.000    0.000    0.000 iostream.py:285(_is_master_process)
            2    0.000    0.000    0.000    0.000 {method '__enter__' of '_thread.RLock' objects}
            2    0.000    0.000    0.000    0.000 queue.py:266(_qsize)
            2    0.000    0.000    0.000    0.000 {built-in method _abc._abc_subclasscheck}
            7    0.000    0.000    0.000    0.000 {method 'append' of 'list' objects}
            3    0.000    0.000    0.000    0.000 {method 'append' of 'collections.deque' objects}
            2    0.000    0.000    0.000    0.000 typing.py:396(inner)
            3    0.000    0.000    0.000    0.000 {built-in method builtins.getattr}
            4    0.000    0.000    0.000    0.000 {method 'popleft' of 'collections.deque' objects}
            2    0.000    0.000    0.000    0.000 typing.py:175(_type_convert)
            2    0.000    0.000    0.000    0.000 {method '__enter__' of '_thread.lock' objects}
            6    0.000    0.000    0.000    0.000 {built-in method builtins.hash}
            1    0.000    0.000    0.000    0.000 iostream.py:229(_handle_event)
            3    0.000    0.000    0.000    0.000 selector_events.py:744(_process_events)
            3    0.000    0.000    0.000    0.000 {built-in method builtins.hasattr}
            3    0.000    0.000    0.000    0.000 {method 'upper' of 'str' objects}
            2    0.000    0.000    0.000    0.000 {method '__exit__' of '_thread.RLock' objects}
            2    0.000    0.000    0.000    0.000 {method 'items' of 'dict' objects}
            2    0.000    0.000    0.000    0.000 {method '__exit__' of '_thread.lock' objects}
            3    0.000    0.000    0.000    0.000 zmqstream.py:528(receiving)
            1    0.000    0.000    0.000    0.000 {built-in method posix.getpid}
            1    0.000    0.000    0.000    0.000 {built-in method _asyncio.get_running_loop}
            1    0.000    0.000    0.000    0.000 {built-in method _contextvars.copy_context}
            1    0.000    0.000    0.000    0.000 iostream.py:327(closed)
            1    0.000    0.000    0.000    0.000 base_events.py:548(_check_closed)
            1    0.000    0.000    0.000    0.000 base_events.py:2075(get_debug)
            1    0.000    0.000    0.000    0.000 typing.py:2300(cast)

    <pstats.Stats at 0x7faaf4761e80>

- The profiler shows a range of statistics, namely
  1.  **ncalls:** The number of times the function is called
  2.  **tottime:** Number of seconds spent executing the function,
      excluding executing sub-functions
  3.  **tottime percall:** Average number of time spent in a function
      each time it is called (excluding sub-functions it calls)
  4.  **cumtime:** Cumulative number of seconds spent executing this
      function, including in sub-functions
  5.  **cumtime percall:** Average number of seconds spent executing
      this function each call, including in sub-functions
- As expected the biggest consumer is our `insert_value` function
  - We can reimplement this with a *binary search*
  - Provided by the `bisect` built-in module

> [!NOTE]
>
> When profiling a program be sure to measure the actual code and not
> any external systems. Functions that access disk or networks will tend
> to otherwise dominate the profile because these operations are orders
> of magnitude slower than the actual CPU. If your program or system
> provides a cache then improperly warming it may cause subsequent tests
> to give very different results

``` python
from bisect import bisect_left
from cProfile import Profile
from pstats import Stats
from random import randint

max_size = 12**4
data = [randint(0, max_size) for _ in range(max_size)]
test = lambda: insertion_sort(data)


def insert_value(array, value):
    i = bisect_left(array, value)
    array.insert(i, value)


def insertion_sort(data):
    result = []
    for value in data:
        insert_value(result, value)
    return result


# Run the profile
profiler = Profile()
profiler.runcall(test)

stats = Stats(profiler)
stats.strip_dirs()
stats.sort_stats("cumulative")
stats.print_stats()
```

             62568 function calls (62564 primitive calls) in 0.041 seconds

       Ordered by: cumulative time

       ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        20736    0.008    0.000    0.037    0.000 2000139989.py:11(insert_value)
            1    0.000    0.000    0.030    0.030 2000139989.py:8(<lambda>)
            1    0.003    0.003    0.030    0.030 2000139989.py:16(insertion_sort)
        20736    0.022    0.000    0.022    0.000 {method 'insert' of 'list' objects}
        20736    0.007    0.000    0.007    0.000 {built-in method _bisect.bisect_left}
            1    0.000    0.000    0.005    0.005 iostream.py:348(<lambda>)
            1    0.000    0.000    0.005    0.005 iostream.py:350(_really_send)
            1    0.001    0.001    0.005    0.005 socket.py:700(send_multipart)
            1    0.000    0.000    0.000    0.000 base_events.py:1977(_run_once)
            1    0.000    0.000    0.000    0.000 events.py:92(_run)
            1    0.000    0.000    0.000    0.000 {method 'run' of '_contextvars.Context' objects}
            1    0.000    0.000    0.000    0.000 ioloop.py:750(_run_callback)
            1    0.000    0.000    0.000    0.000 zmqstream.py:684(<lambda>)
            1    0.000    0.000    0.000    0.000 zmqstream.py:573(_handle_events)
           11    0.000    0.000    0.000    0.000 enum.py:1583(__or__)
            2    0.000    0.000    0.000    0.000 zmqstream.py:653(_rebuild_io_state)
           11    0.000    0.000    0.000    0.000 socket.py:623(send)
            1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
            1    0.000    0.000    0.000    0.000 zmqstream.py:614(_handle_recv)
            2    0.000    0.000    0.000    0.000 zmqstream.py:676(_update_handler)
           48    0.000    0.000    0.000    0.000 enum.py:1576(_get_value)
            1    0.000    0.000    0.000    0.000 socket.py:771(recv_multipart)
      118/114    0.000    0.000    0.000    0.000 {built-in method builtins.isinstance}
            3    0.000    0.000    0.000    0.000 attrsettr.py:43(__getattr__)
            2    0.000    0.000    0.000    0.000 typing.py:184(_type_check)
            5    0.000    0.000    0.000    0.000 enum.py:1594(__and__)
           20    0.000    0.000    0.000    0.000 enum.py:677(__call__)
            1    0.000    0.000    0.000    0.000 asyncio.py:231(add_callback)
            2    0.000    0.000    0.000    0.000 typing.py:1292(__instancecheck__)
            3    0.000    0.000    0.000    0.000 attrsettr.py:66(_get_attr_opt)
            2    0.000    0.000    0.000    0.000 typing.py:1583(__subclasscheck__)
            2    0.000    0.000    0.000    0.000 zmqstream.py:532(sending)
            1    0.000    0.000    0.000    0.000 base_events.py:817(call_soon)
            1    0.000    0.000    0.000    0.000 selectors.py:435(select)
            2    0.000    0.000    0.000    0.000 queue.py:112(empty)
           20    0.000    0.000    0.000    0.000 enum.py:1146(__new__)
            1    0.000    0.000    0.000    0.000 base_events.py:846(_call_soon)
           16    0.000    0.000    0.000    0.000 typing.py:1355(__eq__)
            1    0.000    0.000    0.000    0.000 {method 'poll' of 'select.epoll' objects}
            2    0.000    0.000    0.000    0.000 {built-in method builtins.issubclass}
            1    0.000    0.000    0.000    0.000 zmqstream.py:546(_run_callback)
            3    0.000    0.000    0.000    0.000 <frozen importlib._bootstrap>:1409(_handle_fromlist)
            2    0.000    0.000    0.000    0.000 <frozen abc>:121(__subclasscheck__)
            1    0.000    0.000    0.000    0.000 events.py:41(__init__)
            1    0.000    0.000    0.000    0.000 iostream.py:288(_check_mp_mode)
            6    0.000    0.000    0.000    0.000 typing.py:1361(__hash__)
            1    0.000    0.000    0.000    0.000 iostream.py:285(_is_master_process)
            2    0.000    0.000    0.000    0.000 queue.py:266(_qsize)
            2    0.000    0.000    0.000    0.000 {built-in method _abc._abc_subclasscheck}
            2    0.000    0.000    0.000    0.000 base_events.py:766(time)
            3    0.000    0.000    0.000    0.000 {built-in method builtins.getattr}
            2    0.000    0.000    0.000    0.000 typing.py:396(inner)
            8    0.000    0.000    0.000    0.000 {built-in method builtins.len}
            2    0.000    0.000    0.000    0.000 typing.py:175(_type_convert)
            2    0.000    0.000    0.000    0.000 {method 'popleft' of 'collections.deque' objects}
            2    0.000    0.000    0.000    0.000 {method '__enter__' of '_thread.lock' objects}
            1    0.000    0.000    0.000    0.000 iostream.py:229(_handle_event)
            6    0.000    0.000    0.000    0.000 {built-in method builtins.hash}
            3    0.000    0.000    0.000    0.000 {built-in method builtins.hasattr}
            3    0.000    0.000    0.000    0.000 {method 'upper' of 'str' objects}
            1    0.000    0.000    0.000    0.000 {built-in method posix.getpid}
            2    0.000    0.000    0.000    0.000 {method '__exit__' of '_thread.lock' objects}
            1    0.000    0.000    0.000    0.000 {built-in method math.ceil}
            2    0.000    0.000    0.000    0.000 {built-in method time.monotonic}
            3    0.000    0.000    0.000    0.000 zmqstream.py:528(receiving)
            1    0.000    0.000    0.000    0.000 {built-in method _contextvars.copy_context}
            1    0.000    0.000    0.000    0.000 {built-in method _asyncio.get_running_loop}
            1    0.000    0.000    0.000    0.000 {method 'append' of 'collections.deque' objects}
            1    0.000    0.000    0.000    0.000 base_events.py:548(_check_closed)
            1    0.000    0.000    0.000    0.000 selector_events.py:744(_process_events)
            1    0.000    0.000    0.000    0.000 iostream.py:327(closed)
            1    0.000    0.000    0.000    0.000 base_events.py:2075(get_debug)
            1    0.000    0.000    0.000    0.000 typing.py:2300(cast)

    <pstats.Stats at 0x7faaf47c9f90>

- The new implementation runs much faster
  - The function with the highest **tottime** is now the `insert` method
    on `list`
- One scenario that occurs frequently is a common utility function
  dominating the execution time
  - Can be difficult to interpret these scenarios because the default
    profiler display will mix all the different calls together
    - Would be better to isolate by call site
- Consider the following example,

``` python
from cProfile import Profile
from pstats import Stats


def utility(a, b):
    c = 1
    for i in range(100):
        c += a * b


def first_function():
    for _ in range(1000):
        utility(4, 5)


def second_function():
    for _ in range(10):
        utility(1, 3)


def program():
    for _ in range(20):
        first_function()
        second_function()


profiler = Profile()
profiler.runcall(program)

stats = Stats(profiler)
stats.strip_dirs()
stats.sort_stats("cumulative")
stats.print_stats()
```

             20749 function calls (20744 primitive calls) in 0.086 seconds

       Ordered by: cumulative time

       ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        20200    0.068    0.000    0.068    0.000 3007661153.py:5(utility)
           20    0.004    0.000    0.065    0.003 3007661153.py:11(first_function)
          2/1    0.014    0.007    0.059    0.059 3007661153.py:21(program)
            2    0.000    0.000    0.011    0.005 events.py:92(_run)
            2    0.000    0.000    0.011    0.005 {method 'run' of '_contextvars.Context' objects}
            2    0.000    0.000    0.011    0.005 zmqstream.py:573(_handle_events)
            1    0.000    0.000    0.011    0.011 asyncio.py:206(_handle_events)
            2    0.000    0.000    0.011    0.005 zmqstream.py:614(_handle_recv)
            2    0.000    0.000    0.010    0.005 zmqstream.py:546(_run_callback)
            2    0.000    0.000    0.010    0.005 iostream.py:229(_handle_event)
            2    0.000    0.000    0.010    0.005 iostream.py:348(<lambda>)
            2    0.000    0.000    0.010    0.005 iostream.py:350(_really_send)
            2    0.000    0.000    0.003    0.002 socket.py:700(send_multipart)
           20    0.000    0.000    0.001    0.000 3007661153.py:16(second_function)
            1    0.000    0.000    0.000    0.000 base_events.py:1977(_run_once)
           14    0.000    0.000    0.000    0.000 socket.py:623(send)
            2    0.000    0.000    0.000    0.000 socket.py:771(recv_multipart)
            1    0.000    0.000    0.000    0.000 ioloop.py:750(_run_callback)
            1    0.000    0.000    0.000    0.000 zmqstream.py:684(<lambda>)
            2    0.000    0.000    0.000    0.000 zmqstream.py:653(_rebuild_io_state)
            1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
           14    0.000    0.000    0.000    0.000 enum.py:1583(__or__)
            4    0.000    0.000    0.000    0.000 attrsettr.py:43(__getattr__)
            2    0.000    0.000    0.000    0.000 zmqstream.py:676(_update_handler)
           60    0.000    0.000    0.000    0.000 enum.py:1576(_get_value)
      168/164    0.000    0.000    0.000    0.000 {built-in method builtins.isinstance}
            4    0.000    0.000    0.000    0.000 typing.py:184(_type_check)
            6    0.000    0.000    0.000    0.000 enum.py:1594(__and__)
            4    0.000    0.000    0.000    0.000 attrsettr.py:66(_get_attr_opt)
           26    0.000    0.000    0.000    0.000 enum.py:677(__call__)
           32    0.000    0.000    0.000    0.000 typing.py:1355(__eq__)
            2    0.000    0.000    0.000    0.000 typing.py:1292(__instancecheck__)
            1    0.000    0.000    0.000    0.000 asyncio.py:231(add_callback)
            2    0.000    0.000    0.000    0.000 typing.py:1583(__subclasscheck__)
            2    0.000    0.000    0.000    0.000 zmqstream.py:532(sending)
           26    0.000    0.000    0.000    0.000 enum.py:1146(__new__)
            2    0.000    0.000    0.000    0.000 queue.py:112(empty)
            1    0.000    0.000    0.000    0.000 base_events.py:817(call_soon)
            4    0.000    0.000    0.000    0.000 <frozen importlib._bootstrap>:1409(_handle_fromlist)
            1    0.000    0.000    0.000    0.000 selectors.py:435(select)
           12    0.000    0.000    0.000    0.000 typing.py:1361(__hash__)
            1    0.000    0.000    0.000    0.000 base_events.py:846(_call_soon)
            2    0.000    0.000    0.000    0.000 {built-in method builtins.issubclass}
            2    0.000    0.000    0.000    0.000 iostream.py:288(_check_mp_mode)
            1    0.000    0.000    0.000    0.000 {method 'poll' of 'select.epoll' objects}
            2    0.000    0.000    0.000    0.000 selector_events.py:744(_process_events)
            4    0.000    0.000    0.000    0.000 typing.py:396(inner)
            3    0.000    0.000    0.000    0.000 base_events.py:766(time)
            2    0.000    0.000    0.000    0.000 <frozen abc>:121(__subclasscheck__)
            2    0.000    0.000    0.000    0.000 iostream.py:285(_is_master_process)
            4    0.000    0.000    0.000    0.000 typing.py:175(_type_convert)
            1    0.000    0.000    0.000    0.000 events.py:41(__init__)
           12    0.000    0.000    0.000    0.000 {built-in method builtins.hash}
            4    0.000    0.000    0.000    0.000 {built-in method builtins.getattr}
            1    0.000    0.000    0.000    0.000 base_events.py:1962(_add_callback)
            2    0.000    0.000    0.000    0.000 {built-in method _abc._abc_subclasscheck}
           10    0.000    0.000    0.000    0.000 {built-in method builtins.len}
            4    0.000    0.000    0.000    0.000 {built-in method builtins.hasattr}
            4    0.000    0.000    0.000    0.000 {method 'upper' of 'str' objects}
            4    0.000    0.000    0.000    0.000 {method 'popleft' of 'collections.deque' objects}
            2    0.000    0.000    0.000    0.000 queue.py:266(_qsize)
            2    0.000    0.000    0.000    0.000 {method '__enter__' of '_thread.lock' objects}
            2    0.000    0.000    0.000    0.000 {built-in method posix.getpid}
            3    0.000    0.000    0.000    0.000 {built-in method time.monotonic}
            1    0.000    0.000    0.000    0.000 {method 'get' of 'dict' objects}
            4    0.000    0.000    0.000    0.000 zmqstream.py:528(receiving)
            2    0.000    0.000    0.000    0.000 {method '__exit__' of '_thread.lock' objects}
            2    0.000    0.000    0.000    0.000 iostream.py:327(closed)
            2    0.000    0.000    0.000    0.000 {method 'append' of 'collections.deque' objects}
            1    0.000    0.000    0.000    0.000 {built-in method math.ceil}
            1    0.000    0.000    0.000    0.000 {built-in method _contextvars.copy_context}
            1    0.000    0.000    0.000    0.000 {method 'append' of 'list' objects}
            1    0.000    0.000    0.000    0.000 {built-in method _asyncio.get_running_loop}
            2    0.000    0.000    0.000    0.000 typing.py:2300(cast)
            1    0.000    0.000    0.000    0.000 base_events.py:548(_check_closed)
            1    0.000    0.000    0.000    0.000 base_events.py:2075(get_debug)

    <pstats.Stats at 0x7faaf47ca5d0>

- We can see that `utility` is called the most
  - But not obvious why, or which caller is most responsible
- We can use `print_callers` on the `Stats` object
  - Show’s which caller contributed to each function’s profiling
    information

``` python
from cProfile import Profile
from pstats import Stats


def utility(a, b):
    c = 1
    for i in range(100):
        c += a * b


def first_function():
    for _ in range(1000):
        utility(4, 5)


def second_function():
    for _ in range(10):
        utility(1, 3)


def program():
    for _ in range(20):
        first_function()
        second_function()


profiler = Profile()
profiler.runcall(program)

stats = Stats(profiler)
stats.strip_dirs()
stats.sort_stats("cumulative")
stats.print_callers()
```

       Ordered by: cumulative time

    Function                                              was called by...
                                                              ncalls  tottime  cumtime
    base_events.py:1977(_run_once)                        <-       0    0.000    0.000  base_events.py:1977(_run_once)
    3101860672.py:5(utility)                              <- 18855/839    0.063    0.003  3101860672.py:11(first_function)
                                                                 200    0.001    0.001  3101860672.py:16(second_function)
                                                                 618    0.002    0.002  selectors.py:435(select)
                                                                 160    0.001    0.001  socket.py:700(send_multipart)
                                                                 365    0.001    0.001  {method 'poll' of 'select.epoll' objects}
    3101860672.py:11(first_function)                      <-       0    0.000    0.000  3101860672.py:21(program)
                                                                   6    0.001    0.021  base_events.py:1977(_run_once)
                                                                   2    0.000    0.007  iostream.py:350(_really_send)
                                                                   9    0.002    0.032  selectors.py:435(select)
    3101860672.py:21(program)                             <- 
    events.py:92(_run)                                    <-       0    0.000    0.000  3101860672.py:11(first_function)
                                                                   1    0.000    0.000  base_events.py:1977(_run_once)
                                                                   1    0.000    0.000  selectors.py:435(select)
    {method 'run' of '_contextvars.Context' objects}      <-     2/0    0.000    0.000  events.py:92(_run)
    zmqstream.py:573(_handle_events)                      <-       0    0.000    0.000  asyncio.py:206(_handle_events)
                                                                   1    0.000    0.000  zmqstream.py:684(<lambda>)
    asyncio.py:206(_handle_events)                        <-       0    0.000    0.000  {method 'run' of '_contextvars.Context' objects}
    zmqstream.py:614(_handle_recv)                        <-     1/0    0.000    0.000  zmqstream.py:573(_handle_events)
    iostream.py:348(<lambda>)                             <-       1    0.000    0.000  iostream.py:229(_handle_event)
    zmqstream.py:546(_run_callback)                       <-     1/0    0.000    0.000  zmqstream.py:614(_handle_recv)
    iostream.py:229(_handle_event)                        <-     1/0    0.000    0.000  zmqstream.py:546(_run_callback)
    iostream.py:350(_really_send)                         <-       1    0.000    0.000  iostream.py:348(<lambda>)
    socket.py:700(send_multipart)                         <-       1    0.000    0.000  iostream.py:350(_really_send)
    socket.py:623(send)                                   <-       5    0.000    0.000  3101860672.py:11(first_function)
                                                                   7    0.000    0.000  socket.py:700(send_multipart)
    selectors.py:435(select)                              <-       1    0.000    0.000  base_events.py:1977(_run_once)
    3101860672.py:16(second_function)                     <-       7    0.000    0.000  base_events.py:1977(_run_once)
                                                                   3    0.000    0.000  iostream.py:350(_really_send)
                                                                  10    0.000    0.000  selectors.py:435(select)
    ioloop.py:750(_run_callback)                          <-       2    0.000    0.000  {method 'run' of '_contextvars.Context' objects}
    zmqstream.py:684(<lambda>)                            <-       1    0.000    0.000  ioloop.py:750(_run_callback)
    socket.py:771(recv_multipart)                         <-       2    0.000    0.000  zmqstream.py:614(_handle_recv)
    zmqstream.py:653(_rebuild_io_state)                   <-       1    0.000    0.000  asyncio.py:206(_handle_events)
                                                                   1    0.000    0.000  zmqstream.py:573(_handle_events)
    enum.py:1583(__or__)                                  <-       5    0.000    0.000  3101860672.py:11(first_function)
                                                                   7    0.000    0.000  socket.py:700(send_multipart)
                                                                   2    0.000    0.000  zmqstream.py:653(_rebuild_io_state)
    {method 'disable' of '_lsprof.Profiler' objects}      <-       1    0.000    0.000  base_events.py:1977(_run_once)
    attrsettr.py:43(__getattr__)                          <-       2    0.000    0.000  zmqstream.py:573(_handle_events)
                                                                   2    0.000    0.000  zmqstream.py:676(_update_handler)
    enum.py:1576(_get_value)                              <-      42    0.000    0.000  enum.py:1583(__or__)
                                                                  18    0.000    0.000  enum.py:1594(__and__)
    zmqstream.py:676(_update_handler)                     <-       2    0.000    0.000  zmqstream.py:653(_rebuild_io_state)
    {built-in method builtins.isinstance}                 <-       4    0.000    0.000  <frozen importlib._bootstrap>:1409(_handle_fromlist)
                                                                 100    0.000    0.000  enum.py:1576(_get_value)
                                                                   2    0.000    0.000  events.py:162(__lt__)
                                                                  14    0.000    0.000  socket.py:700(send_multipart)
                                                                   4    0.000    0.000  typing.py:175(_type_convert)
                                                                   8    0.000    0.000  typing.py:184(_type_check)
                                                                  32    0.000    0.000  typing.py:1355(__eq__)
                                                                   4    0.000    0.000  typing.py:1583(__subclasscheck__)
                                                                   1    0.000    0.000  zmqstream.py:546(_run_callback)
                                                                   1    0.000    0.000  zmqstream.py:614(_handle_recv)
    typing.py:184(_type_check)                            <-       4    0.000    0.000  socket.py:771(recv_multipart)
    enum.py:1594(__and__)                                 <-       1    0.000    0.000  asyncio.py:206(_handle_events)
                                                                   3    0.000    0.000  zmqstream.py:573(_handle_events)
                                                                   2    0.000    0.000  zmqstream.py:676(_update_handler)
    enum.py:677(__call__)                                 <-       4    0.000    0.000  attrsettr.py:66(_get_attr_opt)
                                                                  14    0.000    0.000  enum.py:1583(__or__)
                                                                   6    0.000    0.000  enum.py:1594(__and__)
                                                                   2    0.000    0.000  socket.py:771(recv_multipart)
    attrsettr.py:66(_get_attr_opt)                        <-       4    0.000    0.000  attrsettr.py:43(__getattr__)
    iostream.py:682(_flush)                               <-       1    0.000    0.000  ioloop.py:750(_run_callback)
    iostream.py:776(_flush_buffers)                       <-       1    0.000    0.000  iostream.py:682(_flush)
    typing.py:1355(__eq__)                                <-      32    0.000    0.000  typing.py:184(_type_check)
    typing.py:1292(__instancecheck__)                     <-       2    0.000    0.000  {built-in method builtins.isinstance}
    {method 'poll' of 'select.epoll' objects}             <-       1    0.000    0.000  selectors.py:435(select)
    asyncio.py:231(add_callback)                          <-       1    0.000    0.000  zmqstream.py:676(_update_handler)
    typing.py:1583(__subclasscheck__)                     <-       2    0.000    0.000  typing.py:1292(__instancecheck__)
    zmqstream.py:532(sending)                             <-       2    0.000    0.000  zmqstream.py:653(_rebuild_io_state)
    enum.py:1146(__new__)                                 <-      26    0.000    0.000  enum.py:677(__call__)
    iostream.py:784(_rotate_buffers)                      <-       1    0.000    0.000  iostream.py:776(_flush_buffers)
    <frozen importlib._bootstrap>:1409(_handle_fromlist)  <-       4    0.000    0.000  attrsettr.py:43(__getattr__)
    base_events.py:817(call_soon)                         <-       1    0.000    0.000  asyncio.py:231(add_callback)
    queue.py:112(empty)                                   <-       2    0.000    0.000  zmqstream.py:532(sending)
    {built-in method _heapq.heappop}                      <-       1    0.000    0.000  selectors.py:435(select)
    typing.py:1361(__hash__)                              <-      12    0.000    0.000  socket.py:771(recv_multipart)
    base_events.py:766(time)                              <-       1    0.000    0.000  3101860672.py:11(first_function)
                                                                   3    0.000    0.000  base_events.py:1977(_run_once)
                                                                   1    0.000    0.000  selectors.py:435(select)
    base_events.py:846(_call_soon)                        <-       1    0.000    0.000  base_events.py:817(call_soon)
    {built-in method builtins.issubclass}                 <-       2    0.000    0.000  typing.py:1583(__subclasscheck__)
    selector_events.py:744(_process_events)               <-       1    0.000    0.000  3101860672.py:11(first_function)
                                                                   1    0.000    0.000  base_events.py:1977(_run_once)
                                                                   1    0.000    0.000  selectors.py:435(select)
    iostream.py:288(_check_mp_mode)                       <-       2    0.000    0.000  iostream.py:350(_really_send)
    <frozen abc>:121(__subclasscheck__)                   <-       2    0.000    0.000  {built-in method builtins.issubclass}
    typing.py:396(inner)                                  <-       4    0.000    0.000  socket.py:771(recv_multipart)
    events.py:41(__init__)                                <-       1    0.000    0.000  base_events.py:846(_call_soon)
    typing.py:175(_type_convert)                          <-       4    0.000    0.000  typing.py:184(_type_check)
    {built-in method builtins.len}                        <-       1    0.000    0.000  3101860672.py:11(first_function)
                                                                   4    0.000    0.000  base_events.py:1977(_run_once)
                                                                   2    0.000    0.000  iostream.py:229(_handle_event)
                                                                   2    0.000    0.000  queue.py:266(_qsize)
                                                                   4    0.000    0.000  selectors.py:435(select)
    {built-in method builtins.getattr}                    <-       4    0.000    0.000  attrsettr.py:43(__getattr__)
    iostream.py:285(_is_master_process)                   <-       2    0.000    0.000  iostream.py:288(_check_mp_mode)
    events.py:162(__lt__)                                 <-       2    0.000    0.000  {built-in method _heapq.heappop}
    {built-in method time.monotonic}                      <-       5    0.000    0.000  base_events.py:766(time)
    {built-in method builtins.hash}                       <-      12    0.000    0.000  typing.py:1361(__hash__)
    base_events.py:1962(_add_callback)                    <-       1    0.000    0.000  selector_events.py:744(_process_events)
    {built-in method _abc._abc_subclasscheck}             <-       2    0.000    0.000  <frozen abc>:121(__subclasscheck__)
    {built-in method builtins.hasattr}                    <-       4    0.000    0.000  <frozen importlib._bootstrap>:1409(_handle_fromlist)
    {method 'upper' of 'str' objects}                     <-       4    0.000    0.000  attrsettr.py:43(__getattr__)
    {method 'popleft' of 'collections.deque' objects}     <-       1    0.000    0.000  3101860672.py:11(first_function)
                                                                   1    0.000    0.000  base_events.py:1977(_run_once)
                                                                   2    0.000    0.000  iostream.py:229(_handle_event)
                                                                   1    0.000    0.000  selectors.py:435(select)
    queue.py:266(_qsize)                                  <-       2    0.000    0.000  queue.py:112(empty)
    {built-in method math.ceil}                           <-       2    0.000    0.000  selectors.py:435(select)
    {method 'append' of 'collections.deque' objects}      <-       1    0.000    0.000  base_events.py:846(_call_soon)
                                                                   1    0.000    0.000  base_events.py:1962(_add_callback)
                                                                   1    0.000    0.000  selectors.py:435(select)
    {method '__enter__' of '_thread.lock' objects}        <-       2    0.000    0.000  queue.py:112(empty)
    {method 'get' of 'dict' objects}                      <-       1    0.000    0.000  3101860672.py:5(utility)
    {built-in method posix.getpid}                        <-       2    0.000    0.000  iostream.py:285(_is_master_process)
    zmqstream.py:528(receiving)                           <-       2    0.000    0.000  zmqstream.py:573(_handle_events)
                                                                   2    0.000    0.000  zmqstream.py:653(_rebuild_io_state)
    {method '__exit__' of '_thread.lock' objects}         <-       2    0.000    0.000  queue.py:112(empty)
    {method '__enter__' of '_thread.RLock' objects}       <-       1    0.000    0.000  iostream.py:784(_rotate_buffers)
    {built-in method _contextvars.copy_context}           <-       1    0.000    0.000  events.py:41(__init__)
    {method 'items' of 'dict' objects}                    <-       1    0.000    0.000  iostream.py:776(_flush_buffers)
    {method '__exit__' of '_thread.RLock' objects}        <-       1    0.000    0.000  iostream.py:784(_rotate_buffers)
    {built-in method _asyncio.get_running_loop}           <-       1    0.000    0.000  asyncio.py:231(add_callback)
    iostream.py:327(closed)                               <-       2    0.000    0.000  iostream.py:350(_really_send)
    {method 'append' of 'list' objects}                   <-       1    0.000    0.000  3101860672.py:5(utility)
    typing.py:2300(cast)                                  <-       2    0.000    0.000  socket.py:771(recv_multipart)
    base_events.py:548(_check_closed)                     <-       1    0.000    0.000  base_events.py:817(call_soon)
    base_events.py:2075(get_debug)                        <-       1    0.000    0.000  events.py:41(__init__)

    <pstats.Stats at 0x7faaf4774d60>

- Functions called are listed on the left
  - Functions that call that function are listed on the right
- This lets us see that `first_function` is clearly the main culprit
- An alternative is the `print_calles` method
  - Provides a top down view of which functions another function calls

``` python
from cProfile import Profile
from pstats import Stats


def utility(a, b):
    c = 1
    for i in range(100):
        c += a * b


def first_function():
    for _ in range(1000):
        utility(4, 5)


def second_function():
    for _ in range(10):
        utility(1, 3)


def program():
    for _ in range(20):
        first_function()
        second_function()


profiler = Profile()
profiler.runcall(program)

stats = Stats(profiler)
stats.strip_dirs()
stats.sort_stats("cumulative")
stats.print_callees()
```

       Ordered by: cumulative time

    Function                                              called...
                                                              ncalls  tottime  cumtime
    3103966480.py:5(utility)                              ->       1    0.000    0.000  {method 'append' of 'list' objects}
                                                                   1    0.000    0.000  {method 'get' of 'dict' objects}
    3103966480.py:11(first_function)                      -> 17953/799    0.061    0.003  3103966480.py:5(utility)
                                                                   2    0.000    0.000  base_events.py:766(time)
                                                                   1    0.000    0.000  base_events.py:1977(_run_once)
                                                                   2    0.000    0.000  enum.py:1583(__or__)
                                                                 1/0    0.000    0.000  events.py:92(_run)
                                                                   2    0.000    0.000  selector_events.py:744(_process_events)
                                                                 4/3    0.000    0.000  socket.py:623(send)
                                                                   2    0.000    0.000  {built-in method builtins.len}
                                                                   1    0.000    0.000  {built-in method posix.getppid}
                                                                   1    0.000    0.000  {method 'disable' of '_lsprof.Profiler' objects}
                                                                   2    0.000    0.000  {method 'popleft' of 'collections.deque' objects}
    3103966480.py:21(program)                             ->       1    0.000    0.073  3103966480.py:11(first_function)
    base_events.py:1977(_run_once)                        ->      15    0.003    0.053  3103966480.py:11(first_function)
                                                                  16    0.000    0.000  3103966480.py:16(second_function)
                                                                   2    0.000    0.000  base_events.py:766(time)
                                                                   2    0.000    0.000  events.py:92(_run)
                                                                   1    0.000    0.000  selector_events.py:744(_process_events)
                                                                 1/0    0.000    0.000  selectors.py:435(select)
                                                                   1    0.000    0.000  {built-in method _heapq.heappop}
                                                                   4    0.000    0.000  {built-in method builtins.len}
                                                                   1    0.000    0.000  {method 'append' of 'collections.deque' objects}
                                                                   2    0.000    0.000  {method 'popleft' of 'collections.deque' objects}
    events.py:92(_run)                                    ->     3/0    0.000    0.000  {method 'run' of '_contextvars.Context' objects}
    {method 'run' of '_contextvars.Context' objects}      ->       0    0.000    0.000  asyncio.py:206(_handle_events)
                                                                   2    0.000    0.000  ioloop.py:750(_run_callback)
                                                                   1    0.000    0.000  zmqstream.py:563(_log_error)
    zmqstream.py:573(_handle_events)                      ->       2    0.000    0.000  attrsettr.py:43(__getattr__)
                                                                   3    0.000    0.000  enum.py:1594(__and__)
                                                                   2    0.000    0.000  zmqstream.py:528(receiving)
                                                                 1/0    0.000    0.000  zmqstream.py:614(_handle_recv)
                                                                   1    0.000    0.000  zmqstream.py:653(_rebuild_io_state)
    asyncio.py:206(_handle_events)                        ->       0    0.000    0.000  zmqstream.py:573(_handle_events)
    zmqstream.py:614(_handle_recv)                        ->       1    0.000    0.000  enum.py:1594(__and__)
                                                                   2    0.000    0.000  socket.py:771(recv_multipart)
                                                                 1/0    0.000    0.000  zmqstream.py:546(_run_callback)
                                                                   1    0.000    0.000  zmqstream.py:653(_rebuild_io_state)
    zmqstream.py:546(_run_callback)                       ->     1/0    0.000    0.000  iostream.py:229(_handle_event)
                                                                   1    0.000    0.000  {built-in method builtins.isinstance}
    iostream.py:229(_handle_event)                        ->       0    0.000    0.000  iostream.py:348(<lambda>)
                                                                   1    0.000    0.000  {built-in method builtins.isinstance}
                                                                   2    0.000    0.000  {built-in method builtins.len}
                                                                   1    0.000    0.000  {method 'popleft' of 'collections.deque' objects}
    iostream.py:348(<lambda>)                             ->       1    0.000    0.005  iostream.py:348(<lambda>)
                                                                 1/0    0.000    0.000  iostream.py:350(_really_send)
                                                                   1    0.000    0.000  {method 'popleft' of 'collections.deque' objects}
    iostream.py:350(_really_send)                         ->       3    0.000    0.008  3103966480.py:11(first_function)
                                                                   4    0.000    0.000  3103966480.py:16(second_function)
                                                                   0    0.000    0.000  base_events.py:1977(_run_once)
                                                                   2    0.000    0.000  iostream.py:288(_check_mp_mode)
                                                                   2    0.000    0.000  iostream.py:327(closed)
                                                                 1/0    0.000    0.000  socket.py:700(send_multipart)
    socket.py:700(send_multipart)                         -> 409/200    0.001    0.001  3103966480.py:5(utility)
                                                                  10    0.000    0.000  enum.py:1583(__or__)
                                                                 9/3    0.000    0.000  socket.py:623(send)
                                                                  14    0.000    0.000  {built-in method builtins.isinstance}
    3103966480.py:16(second_function)                     ->     200    0.001    0.001  3103966480.py:5(utility)
    socket.py:623(send)                                   -> 
    ioloop.py:750(_run_callback)                          ->       1    0.000    0.000  iostream.py:682(_flush)
                                                                   1    0.000    0.000  zmqstream.py:684(<lambda>)
    socket.py:771(recv_multipart)                         ->       2    0.000    0.000  enum.py:677(__call__)
                                                                   4    0.000    0.000  typing.py:184(_type_check)
                                                                   4    0.000    0.000  typing.py:396(inner)
                                                                  12    0.000    0.000  typing.py:1361(__hash__)
                                                                   2    0.000    0.000  typing.py:2300(cast)
    zmqstream.py:684(<lambda>)                            ->       1    0.000    0.000  zmqstream.py:573(_handle_events)
    zmqstream.py:653(_rebuild_io_state)                   ->       2    0.000    0.000  enum.py:1583(__or__)
                                                                   2    0.000    0.000  zmqstream.py:528(receiving)
                                                                   2    0.000    0.000  zmqstream.py:532(sending)
                                                                   2    0.000    0.000  zmqstream.py:676(_update_handler)
    {method 'disable' of '_lsprof.Profiler' objects}      -> 
    enum.py:1583(__or__)                                  ->      14    0.000    0.000  enum.py:677(__call__)
                                                                  42    0.000    0.000  enum.py:1576(_get_value)
    attrsettr.py:43(__getattr__)                          ->       4    0.000    0.000  <frozen importlib._bootstrap>:1409(_handle_fromlist)
                                                                   4    0.000    0.000  attrsettr.py:66(_get_attr_opt)
                                                                   4    0.000    0.000  {built-in method builtins.getattr}
                                                                   4    0.000    0.000  {method 'upper' of 'str' objects}
    zmqstream.py:676(_update_handler)                     ->       1    0.000    0.000  asyncio.py:231(add_callback)
                                                                   2    0.000    0.000  attrsettr.py:43(__getattr__)
                                                                   2    0.000    0.000  enum.py:1594(__and__)
    enum.py:1576(_get_value)                              ->     100    0.000    0.000  {built-in method builtins.isinstance}
    {built-in method builtins.isinstance}                 ->       2    0.000    0.000  typing.py:1292(__instancecheck__)
    typing.py:184(_type_check)                            ->       4    0.000    0.000  typing.py:175(_type_convert)
                                                                  32    0.000    0.000  typing.py:1355(__eq__)
                                                                   8    0.000    0.000  {built-in method builtins.isinstance}
    enum.py:1594(__and__)                                 ->       6    0.000    0.000  enum.py:677(__call__)
                                                                  18    0.000    0.000  enum.py:1576(_get_value)
    attrsettr.py:66(_get_attr_opt)                        ->       4    0.000    0.000  enum.py:677(__call__)
    enum.py:677(__call__)                                 ->      26    0.000    0.000  enum.py:1146(__new__)
    typing.py:1292(__instancecheck__)                     ->       2    0.000    0.000  typing.py:1583(__subclasscheck__)
    asyncio.py:231(add_callback)                          ->       1    0.000    0.000  base_events.py:817(call_soon)
                                                                   1    0.000    0.000  {built-in method _asyncio.get_running_loop}
    typing.py:1355(__eq__)                                ->      32    0.000    0.000  {built-in method builtins.isinstance}
    typing.py:1583(__subclasscheck__)                     ->       4    0.000    0.000  {built-in method builtins.isinstance}
                                                                   2    0.000    0.000  {built-in method builtins.issubclass}
    iostream.py:682(_flush)                               ->       1    0.000    0.000  iostream.py:776(_flush_buffers)
    zmqstream.py:532(sending)                             ->       2    0.000    0.000  queue.py:112(empty)
    enum.py:1146(__new__)                                 -> 
    iostream.py:776(_flush_buffers)                       ->       1    0.000    0.000  iostream.py:784(_rotate_buffers)
                                                                   1    0.000    0.000  {method 'items' of 'dict' objects}
    base_events.py:817(call_soon)                         ->       1    0.000    0.000  base_events.py:548(_check_closed)
                                                                   1    0.000    0.000  base_events.py:846(_call_soon)
    queue.py:112(empty)                                   ->       2    0.000    0.000  queue.py:266(_qsize)
                                                                   2    0.000    0.000  {method '__enter__' of '_thread.lock' objects}
                                                                   2    0.000    0.000  {method '__exit__' of '_thread.lock' objects}
    <frozen importlib._bootstrap>:1409(_handle_fromlist)  ->       4    0.000    0.000  {built-in method builtins.hasattr}
                                                                   4    0.000    0.000  {built-in method builtins.isinstance}
    typing.py:1361(__hash__)                              ->      12    0.000    0.000  {built-in method builtins.hash}
    base_events.py:766(time)                              ->       4    0.000    0.000  {built-in method time.monotonic}
    base_events.py:846(_call_soon)                        ->       1    0.000    0.000  events.py:41(__init__)
                                                                   1    0.000    0.000  {method 'append' of 'collections.deque' objects}
    {built-in method builtins.issubclass}                 ->       2    0.000    0.000  <frozen abc>:121(__subclasscheck__)
    iostream.py:784(_rotate_buffers)                      ->       1    0.000    0.000  {method '__enter__' of '_thread.RLock' objects}
                                                                   1    0.000    0.000  {method '__exit__' of '_thread.RLock' objects}
    iostream.py:288(_check_mp_mode)                       ->       2    0.000    0.000  iostream.py:285(_is_master_process)
    selector_events.py:744(_process_events)               ->       1    0.000    0.000  base_events.py:1962(_add_callback)
    <frozen abc>:121(__subclasscheck__)                   ->       2    0.000    0.000  {built-in method _abc._abc_subclasscheck}
    typing.py:396(inner)                                  -> 
    zmqstream.py:563(_log_error)                          ->       1    0.000    0.000  {method 'result' of '_asyncio.Task' objects}
    {built-in method _heapq.heappop}                      ->       2    0.000    0.000  events.py:162(__lt__)
    iostream.py:285(_is_master_process)                   ->       2    0.000    0.000  {built-in method posix.getpid}
    {built-in method builtins.len}                        -> 
    typing.py:175(_type_convert)                          ->       4    0.000    0.000  {built-in method builtins.isinstance}
    {built-in method builtins.getattr}                    -> 
    events.py:41(__init__)                                ->       1    0.000    0.000  base_events.py:2075(get_debug)
                                                                   1    0.000    0.000  {built-in method _contextvars.copy_context}
    {built-in method builtins.hash}                       -> 
    {built-in method _abc._abc_subclasscheck}             -> 
    {method 'popleft' of 'collections.deque' objects}     -> 
    base_events.py:1962(_add_callback)                    ->       1    0.000    0.000  {method 'append' of 'collections.deque' objects}
    {built-in method time.monotonic}                      -> 
    {built-in method builtins.hasattr}                    -> 
    events.py:162(__lt__)                                 ->       2    0.000    0.000  {built-in method builtins.isinstance}
    queue.py:266(_qsize)                                  ->       2    0.000    0.000  {built-in method builtins.len}
    {method 'upper' of 'str' objects}                     -> 
    {built-in method posix.getpid}                        -> 
    {method '__enter__' of '_thread.lock' objects}        -> 
    {method 'append' of 'collections.deque' objects}      -> 
    {built-in method posix.getppid}                       -> 
    {method 'get' of 'dict' objects}                      -> 
    zmqstream.py:528(receiving)                           -> 
    {method '__exit__' of '_thread.lock' objects}         -> 
    {method 'result' of '_asyncio.Task' objects}          -> 
    {built-in method math.ceil}                           -> 
    base_events.py:548(_check_closed)                     -> 
    {built-in method _contextvars.copy_context}           -> 
    {built-in method _asyncio.get_running_loop}           -> 
    {method 'items' of 'dict' objects}                    -> 
    iostream.py:327(closed)                               -> 
    {method '__enter__' of '_thread.RLock' objects}       -> 
    {method 'append' of 'list' objects}                   -> 
    {method '__exit__' of '_thread.RLock' objects}        -> 
    typing.py:2300(cast)                                  -> 
    base_events.py:2075(get_debug)                        -> 
    selectors.py:435(select)                              -> 1636/809    0.006    0.003  3103966480.py:5(utility)
                                                                   3    0.000    0.000  {built-in method builtins.len}
                                                                   1    0.000    0.000  {built-in method math.ceil}
                                                                 1/0    0.000    0.000  {method 'poll' of 'select.epoll' objects}
    {method 'poll' of 'select.epoll' objects}             -> 

    <pstats.Stats at 0x7faaf4774050>

- There are further tools for analysing performance once a basic
  profiling has been conducted (See [Item 93](../Item_093/item_093.qmd)
  and [Item 98](../Item_098/item_098.qmd))
- There is also a broader community of profiling tools, e.g.
  - Line profilers
  - Sampling profilers
  - Linux’s `perf` tool
  - Memory usage profilers

## Things to Remember

- Before attempting to optimise always profile to identify bottlenecks
- Prefer the `cProfile` profiler over `profile` for less profiling
  overhead
- Use `runcall` on a `Profile` object to profile a tree of function
  calls isolated from a larger program
- Use `Stats` from the `pstats` module to select and print statistics
  generated by a profiler
