# Chapter 1: Pythonic Thinking

- [Item 1: Know which Version of Python you’re
  Using](#item-1-know-which-version-of-python-youre-using)
  - [Things to Remember](#things-to-remember)
- [Item 2: Follow the PEP Style
  Guide](#item-2-follow-the-pep-style-guide)
  - [Whitespace](#whitespace)
  - [Naming](#naming)
  - [Expressions and Statements](#expressions-and-statements)
  - [Imports](#imports)
  - [Automation](#automation)
  - [Things to Remember](#things-to-remember-1)
- [Item 3: Never Expect Python to Detect Errors at Compile
  Time](#item-3-never-expect-python-to-detect-errors-at-compile-time)
  - [Things to Remember](#things-to-remember-2)
- [Item 4: Write Helper Functions instead of Complex
  Expressions](#item-4-write-helper-functions-instead-of-complex-expressions)
  - [Things to Remember](#things-to-remember-3)
- [Item 5: Prefer Multiple-Assignment Unpacking over
  Indexing](#item-5-prefer-multiple-assignment-unpacking-over-indexing)
  - [Things to Remember](#things-to-remember-4)

- *Pythonic* is a loose term in the python community to describe code
  that follows community best practice style
- Python’s style isn’t enforced by a compiler
- Some basic tenants are:
  1. Explicit over implicit
  2. Simple over complex
  3. Maximise readability
- *The Zen of Python* is a document that outlines some of these
  principles
  - You can read it by calling `import this` from the interpreter

``` python
    import this
```

    The Zen of Python, by Tim Peters

    Beautiful is better than ugly.
    Explicit is better than implicit.
    Simple is better than complex.
    Complex is better than complicated.
    Flat is better than nested.
    Sparse is better than dense.
    Readability counts.
    Special cases aren't special enough to break the rules.
    Although practicality beats purity.
    Errors should never pass silently.
    Unless explicitly silenced.
    In the face of ambiguity, refuse the temptation to guess.
    There should be one-- and preferably only one --obvious way to do it.
    Although that way may not be obvious at first unless you're Dutch.
    Now is better than never.
    Although never is often better than *right* now.
    If the implementation is hard to explain, it's a bad idea.
    If the implementation is easy to explain, it may be a good idea.
    Namespaces are one honking great idea -- let's do more of those!

## Item 1: Know which Version of Python you’re Using

- Python has several different versions all in various states of
  maintenance

- Python 2 is the previous major version

  - No longer supported

- Many Operating Systems have multiple python versions installed by
  default

- However the default meaning of `python` (the command to run python) is
  ill-defined

  - Typically an alias for *python 2.7*
    - May be an older version of python 2 though
    - Or even *python 3*
  - On systems where python 2 is not installed, then the command may
    error
    - This happens on my machine

  ``` shell
    $ python --version
    Command 'python' not found, did you mean:
        command 'python3' from deb python3
        command 'python' from deb python-is-python3
  ```

- *Python 3*, the new and currently developed major version is usually
  found under the command `python3`

- On my machine

  ``` shell
    $ python3 --version
    Python 3.12.3
  ```

- Alternative run times like [PyPy](https://pypy.org/) have their own
  run commands

- I use [uv](https://docs.astral.sh/uv/) which is a python version
  manager

  - To run a uv managed python version my command is

    ``` shell
      uv run [python3.X]
    ```

- You can inspect the python version at run time using the `sys` module

  - See the example
    [check_python_version.py](./Examples/01_PythonVersion/check_python_version.py)

  ``` python
    import sys

    print(sys.platform)
    print(sys.implementation.name)
    print(sys.version_info)
    print(sys.version)
  ```

      linux
      cpython
      sys.version_info(major=3, minor=14, micro=3, releaselevel='final', serial=0)
      3.14.3 (main, Feb  4 2026, 13:50:59) [GCC 13.3.0]

- Python 3’s minor versions update relatively often

  - These add new features, deprecate or remove old ones
  - The [Release Notes](http://docs.python.org/3/whatsnew/index.html)
    are the best place to keep track of the updates

- There is also constant evolution of community packages

### Things to Remember

- Python 3 is the sole actively maintained and developed python version
- It can be unclear what python is installed on a computer
  - Use `--version` or `sys` to verify

## Item 2: Follow the PEP Style Guide

- PEP (short for Python Enhancement Proposal) 8 is the style guide for
  python code
- A common style encourages collaboration
- Let’s you use common tooling
- [PEP 8](https://www.python.org/dev/peps/pep-0008/) evolves as the
  language ecosystem does too
  - You should stay up to date with it
- Below highlights some of the main points

### Whitespace

- Python whitespace is syntactically significant
- As a result you should
  1. Use spaces instead of tabs
  2. Use four spaces for each level of syntactically significant
      indenting
  3. Lines should be $79$ characters or less
      - Docstrings and comments should be $72$ characters or less
      - Internal teams may relax the first requirement to $99$
        characters
  4. Continuation of expressions onto additional lines should be
      indented by four extra spaces
  5. In a file
      - Functions and classes should be separated by two blank lines
  6. In a class
      - Methods are separated by one line
  7. In a dictionary,
      - No whitespace between key and colon value e.g. `key:value` not
        `key :`
      - One space between colon and value if room on the same line,
        e.g. `: value` not `:value`
  8. One whitespace before and after assignment operator
      - e.g. `a = b` not `a=b`
  9. For a type annotation
      - No space between variable and colon e.g. `x:` not `x :`
      - One space before the type information e.g. `x: int` not `x:int`

### Naming

- Different parts of the language should be named differently

- Helps the reader quickly distinguish between variables, constants,
  functions and classes

  1. *Functions*, *variables* and *attributes* to use *snake_case*
      e.g. `lowercase_underscore`
  2. *Protected* attributes to have a leading underscore,
      e.g. `_protected_attribute`
  3. *Private* attributes to use a double leading underscore,
      e.g. `__private_attribute`
  4. *Classes* to use capitalised *CamelCase* e.g. `ClassName`
      - This includes exceptions
  5. *Instance methods* should name the first parameter (the object
      reference) `self`
  6. Class methods should name the first parameter (the class
      reference) `cls`

### Expressions and Statements

1. Use inline negation `if a is not b` instead of negating a positive
    `if not a is b`
2. Don’t check for empty containers (e.g. `[]` or `""`) by checking the
    length
    - Use `not`, e.g. `if not some_list`
      - Assume that empty values will evaluate to `False`
3. Assume a non-empty container (e.g. `[1]` or `"a"`) will evaluate
    `True`
    - e.g. `if some_list` should evaluate to `True`
4. Avoid single line `if`, `while` and `except` statements
    - Prefer to spread these over multiple lines for readability
5. Break a statement over multiple lines by wrapping it in parentheses
    - Add line breaks and indentation to make it readable
6. Corollary to the above:
    - Prefer using parentheses to split over multiple lines
    - Avoid using the line continuation marker `\`

### Imports

1. Put `import` statements at the top of a file
2. Use absolute names for modules
    - Don’t use relative names
    - e.g. use `from foo import bar` not `import foo` to get the package
      `bar`
3. If you *must* do relative imports, use explicit syntax
    - e.g. `from . import foo`
4. Imports should be:
    - Sectioned into the following,
      1. standard library modules
      2. third-party modules
      3. Your own modules
    - Each subsection should be sorted alphabetically

### Automation

- Because there is a common framework of style that means there can be a
  common tooling ecosystem
- Some popular ones are
  - [Flake8](https://flake8.pycqa.org/en/latest/) is a *linter* that
    assesses code style
  - [Black](https://black.readthedocs.io/en/stable/) is a *formatter*
    that automatically updates code to conform to the PEP 8 style guide
    - Black is also officially supported by the Python Software
      Foundation

      ``` shell
        $ pip install black
        $ python -m black example.py
        reformatted example.py

        All done!
        1 file reformatted
      ```

  - [isort](https://pycqa.github.io/isort/index.html) automatically
    sorts imports
  - [Ruff](https://docs.astral.sh/ruff/) combines linting, formatting
    and import sorting
    - Plus other features

    - Can replace the previous three entirely

      ``` shell
        pip install ruff
        ruff check [file] # lint a file
        ruff format [file] # format a file
      ```

  - [Pylint](https://www.pylint.org/) another linting tool

### Things to Remember

- Always follow PEP 8 when writing python code
- Sharing a common style helps you collaborate
- Community tooling helps you stick to the PEP 8 style and can be used
  to catch errors

## Item 3: Never Expect Python to Detect Errors at Compile Time

- Python doesn’t have a strict compile time

- It’s an interpreted language

- When a python program is loaded

  - Source code is parsed into abstract syntax trees

  - Checked for obvious syntax errors

    - This will raise a `SyntaxError`

    ``` python
      if True # Bad Syntax
          print("hello")
    ```

        SyntaxError: expected ':' (2631849070.py, line 1)
          Cell In[3], line 1
            if True # Bad Syntax
                    ^
        SyntaxError: expected ':'

  - Errors in literals can also be caught

    ``` python
      1.3j5 # Bad number
    ```

        SyntaxError: invalid imaginary literal (2742080217.py, line 1)
          Cell In[4], line 1
            1.3j5 # Bad number
               ^
        SyntaxError: invalid imaginary literal

- Not likely to get much than that

  - Basic tokenization errors
  - Parse errors

- Because python is dynamic, variable definitions and lifetimes are
  difficult to track

- Means that something obviously wrong like below, is not strictly
  invalid, so can’t be flagged as an error at parse time

  ``` python
    def bad_reference():
        print(local_var)
        local_var = 123
  ```

- The error will only trip once we try to execute it

  ``` python
    bad_reference()
  ```

      UnboundLocalError: cannot access local variable 'local_var' where it is not associated with a value
      ---------------------------------------------------------------------------
      UnboundLocalError                         Traceback (most recent call last)
      Cell In[6], line 1
      ----> 1 bad_reference()

      Cell In[5], line 2, in bad_reference()
            1 def bad_reference():
      ----> 2     print(local_var)
            3     local_var = 123

      UnboundLocalError: cannot access local variable 'local_var' where it is not associated with a value

- To emphasise this issue, we can see that in the function below,
  sometimes `x` is valid, sometimes not

  ``` python
    def sometimes_ok(x):
        if x:
            local_var = 123
        print(local_var)
  ```

- If we call it, with a truthful value for `x`, every work fine

  ``` python
    sometimes_ok(True)
  ```

      123

- If not,

  ``` python
    sometimes_ok(False)
  ```

      UnboundLocalError: cannot access local variable 'local_var' where it is not associated with a value
      ---------------------------------------------------------------------------
      UnboundLocalError                         Traceback (most recent call last)
      Cell In[9], line 1
      ----> 1 sometimes_ok(False)

      Cell In[7], line 4, in sometimes_ok(x)
            2 if x:
            3     local_var = 123
      ----> 4 print(local_var)

      UnboundLocalError: cannot access local variable 'local_var' where it is not associated with a value

- Python can also struggle with mathematical errors, e.g.

  ``` python
    def bad_math():
        return 1 / 0

    bad_math()
  ```

      ZeroDivisionError: division by zero
      ---------------------------------------------------------------------------
      ZeroDivisionError                         Traceback (most recent call last)
      Cell In[10], line 4
            1 def bad_math():
            2     return 1 / 0
      ----> 4 bad_math()

      Cell In[10], line 2, in bad_math()
            1 def bad_math():
      ----> 2     return 1 / 0

      ZeroDivisionError: division by zero

- Can’t immediately infer this is wrong because the `/` operator might
  have been overloaded

- Some other problems python will fail to statically detect are

  1. undefined methods
  2. too many or too few arguments to a function call
  3. mismatched return types

- Linting tools like [Flake 8](#item-2-follow-the-pep-style-guide) and
  Ruff (see above) can help catch these

  - More advanced techniques are *type checkers*
  - We’ll discuss these later

- Even with these tools its important to be aware that most python
  errors will be caught at run time

  - This is because python prioritises run time flexibility

- Therefore it’s important to,

  1. Check assumptions are correct at run time
  2. Verify program correctness with automated tests

### Things to Remember

- Python detects most errors at run time
- Community projects like linters and type checkers can help catch some
  types of errors

## Item 4: Write Helper Functions instead of Complex Expressions

- Python’s high level syntax lets you write very compact expressions

- e.g. To decode a website query string,

  ``` python
    from urllib.parse import parse_qs

    my_values = parse_qs("red=5&blue=0&green=", keep_blank_values=True)
    print(repr(my_values))
  ```

      {'red': ['5'], 'blue': ['0'], 'green': ['']}

- Query strings parameters may

  1. Have multiple values
  2. Have a single value
  3. Be present with no value
  4. Be omitted entirely

- If we try and access them using a dictionary, we get different results

  ``` python
    print("Red: {0}".format(my_values.get("red")))
    print("Green: {0}".format(my_values.get("green")))
    print("Opacity: {0}".format(my_values.get("opacity")))
  ```

      Red: ['5']
      Green: ['']
      Opacity: None

  - Might like to assign $0$ to a missing parameter or blank parameter

- We can write a complicated python expression to do this

  - Why?
    - Empty string, empty list and zero are all `False`
    - Means that in the below expressions, if the first part is `False`,
      then the rest evaluates to $0$

  ``` python
    red = my_values.get("red", [""])[0] or 0
    green = my_values.get("green", [""])[0] or 0
    opacity = my_values.get("opacity", [""])[0] or 0

    print(f"Red:        {red!r}")
    print(f"Green:      {green!r}")
    print(f"Opacity:    {opacity!r}")
  ```

      Red:        '5'
      Green:      0
      Opacity:    0

  - In the `"red"` case, red is in the dictionary and so is retrieved
    - The value is non-zero and so `True`
    - The first expression ends and `"5"` is returned
  - In the `"green"` case, green is in the dictionary
    - The empty string is retrieved
    - Evaluates to `False`
    - So we move to the second sub-expression which results in `0` being
      returned
  - In the `"opacity"` case, opacity is not in the dictionary
    - `get` returns `[""]`
    - We then access the list to get the empty string
    - This evaluates to `False`
    - We move to the second sub-expression which results in `0` being
      returned

- This logic is very hard to understand, even while knowing what is
  trying to be achieved

- Still not complete!

  - For the missing values we have the integer `0`

  - For the values that are present we have the string `"5"`

  - So we need to add an extra layer to do a conversion to integer, e.g.

    ``` python
      red = int(my_values.get("red", [""])[0] or 0)
      print(f"Red:        {red!r}")
    ```

        Red:        5

- At this the code while functional is too obscure to be easily
  understood

- Instead we could write a simple function

  ``` python
    def get_first_int(values, key, default=0):
        found = values.get(key, [""])
        if found[0]:
            return int(found[0])
        return default
  ```

- This is much easier to understand and follow

  - Also easier to modify in the future

- We can rewrite our initial parse as

  ``` python
    red = get_first_int(my_values, "red")
    green = get_first_int(my_values, "green")
    opacity = get_first_int(my_values, "opacity")

    print(f"Red:        {red!r}")
    print(f"Green:      {green!r}")
    print(f"Opacity:    {opacity!r}")
  ```

      Red:        5
      Green:      0
      Opacity:    0

- As with anything follow the rules

  - Code is read more than it is written
  - *Don’t repeat yourself*

### Things to Remember

- Python’s syntax lets you write complicated single line expressions
  - These are difficult to read
- Instead break complex expressions into easy to read helper functions

## Item 5: Prefer Multiple-Assignment Unpacking over Indexing

- `tuple` is a builtin type for immutable, ordered sequences

- Can be empty, contain a single item, or multiple, e.g.

  ``` python
    no_snack = ()
    print(no_snack)
    snack = ("chips", )
    print(snack)
    snack_calories = {"chips": 140, "popcorn": 80, "nuts":190}

    items = list(snack_calories.items())
    print(items)
  ```

      ()
      ('chips',)
      [('chips', 140), ('popcorn', 80), ('nuts', 190)]

- Like lists, they support numerical indices and slices

  ``` python
    item = ("Peanut butter", "Jelly")
    first_item = item[0] # index access
    first_half = item[:1] # slice access
    print(first_item)
    print(first_half)
  ```

      Peanut butter
      ('Peanut butter',)

- Tuples are *immutable*

  - Once created they cannot be modified

  ``` python
    pair = ("Chocolate", "Peanut Butter")
    pair[0] = "Honey"
  ```

      TypeError: 'tuple' object does not support item assignment
      ---------------------------------------------------------------------------
      TypeError                                 Traceback (most recent call last)
      Cell In[19], line 2
            1 pair = ("Chocolate", "Peanut Butter")
      ----> 2 pair[0] = "Honey"

      TypeError: 'tuple' object does not support item assignment

- Python supports an *unpacking* syntax

- Let’s us perform multiple assignments on one line

- For example, if we know a tuple is a pair, we can assign both values
  to variables

  ``` python
    item = ("Peanut Butter", "Jelly")
    first, second = item # unpacking
    print(f"{first} and {second}")
  ```

      Peanut Butter and Jelly

- Unpacking tends to be less noisy than repeated explicit index accesses

- Uses pattern matching

  - We can extend this to more complex scenarios
  - Can also extend it to list, sequence assignments and nested
    iterables

  ``` python
    favourite_snacks = {
        "salty" : ("pretzels", 100),
        "sweet" : ("cookies", 180),
        "veggie" : ("carrots", 20)
    }

    ((type1, (name1, cals1)),
    (type2, (name2, cals2)),
    (type3, (name3, cals3))) = favourite_snacks.items()

    print(f"Favourite {type1} is {name1} with {cals1} calories")
    print(f"Favourite {type2} is {name2} with {cals2} calories")
    print(f"Favourite {type3} is {name3} with {cals3} calories")
  ```

      Favourite salty is pretzels with 100 calories
      Favourite sweet is cookies with 180 calories
      Favourite veggie is carrots with 20 calories

- Can also be used to swap without a temporary variables

- Using the normal syntax

  ``` python
    def bubble_sort(a):
        for _ in range(len(a)):
            for i in range(1, len(a)):
                if a[i] < a[i - 1]:
                    temp = a[i]
                    a[i] = a[i - 1]
                    a[i - 1] = temp

    names = ["pretzels", "carrots", "arugula", "bacon"]
    bubble_sort(names)
    print(names)
  ```

      ['arugula', 'bacon', 'carrots', 'pretzels']

- We can rewrite this with unpacking syntax

  ``` python
    def bubble_sort(a):
        for _ in range(len(a)):
            for i in range(1, len(a)):
                if a[i] < a[i - 1]:
                    a[i - 1], a[i] = a[i], a[i - 1] # swap

    names = ["pretzels",  "carrots", "arugula", "bacon"]
    bubble_sort(names)
    print(names)
  ```

      ['arugula', 'bacon', 'carrots', 'pretzels']

- How does this work?

  - Right side is evaluated and stored in a temporary tuple
  - The left side is then assigned via unpacking of this temporary right
    side tuple
  - Temporary tuple then ceases to exist at the end of the process

- A common use case is in unpacking lists generated in `for` loop
  expressions, e.g.

  ``` python
    snacks = [("bacon", 350), ("donut", 240), ("muffin", 190)]
    for rank, (name, calories) in enumerate(snacks, 1):
        print(f"{rank}: {name} as {calories} calories")
  ```

      1: bacon as 350 calories
      2: donut as 240 calories
      3: muffin as 190 calories

- This is the classic example of *pythonic*

- Short, but clear to see what is happening

  - No indices, which clutter the code with noise

- Unpacking can also be used for

  1. Unpacking list construction
  2. Function arguments
  3. Keyword arguments
  4. Multiple return values
  5. Structural pattern matching
  6. etc.

- Unpacking does not work for assignment expressions

- Requires you to be careful with your data structure to ensure the
  pattern matching works

### Things to Remember

- Python provides unpacking syntax for assigning multiple values in one
  statement
- Unpacking uses generalised pattern matching
  - Can be applied to any iterable
  - including iterables of iterables
- Unpacking reduces code noise by removing indices, enhancing clarity
