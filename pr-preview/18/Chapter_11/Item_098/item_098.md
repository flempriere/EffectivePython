# Item 98: Lazy-Load Modules with Dynamic Imports to Reduce Startup Time


- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- For python programs with slow start-up times (See [Item
  97](../Item_097/item_097.qmd)) an option is to consider *dynamic
  imports*

- For example, consider an image processing tool

  - Has two features

- One adjusts brightness and contrast using user supplied parameters
  (see [adjust.py](./CLI/adjust.py))

``` python
# First module
# adjust.py
# Fast initialisation


def do_adjust(path, brightness, contrast):
    print(f"Adjusting {brightness=}, {contrast=}")


# Demonstrative use
do_adjust(path="", brightness=1.0, contrast=0.2)
```

    Adjusting brightness=1.0, contrast=0.2

- Second automatically tunes brightness and contrast (See
  [enhance.py](./CLI/enhance.py))
  - Assume requires loading a large native image processing library
  - Suppose this then initialises slowly

``` python
# Second module
# enhance.py
# Slow initialisation

# mimic slow import
import time

time.sleep(1)


def do_enhance(path, amount):
    print(f"Enhancing! {amount=}")


# demonstrative use
do_enhance("", 1)
```

    Enhancing! amount=1

- To convert these to command line utilities we can use the built-in
  `argparse` module
  - Automatically handles parsing user-supplied arguments to a
    command-line program (see [parser.py](./CLI/parser.py))

``` python
# parser.py

import argparse

PARSER = argparse.ArgumentParser()
PARSER.add_argument("file")

sub_parsers = PARSER.add_subparsers(dest="command")

enhance_parser = sub_parsers.add_parser("enhance")
enhance_parser.add_argument("--amount", type=float)

adjust_parser = sub_parsers.add_parser("enhance")
adjust_parser.add_argument("--brightness", type=float)
adjust_parser.add_argument("--contrast", type=float)
```

- `add_subparser` lets us make different modes require a different set
  of flags, e.g.
  1.  `adjust` to use the adjust tool
      - Which requires `brightness` and `contrast`
  2.  `enhance` to use the enhance tool
      - Which requires `amount`
- We can then put this all together in a main file (See
  [cli.py](./CLI/cli.py))

``` python
# cli.py

import adjust
import ehance
import parser

def main():
    args = parser.PARSER.parse_args()

    if args.command == "enhance":
        enhance.do_enhance(args.file, args.amount)
    elif args.command == "adjust":
        adjust.do_adjust(args.file, args.brightness, args.contrast)
    else:
        raise RuntimeError("Not reachable!")

if __name__ == "__main__":
    main()
```

- Running this program is slow,
  - Largely due to slow load of the `enhance.py` module

``` shell
$ time uv run cli.py dummy_file.txt enhance --amount 0.8
Enhancing! amount=0.8

real    0m1.207s
user    0m0.133s
sys     0m0.074s
```

- *But*, because python will load all modules at the start, we can see
  this slow down *still* occurs even if we only use the `adjust` command

``` shell
$ time uv run cli.py dummy_file.txt adjust --brightness 0.3 --contrast -0.1
Adjusting brightness=0.3, contrast=-0.1

real    0m1.321s
user    0m0.218s
sys     0m0.101s
```

- Unfortunately, this is the PEP 8 recommended practice (See [Item
  2](../../Chapter_01/Item_002/item_002.qmd))
- This has the downside that when running a program we’ll load *all*
  functionality, even when only using *some*
- We can measure the impact of import time on a program via the
  `-X importtime` flag if using CPython (See [Item
  1](../../Chapter_01/Item_001/item_001.qmd))
  - Cutting the output to the largest couple of modules, and our modules

``` shell
$ uv run python3.14 -X importtime cli.py
import time: self [us] | cumulative | imported package
import time:      6756 |      61837 | site
import time:       418 |        418 | adjust
import time:   1000577 |    1000577 | enhance
import time:      5637 |       7117 |   argparse
import time:      7987 |      23440 |       inspect
import time:      9100 |      41394 |   _colorize
```

- The time reported is in microseconds.
- Shows the time to execute all global statements
  - Excludes imports
- The cumulative column is the time to load a module and all it’s
  dependencies
- ideally we want to delay loading the `enhance` module until (or if) we
  need it
  - `import` statements can be scoped
  - e.g. located within functions
  - Let’s us explicitly `import` when and where it’s needed
    - At the cost of making it harder to see what all the imports
      associated with a file are (See
      [cli_faster.py](./CLI/cli_faster.py))

``` python
# cli_faster.py
# Improves the cli load time by using lazy imports

import parser


def main():
    args = parser.PARSER.parse_args()

    if args.command == "enhance":
        import enhance  # lazy import module

        enhance.do_enhance(args.file, args.amount)

    elif args.command == "adjust":
        import adjust  # lazy import module

        adjust.do_adjust(args.file, args.brightness, args.contrast)

    else:
        raise RuntimeError


if __name__ == "__main__":
    main()
```

