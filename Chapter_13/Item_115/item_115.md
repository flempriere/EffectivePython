# Item 115: Use `tracemalloc` to Understand Memory Usage and Leaks


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- By default Python is a memory-managed language

- CPython uses a reference counting garbage collector

  - Once all references to an object expire, it is queued for cleanup
  - Also uses a cycle-detector to clean-up self-referential objects

- Usually you can avoid worrying about allocating or deallocating memory

  - In practice programs might run out of memory from references
    overstaying their welcome

- It can be hard to work out how or where a python program is consuming
  memory

- Can use the `gc` built-in module

  - Let’s us see all memory known to the garbage collector
  - Unfortunately this is quite blunt

``` python
import gc
import os

# Before module
found_objects = gc.get_objects()
print("Before:", len(found_objects))


class MyObject:
    def __init__(self):
        self.data = os.urandom(100)


def get_data():
    values = []
    for _ in range(100):
        obj = MyObject()
        values.append(obj)
    return values


def run():
    deep_values = []
    for _ in range(100):
        deep_values.append(get_data())
    return deep_values


waste_memory = run()
found_objects = gc.get_objects()
print("After:   ", len(found_objects))
for obj in found_objects[:3]:
    print(repr(obj)[:100])
```

    Before: 87936
    After:    98008
    <__main__.MyObject object at 0x7fd9c4d11810>
    <__main__.MyObject object at 0x7fd9c4d11860>
    <__main__.MyObject object at 0x7fd9c4d118b0>

- Lot’s of the memory above is from running the jupyter notebook
- But `gc.get_objects` doesn’t provide context about the object’s it’s
  found
  - Such as how they were created
- Typically it is better to understand *where* an object came from
  rather than *what* it is
- Python 3.4 introduces the `tracemalloc` built-in library
  - Allows you to link an object to where it was allocated

``` python
import os
import tracemalloc

# Before module
tracemalloc.start(10)  # Set stack depth
time1 = tracemalloc.take_snapshot()  # Before MyObject


class MyObject:
    def __init__(self):
        self.data = os.urandom(100)


def get_data():
    values = []
    for _ in range(100):
        obj = MyObject()
        values.append(obj)
    return values


def run():
    deep_values = []
    for _ in range(100):
        deep_values.append(get_data())
    return deep_values


waste_memory = run()
time2 = tracemalloc.take_snapshot()  # After snapshot

stats = time2.compare_to(time1, "lineno")  # Compare snapshots
for stat in stats[:3]:
    print(stat)
```

    /tmp/ipykernel_13952/1425524081.py:11: size=1299 KiB (+1299 KiB), count=10000 (+10000), average=133 B
    /tmp/ipykernel_13952/1425524081.py:17: size=785 KiB (+785 KiB), count=10000 (+10000), average=80 B
    /tmp/ipykernel_13952/1425524081.py:18: size=84.4 KiB (+84.4 KiB), count=100 (+100), average=864 B

- `size` and `count` labels help identify which objects dominate memory
  usage
  - Also links where they are allocated
- Can print the full stack trace

``` python
import tracemalloc

tracemalloc.start(10)
time1 = tracemalloc.take_snapshot()


class MyObject:
    def __init__(self):
        self.data = os.urandom(1000)


def get_data():
    values = []
    for _ in range(100):
        obj = MyObject()
        values.append(obj)
    return values


def run():
    deep_values = []
    for _ in range(100):
        deep_values.append(get_data())
    return deep_values


waste_memory = run()
time2 = tracemalloc.take_snapshot()  # After snapshot

stats = time2.compare_to(time1, "traceback")
top = stats[0]
print("Biggest offender is:")
print("\n".join(top.traceback.format()))
```

    Biggest offender is:
      File "/home/runner/work/EffectivePython/EffectivePython/.venv/lib/python3.14/site-packages/IPython/core/interactiveshell.py", line 3169
        result = self._run_cell(
      File "/home/runner/work/EffectivePython/EffectivePython/.venv/lib/python3.14/site-packages/IPython/core/interactiveshell.py", line 3224
        result = runner(coro)
      File "/home/runner/work/EffectivePython/EffectivePython/.venv/lib/python3.14/site-packages/IPython/core/async_helpers.py", line 128
        coro.send(None)
      File "/home/runner/work/EffectivePython/EffectivePython/.venv/lib/python3.14/site-packages/IPython/core/interactiveshell.py", line 3446
        has_raised = await self.run_ast_nodes(code_ast.body, cell_name,
      File "/home/runner/work/EffectivePython/EffectivePython/.venv/lib/python3.14/site-packages/IPython/core/interactiveshell.py", line 3687
        if await self.run_code(code, result, async_=asy):
      File "/home/runner/work/EffectivePython/EffectivePython/.venv/lib/python3.14/site-packages/IPython/core/interactiveshell.py", line 3747
        exec(code_obj, self.user_global_ns, self.user_ns)
      File "/tmp/ipykernel_13952/1838260187.py", line 27
        waste_memory = run()
      File "/tmp/ipykernel_13952/1838260187.py", line 23
        deep_values.append(get_data())
      File "/tmp/ipykernel_13952/1838260187.py", line 15
        obj = MyObject()
      File "/tmp/ipykernel_13952/1838260187.py", line 9
        self.data = os.urandom(1000)

- Stack trace is the best mechanism for differentiating different usages
  of the same function or class
  - Can work out which usages are causing memory issues
- For more advanced memory profiling consider community packages (See
  [Item 116](../../Chapter_14/Item_116/item_116.qmd))
  - e.g. [`Memray`](https://github.com/bloomberg/memray)

## Things to Remember

- It can be difficult to understand memory consumption in Python
- The `gc` module can be used to understand what objects exist
  - Does not provide context of how they were allocated
- `tracemalloc` built-in provides tools for understanding memory
  consumption and allocation
