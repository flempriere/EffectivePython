# Item 114: Consider Interactive Debugging with `pdb`

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

> [!NOTE]
>
> We can’t run the debugger in the generator for this site. So rather
> than providing inline examples, we’ll provide scripts

- `print` debugging can usually get you pretty far (See [Item
  12](../../Chapter_02/Item_012/item_012.qmd))
- Writing tests for specific cases also helps you find and solve
  problems (See [Item 109](../Item_109/item_109.qmd))
- For more complex case often we want to use *interactive debugging*
  - Able to investigate the state of a running python program
  - Python comes with a pre-supplied interactive debugger
- Python programs can directly invoke the debugger (see
  [always_breakpoint.py](./Examples/always_breakpoint.py))
  - Just have to call `breakpoint`
    - Equivalent to importing `pdb` and running `set_trace`

``` python
# always_breakpoint.py
import math


def compute_rmse(observed, ideal):
    total_err_2 = 0
    count = 0
    for got, wanted in zip(observed, ideal):
        err_2 = (got - wanted) ** 2
        breakpoint()  # Start the debugger here
        total_err_2 += err_2
        count += 1

    mean_err = total_err_2 / count
    rmse = math.sqrt(mean_err)
    return rmse


result = compute_rmse([1.8, 1.7, 3.2, 6], [2, 1.5, 3, 5])
print(result)
```

- Running this program, as soon as the `breakpoint` call is reached
  `pdb` is invoked

``` shell
$ uv run always_breakpoint.py
> always_breakpoint.py(10)compute_rmse()
-> breakpoint() # Start the debugger here
(Pdb)
```

- With `pdb` you can

  1. Type names of a local variable
      - Or use `p <name>`
      - Show’s the current value
  2. Call `locals()` to see a list of all local variables
  3. Import modules
  4. Inspect global state
  5. Construct new objects
  6. Modify a running program

- Not all python functionality is supported

  - `interact` provides a python REPL
    - Maintains the program state

- Debugger has specific commands for controlling program execution and
  inspecting state

  - `help` provides the full list

- For example,

  1. **where**
      - Print current call stack
      - Can figure out where you are in a program
      - Also shows how you got there
  2. **up**
      - Move scope up the execution call stack
      - Can inspect variables in a higher scope
  3. **down**
      - Move scope down the execution call stack

- Once done inspecting state we might want to continue program execution

  - Different methods for doing so

  1. **step**
      - Run until next line of execution in the program
      - Control returns to the debugger prompt
      - If next line is a function debugger stops inside the called
        function
      - i.e. will step *into* a function
  2. **next**
      - Run until next line of execution in the current program
      - Control returns to the debugger
      - If next line of execution is a function, debugger will not stop
        until the function returns
      - i.e. will step *over* a function
  3. **return**
      - Run the program until the current function returns
      - Control then returns to the debugger
  4. **continue**
      - Continue running a program until the next breakpoint
  5. **quit**
      - Exit debugger and end the program
      - Run when the problem has been,
        - Identified,
        - You’ve gone too far through the program,
        - Or need to modify the program

- Can call `breakpoint` anywhere in a program

  - If trying to find bug that has very specific trigger conditions,
    then set a `breakpoint` in code to only fire when that condition is
    made
  - See
    [conditional_breakpoint.py](./Examples/conditional_breakpoint.py)

``` python
# conditional_breakpoint
import math


def compute_rmse(observed, ideal):
    total_err_2 = 0
    count = 0
    for got, wanted in zip(observed, ideal):
        err_2 = (got - wanted) ** 2
        if err_2 >= 1:  # Debugging condition
            breakpoint()
        total_err_2 += err_2
        count += 1

    mean_err = total_err_2 / count
    rmse = math.sqrt(mean_err)
    return rmse


result = compute_rmse([1.8, 1.7, 3.2, 6], [2, 1.5, 3, 5])
print(result)
```

- When the debugger trips we can confirm that the condition is true

``` shell
$ uv run conditional_breakpoint.py
> conditional_breakpoint.py(11)compute_rmse()
-> breakpoint()
(Pdb) wanted
5
(Pdb) got
6
(Pdb) err_2
2
```

- Alternative technique is *postmortem debugging*
  - Can debug a program *after* an exception is raised
- Help’s when unsure where to use a breakpoint
- For example, (see
  [postmortem_breakpoint.py](./Examples/postmortem_breakpoint.py))

``` python
# postmortem_breakpoint
import math


def compute_rmse(observed, ideal):
    total_err_2 = 0
    count = 0
    for got, wanted in zip(observed, ideal):
        err_2 = (got - wanted) ** 2
        total_err_2 += err_2
        count += 1

    mean_err = total_err_2 / count
    rmse = math.sqrt(mean_err)
    return rmse


result = compute_rmse(
    [1.8, 1.7, 3.2, 7j],  # Bad input
    [2, 1.5, 3, 5],
)
print(result)
```

- To run the post-mortem debugger we can run as follows

``` shell
$ uv run -m pdb -c continue postmortem_breakpoint.py
Traceback (most recent call last):
  File ".../pdb.py", line 3652, in main
    pdb._run(target)
    ~~~~~~~~^^^^^^^^
  File ".../pdb.py", line 2566, in _run
    self.run(target.code)
    ~~~~~~~~^^^^^^^^^^^^^
  File ".../bdb.py", line 913, in run
    exec(cmd, globals, locals)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 1, in <module>
  File ".../postmortem_breakpoint.py", line 18, in <module>
    result = compute_rmse(
        [1.8, 1.7, 3.2, 7j],  # Bad input
        [2, 1.5, 3, 5],
    )
  File "..../postmortem_breakpoint.py", line 14, in compute_rmse
    rmse = math.sqrt(mean_err)
TypeError: must be real number, not complex
Uncaught exception. Entering post mortem debugging
Running 'cont' or 'step' will restart the program
> postmortem_breakpoint.py(14)compute_rmse()
-> rmse = math.sqrt(mean_err)
(Pdb)
```

- `-m pdb` tells python to run the `pdb` debugger over the program
  - `-c continue` tells `pdb` to start the program immediately
- When the program encounters an error rather than crashing the `pdb`
  debugger is invoked
- Can invoke postmortem debugging in the interactive debugger
  - Call the `pm` function from the `pdb` module

``` shell
$ uv run python3.14
>>> import my_module
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
    import my_module
ModuleNotFoundError: No module named 'my_module'
>>> import pdb; pdb.pm()
> <stdin-0>(1)<module>()
(Pdb)
```

## Things to Remember

- Initiate the python interactive debugger directly within a python
  program via the `breakpoint()` function call
- `pdb` shell commands let you control program execution and inspect
  program state
- The `pdb` module can be used to debug exceptions after they happen in
  independent Python programs
  - Use `python -m pdb -c continue <program path>`
  - Or the interactive interpreter
    - Via `import pdb; pdb.pm()`
