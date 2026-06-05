# Item 91: Avoid `exec` and `eval` Unless you’re Building a Developer

Tool

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- As a dynamic program python provide many mechanisms for runtime
  execution (See [Item 3](../../Chapter_01/Item_003/item_003.qmd))
- For example,
  - `setattr/getattr/hasattr` (See [Item
    61](../../Chapter_08/Item_061/item_061.qmd))
  - Metaclasses (See [Item 64](../../Chapter_08/Item_064/item_064.qmd))
  - Descriptors (See [Item 60](../../Chapter_08/Item_060/item_060.qmd))
- Python also allows for *arbitrary code execution* from an input string
  - Works via the `exec` and `eval` built-ins
- `eval` takes a single python expression as a string and returns the
  result of it’s evaluation

``` python
x = eval("1 + 2")
print(x)
```

    3

- We can’t pass a statement to `eval`
  - Will cause an error

``` python
eval("""
if True:
    print("okay")
else:
    print("no")
""")
```

    SyntaxError: invalid syntax (<string>, line 2)
    Traceback (most recent call last):

      File ~/work/EffectivePython/EffectivePython/.venv/lib/python3.14/site-packages/IPython/core/interactiveshell.py:3747 in run_code
        exec(code_obj, self.user_global_ns, self.user_ns)

      Cell In[2], line 1
        eval("""

      File <string>:2
        if True:
        ^
    SyntaxError: invalid syntax

- `exec` can be used to dynamically evaluate longer python chunks of
  python code
  - Always returns `None`
  - To get data need to use `global` or `local` scope dictionary
    arguments

``` python
global_scope = {"my_condition": False}
local_scope = {}

exec(
    """
if my_condition:
    x = "yes"
else:
    x = "no"
""",
    global_scope,
    local_scope,
)

print(local_scope)
```

    {'x': 'no'}

- In the section above `my_condition` bubbles up to the global scope to
  be evaluated
  - The assignment to `x` is then made in the `local_scope` (See [Item
    33](../../Chapter_05/Item_033/item_033.qmd))
- Use of `exec` or `eval` is a red flag in standard application code
  - Allowing dynamic and arbitrary code execution is a serious security
    risk
  - There are better techniques even for plugin architectures (See [Item
    98](../../Chapter_11/Item_098/item_098.qmd))
- `exec` and `eval` should only be used for developer tools e.g.
  - A debugger
  - Notebook system
  - run-eval-print-loop (REPL)
  - performance benchmarking tool
  - code generation utility
  - etc…
- Otherwise use other dynamic tools and meta-programming features

## Things to Remember

- `eval` evaluates and returns the result of a string containing a
  python expression
- `exec` enables execution of a block of python code
  - Can be connected to a external variables and the surrounding
    environment
- `eval` and `exec` are sources of major security risks
  - They should be rarely used if at all
  - Only to be used for supporting developer tools