- The `adjust` command runs very quickly, since it now only loads the
  `adjust` module

``` shell
$ time uv run ./cli_faster.py dummy_file.txt adjust --brightness .3 --contrast -0.1
Adjusting brightness=0.3, contrast=-0.1

real    0m0.567s
user    0m0.078s
sys     0m0.238s
```

- The `enhance` command remains slow

``` shell
 time uv run ./cli_faster.py dummy_file.txt enhance --amount 0.8
Enhancing! amount=0.8

real    0m1.295s
user    0m0.185s
sys     0m0.110s
```

- We can use `-X importtime` to confirm that the `adjust` and `enhance`
  modules are only loaded when their respective command is specified
- Using `adjust`

``` shell
$ uv run python3.14 -X importtime cli_faster.py dummy_file.txt adjust --brightness .3 --contrast -0.1
import time: self [us] | cumulative | imported package
import time:      2042 |      42290 | parser
import time:       784 |        784 | adjust
Adjusting brightness=0.3, contrast=-0.1
```

- Then using `enhance`

``` shell
$ uv run python3.14 -X importtime cli_faster.py dummy_file.txt enhance --amount 0.8
import time: self [us] | cumulative | imported package
import time:      2051 |      39437 | parser
import time:   1000604 |    1000604 | enhance
Enhancing! amount=0.8
```

- Lazy loading can also be used in web-applications to reduce cost of
  *cold starts*
- For example, if we hosted our image processing program on a web server
  we wouldn’t want it to load `enhance` until a user called for it

``` python
# server.py

from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/adjust", methods=["GET", "POST"])
def do_adjust():
    if request.method == "POST":
        the_file = request.files["the_file"]
        brightness = request.form["brightness"]
        contrast = request.form["contrast"]

        import adjust # Lazy import
        return adjust.do_adjust(the_file, brightness, contrast)
    else:
        return render_template("adjust.html")

@app.route("/enhance", methods=["GET", "POST"])
def do_enhance():
    if request.methods == "POST":
        the_file = request.files["the_file"]
        amount = request.form["amount"]

        import enhance # Lazy import
        return enhance.do_enhance(the_file, amount)
    else:
        return render_template("enhance.html")
```

- When a request is handled by the python process for the first time the
  module will be imported
  - Subsequent calls will access the already loaded module
- There is a cost associated with dynamic imports compared to global
  imports
  - Since we have to check if we’ve already loaded a module each time
  - But it’s not high
  - We can time it using `timeit` to check the time associated with
    dynamically importing an already imported module

``` python
import timeit

trials = 10_000_000

result = timeit.timeit(
    setup="import CLI.enhance",
    stmt="import CLI.enhance",
    globals=globals(),
    number=trials,
)

print(f"{result / trials * 1e9:2.1f} nanos per call")
```

    238.3 nanos per call

- In comparison, consider the approach below of using a lock-protected
  global variable
  - Common way to prevent multiple threads from dog-piling during
    program initialisation

``` python
import timeit
import threading

trials = 100_000_000

initialised = False
initialised_lock = threading.Lock()

result = timeit.timeit(
    stmt="""
global initialised
# Speculatively check without the lock
if not initialised:
    with initialised_lock:
        # Double check after holding the lock
        if not initialised:
            # Do expensive initialisation
            initialised = True
""",
    globals=globals(),
    number=trials,
)

print(f"{result / trials * 1e9:2.1f} nanos per call")
```

    13.7 nanos per call

- There should be an order of magnitude difference between the above and
  the dynamic import (approx. $10$ times)
- Of course the above is assuming no lock contention
  - But the speed is about equal to adding two integers in python
- However, dynamic import is simple code that doesn’t require
  boilerplate
  - The takeaway is not to *not use* dynamic imports but rather consider
    where to put them
  - Avoid putting them in hot loops

> [!TIP]
>
> **Python 3.15 and Lazy Imports**
>
> Python 3.15 is introducing syntax for lazy imports. This lets you
> achieve the fast start-up of dynamic imports but the readability of
> having all imports at the top of a file. Simply specifying an `import`
> with the `lazy` keyword like,
>
> ``` python
> lazy import enhance
> ```
>
> will defer loading the import until the first time that the module is
> actually needed.

## Things to Remember

- CPython’s `-X importtime` flag let’s you interrogate the time a python
  program spends importing modules
  - Help’s diagnose sources of slow start-up times
- Modules can be imported from within functions
  - This then loads them *dynamically*
  - Enables delaying the load of a module until it is actually needed
- Overhead of dynamic imports and checking if it has already been loaded
  is small but non-negligible
  - It is worthwhile in general but should be avoided from being called
    in hot code
- If using Python 3.15+ consider using `lazy import` instead to combine
  the benefits of both global and dynamic imports
