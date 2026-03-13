# Pythonic Thinking

- [Item 1: Know which Version of Python you’re
  Using](#item-1-know-which-version-of-python-youre-using)

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
        3.14.3 (main, Feb  3 2026, 22:52:18) [Clang 21.1.4 ]
